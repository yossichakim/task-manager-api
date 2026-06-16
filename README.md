# Task Manager API

A RESTful backend API built with Flask and SQLite for secure personal task management.

Users can register, log in, receive a JWT access token, and perform CRUD operations only on tasks that belong to their own account.

## Live Demo

* API: https://task-manager-api-yossi.onrender.com
* Swagger UI: https://task-manager-api-yossi.onrender.com/docs

> The application is deployed on Render's free tier. The first request may take some time if the service is sleeping.

## Features

* User registration
* User login
* Secure password hashing
* JWT authentication
* JWT logout and token revocation
* Create personal tasks
* Retrieve all personal tasks
* Filter tasks by status
* Filter tasks by category
* Retrieve a task by ID
* Update task details
* Mark tasks as pending or completed
* Delete tasks
* User-specific task ownership
* Interactive Swagger/OpenAPI documentation
* Automated tests with pytest
* Production deployment with Gunicorn and Render

## Technologies

* Python
* Flask
* SQLite
* Flask-JWT-Extended
* Werkzeug
* python-dotenv
* Flask-Swagger-UI
* OpenAPI 3.0
* pytest
* Gunicorn
* Render
* Git and GitHub

## Project Structure

```text
task-manager-api/
├── app/
│   ├── __init__.py
│   ├── auth_routes.py
│   ├── database.py
│   ├── jwt_handlers.py
│   ├── main_routes.py
│   └── task_routes.py
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_jwt.py
│   ├── test_main.py
│   └── test_tasks.py
├── .env.example
├── .gitignore
├── app.py
├── openapi.yaml
├── README.md
├── requests.http
├── requirements.txt
└── wsgi.py
```

## Architecture

The project uses the Flask application factory pattern.

The `create_app()` function:

* Creates and configures the Flask application
* Loads the JWT secret key
* Registers the authentication and task blueprints
* Registers JWT error handlers
* Initializes the SQLite database
* Serves the OpenAPI specification
* Configures Swagger UI

The application is divided into separate modules for authentication, task management, database access, JWT handling, and general routes.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yossichakim/task-manager-api.git
```

### 2. Navigate to the project directory

```bash
cd task-manager-api
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

Windows Command Prompt:

```bash
venv\Scripts\activate
```

Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
source venv/bin/activate
```

### 5. Install dependencies

```bash
python -m pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root:

```env
JWT_SECRET_KEY=your-secure-secret-key
```

Generate a secure secret key with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the generated value into the `.env` file.

Do not commit the `.env` file to GitHub.

An example configuration is available in `.env.example`.

## Database

The project uses SQLite.

The database and its required tables are initialized automatically when the Flask application starts.

No manual database setup command is required.

The main tables are:

### Users

* `id`
* `username`
* `password_hash`

### Tasks

* `id`
* `title`
* `description`
* `category`
* `status`
* `user_id`

Each task is connected to the user who created it.

## Run Locally

Start the development server:

```bash
python app.py
```

The API will be available at:

```text
http://127.0.0.1:5000
```

Swagger UI will be available at:

```text
http://127.0.0.1:5000/docs
```

## Production Entry Point

The production deployment uses Gunicorn and the WSGI entry point:

```bash
gunicorn wsgi:app
```

The `wsgi.py` file creates the Flask application instance used by the production server.

## API Documentation

The API is documented using OpenAPI 3.0 and Swagger UI.

Local documentation:

```text
http://127.0.0.1:5000/docs
```

Production documentation:

```text
https://task-manager-api-yossi.onrender.com/docs
```

The OpenAPI specification is available at:

```text
/openapi.yaml
```

## Authentication

Protected endpoints require a JWT access token.

After logging in, include the token in the request header:

```http
Authorization: Bearer <access_token>
```

In Swagger UI:

1. Register a user with `POST /register`
2. Log in with `POST /login`
3. Copy the returned access token
4. Click `Authorize`
5. Paste the token
6. Execute protected task endpoints

Swagger automatically adds the `Bearer` prefix.

## API Endpoints

