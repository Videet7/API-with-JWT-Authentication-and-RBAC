# FastAPI JWT Authentication with Role-Based Access Control (RBAC)

Features
- User Registration: Register with username, password, and role.
- User Login: Obtain a JWT token after successful authentication.
- JWT-based Authorization: Secure endpoints with JWT tokens.
- Role-Based Access Control:
 - Admin role: Full CRUD access to projects.
 - User role: Read-only access to project data.
- MongoDB integration using pymongo for storing users and project information.
- Project Management: Create, update, delete, and view projects.
- Password Hashing: Passwords are hashed using bcrypt for security

Prerequisites

To run this project, ensure you have the following installed:
- Python 3.7+
- MongoDB
- pip (Python package installer)

Installation

Clone the repository:
-  git clone <repository-url>
-  cd <repository-directory>
 
Create a virtual environment:
-  python -m venv env

Install the required dependencies:
-  pip install -r requirements.txt

Set up MongoDB:
-  Ensure MongoDB is running on localhost:27017.
- You may update the MongoDB connection URL if necessary in the script

To run the FastAPI application locally, use the following command:
- uvicorn main:app --reload

API Endpoints
1. User Registration
 - Endpoint: /register
 - Method: POST
 - Request Body: { "username": "exampleuser", "password": "password123", "role": "admin" }
2. User Login
 - Endpoint: /login
 - Method: POST
 - Request Body: { "username": "exampleuser", "password": "password123" }
 - Response: { "access_token": "JWT_TOKEN" }
3. Get All Projects
 - Endpoint: /projects
 - Method: GET
 - Requires JWT token
4. Create Project (Admin Only)
 - Endpoint: /projects
 - Method: POST
 - Request Body: { "name": "Project A", "description": "Description of project" }
 - Requires JWT token with admin role.
5. Update Project (Admin Only)
 - Endpoint: /projects/{project_id}
 - Method: PUT
 - Admin role required
6. Delete Project (Admin Only)
 - Endpoint: /projects/{project_id}
 - Method: DELETE
 - Admin role required

Deployment
To deploy this FastAPI application on AWS Lambda, use Zappa.
Using Zappa:
1. Install Zappa:
- pip install zappa
2. Initialize Zappa:
- zappa init
3. Deploy:
- zappa deploy dev
