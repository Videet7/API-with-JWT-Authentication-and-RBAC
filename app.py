from fastapi import FastAPI, Header
from pydantic import BaseModel
import pymongo, jwt, bcrypt, datetime, uvicorn, random

app = FastAPI()
client = pymongo.MongoClient("localhost", 27017)
SECRET_KEY = 'api_token_key' #os.environ['SECRET_KEY'] 

try:
    db = client.api_config
except Exception as err:
    print("Error due to %s", str(err))

#################################Pydantic Model#######################

class User(BaseModel):
    username : str 
    password : str
    role : str 

class LoginDetails(BaseModel):
    username: str
    password: str

class Project(BaseModel):
    name : str
    description: str

class UpdateProject(BaseModel):
    name : str | None = None
    description: str | None = None

#################################API##################################

@app.get("/")
def home():
    return "Welcome to FastAPI"


@app.post("/register")
async def register(request:User):
    try:
        request = request.dict()
        pipeline = [
            {
                "$match":
                {
                    "username": request['username']
                }
            }
            ]
        
        user_obj = db.user.aggregate(pipeline=pipeline)

        if list(user_obj):
            return {"Status Code" : 200,
                "message" : f'{request["username"]} already exist, Please try with another username'}

        hashed_pw = bcrypt.hashpw(request['password'].encode('utf-8'), bcrypt.gensalt())

        insert_dict = {
            "username": request['username'],
            "password": request['password'] if not hashed_pw else hashed_pw,
            "role": request['role'],
        }

        db.User.insert_one(insert_dict)

        return {"Status Code" : 200,
                "message" : f'{request["username"]} user created successfully'}

    except Exception as err:
        return {"Status Code" : 401,
                "message" : f'{request["username"]} creation failed due to {str(err)}'}

@app.post("/login")
async def login(request:LoginDetails):
    try:
        request = request.dict()
        pipeline = [
            {
                "$match":
                {
                    "username": request['username']
                }
            }
            ]

        user_obj = db.User.aggregate(pipeline=pipeline)
        user = list(user_obj)
        hash_pw = user[0]['password']

        if user and bcrypt.checkpw(request['password'].encode('utf-8'), hash_pw):
            token = jwt.encode({
                'username': request['username'],
                'role': user[0]['role'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
            }, SECRET_KEY, algorithm='HS256')
            return {"access_token": token}
        else:
            return {"Status Code" : 401, 'error': 'Invalid email or password'} 
            
    except Exception as err:
        return {"Status Code" : 401,
                "message" : f'{request["username"]} login failed due to {str(err)}'}
    
@app.get("/projects")
async def projects(token: str = Header(None)):
    try:
        try:    
            payload = jwt.decode(token, SECRET_KEY, algorithms='HS256')
        except:
            return {"Status Code" : 401,
                "message" : f'Invalid Token'}

        if payload:
            project_obj = db.Project
            projects = list(project_obj.find({},{"_id": 0}))

            return {
                "Status Code" : 200,
                "Projects" : [project for project in projects]
            }

    except Exception as err:
        return {"Status Code" : 401,
                "message" : f'Failed due to {str(err)}'}

@app.post("/projects")
async def projects(project:Project, token: str = Header(None)):
     try:
        project = project.dict()

        try:    
            payload = jwt.decode(token, SECRET_KEY, algorithms='HS256')
        except:
            return {"Status Code" : 401,
                "message" : f'Invalid Token'}
        
        if payload and payload['role'] == 'admin':

            project_id = random.randint(1,99999)

            insert_dict = {
                "name": project['name'],
                "description": project['description'],
                "project_id":project_id,
            }

            db.Project.insert_one(insert_dict)

            return {"Status Code" : 200,
                    "message" : f'{project["name"]} project created successfully',
                    "project_id":  project_id}
        
        return {
            "Status Code" : 200,
            "message" : f'Admin Role Required to create a Project'
        }

     except Exception as err:
        return {"Status Code" : 401,
                "message" : f'Failed due to {str(err)}'}
     
@app.delete("/projects/{project_id}")
async def delete_projects(project_id, token: str = Header(None)):
    try:
        try:    
            payload = jwt.decode(token, SECRET_KEY, algorithms='HS256')
        except:
            return {"Status Code" : 401,
                "message" : f'Invalid Token'}
        
        if payload and payload['role'] == 'admin':
            db.Project.delete_one({"project_id":int(project_id)})

            return {"Status Code" : 200,
                "message" : f'Project deleted successfully',}

        return {
            "Status Code" : 200,
            "message" : f'Admin Role Required to delete a Project'
        }
    
    except Exception as err:
        return {"Status Code" : 401,
                "message" : f'Failed due to {str(err)}'}

@app.put("/projects/{project_id}")
async def delete_projects(project:UpdateProject, project_id, token: str = Header(None)):
    try:
        project = project.dict()
        try:    
            payload = jwt.decode(token, SECRET_KEY, algorithms='HS256')
        except:
            return {"Status Code" : 401,
                "message" : f'Invalid Token'}
        
        if payload and payload['role'] == 'admin':
            project_obj = {}
            for k,v in project.items():
                if v:
                    project_obj[k] = v

            db.Project.update_one({"project_id":int(project_id)}, {"$set": project_obj})

            return {"Status Code" : 200,
                "message" : f'Project Updated successfully'}
        
        return {
            "Status Code" : 200,
            "message" : f'Admin Role Required to update a Project'
        }

    except Exception as err:
        return {"Status Code" : 401,
                "message" : f'Failed due to {str(err)}'}

###################################Start Server#############################################
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)