| Method | Endpoint           | Authentication | Description                             |
| ------ | ------------------ | -------------: | --------------------------------------- |
| GET    | `/`                |             No | Check API status                        |
| GET    | `/about`           |             No | Get project information                 |
| POST   | `/register`        |             No | Register a user                         |
| POST   | `/login`           |             No | Log in and receive a JWT                |
| DELETE | `/logout`          |            Yes | Revoke the current JWT                  |
| GET    | `/tasks`           |            Yes | Retrieve the authenticated user's tasks |
| POST   | `/tasks`           |            Yes | Create a task                           |
| GET    | `/tasks/{task_id}` |            Yes | Retrieve one task                       |
| PUT    | `/tasks/{task_id}` |            Yes | Update a task                           |
| DELETE | `/tasks/{task_id}` |            Yes | Delete a task                           |

## Request Examples

### Register

```http
POST /register
Content-Type: application/json
```

```json
{
  "username": "yossi",
  "password": "secure123"
}
```

### Login

```http
POST /login
Content-Type: application/json
```

```json
{
  "username": "yossi",
  "password": "secure123"
}
```

A successful login returns an access token:

```json
{
  "access_token": "<jwt_access_token>",
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "yossi"
  }
}
```

### Create a Task

```http
POST /tasks
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "title": "Finish API documentation",
  "description": "Complete and review the project README",
  "category": "work"
}
```

New tasks receive the default status:

```text
pending
```

### Get All Tasks

```http
GET /tasks
Authorization: Bearer <access_token>
```

Optional filters:

```http
GET /tasks?status=pending
GET /tasks?category=work
GET /tasks?status=completed&category=study
```

### Update a Task

```http
PUT /tasks/1
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "status": "completed"
}
```

Fields that are not included in the request keep their existing values.

### Delete a Task

```http
DELETE /tasks/1
Authorization: Bearer <access_token>
```

## Testing

Run the complete test suite:

```bash
python -m pytest
```

Run the tests with verbose output:

```bash
python -m pytest -v
```

The test suite covers:

* User registration
* User login
* Password validation
* JWT authentication
* JWT error handling
* JWT logout and revocation
* Task creation
* Task retrieval
* Task filtering
* Task updates
* Task deletion
* User ownership and access isolation

## Testing with REST Client

The `requests.http` file contains example HTTP requests that can be executed with the REST Client extension in Visual Studio Code.

Update the access token in the file after logging in.

## Deployment

The API is deployed on Render.

Render configuration:

```text
Build Command:
pip install -r requirements.txt
```

```text
Start Command:
gunicorn wsgi:app
```

The production environment must include:

```text
JWT_SECRET_KEY
```

The Render service is connected to the GitHub repository, allowing new pushes to the `main` branch to trigger automatic deployments.

## SQLite Deployment Limitation

This project currently uses SQLite.

On Render's free tier, the local filesystem is ephemeral. This means that registered users and tasks may be deleted after a restart, redeployment, or infrastructure replacement.

The deployed application should therefore be treated as a live demonstration rather than permanent data storage.

A production-ready future version should use a persistent database such as PostgreSQL.

## Security

* Passwords are stored as secure hashes rather than plain text
* JWT authentication protects task routes
* Each user can access only their own tasks
* JWT tokens can be revoked during logout
* Secret keys are loaded from environment variables
* The `.env` file is excluded from Git
* The local SQLite database is excluded from Git
* Protected routes verify the authenticated user's identity

## Future Improvements

* Replace SQLite with PostgreSQL
* Add database migrations
* Add token refresh support
* Add pagination
* Add task deadlines
* Add task priorities
* Add sorting options
* Add continuous integration with GitHub Actions
* Add Docker support
* Add rate limiting
* Add structured production logging

## Project Status

The core backend project is complete and includes:

* RESTful API design
* User authentication
* JWT authorization
* Task CRUD operations
* User-specific data ownership
* Automated testing
* OpenAPI documentation
* Swagger UI
* Public deployment

## Author

Yossi Hakim

Computer Science graduate focused on backend development and software engineering.
