# Task Manager API

A full-stack task manager project with a Flask/SQLite backend and a React/Vite frontend.

The backend lets users register, log in, receive a JWT access token, and perform CRUD operations only on tasks that belong to their own account.

## Live Demo

* API: https://task-manager-api-yossi.onrender.com
* Swagger UI: https://task-manager-api-yossi.onrender.com/docs

> The application is deployed on Render's free tier. The first request may take some time if the service is sleeping.

## Features

* User registration and login
* Secure password hashing
* JWT authentication, logout, and token revocation
* User-owned task CRUD operations
* Task filtering by status and category
* Interactive Swagger/OpenAPI documentation
* Automated backend tests with pytest
* React frontend built with Vite
* Production backend deployment with Gunicorn and Render

## Technologies

* Python, Flask, SQLite, Flask-JWT-Extended, python-dotenv
* Flask-Swagger-UI, OpenAPI 3.0
* pytest, Gunicorn, Render
* React, Vite, ESLint
* Git and GitHub

## Project Structure

```text
task-manager-api/
|-- backend/
|   |-- app/
|   |   |-- __init__.py
|   |   |-- auth_routes.py
|   |   |-- database.py
|   |   |-- jwt_handlers.py
|   |   |-- main_routes.py
|   |   `-- task_routes.py
|   |-- tests/
|   |   |-- conftest.py
|   |   |-- test_auth.py
|   |   |-- test_jwt.py
|   |   |-- test_main.py
|   |   `-- test_tasks.py
|   |-- .env.example
|   |-- app.py
|   |-- openapi.yaml
|   |-- requests.http
|   |-- requirements.txt
|   `-- wsgi.py
|-- frontend/
|-- .gitignore
`-- README.md
```

## Backend Architecture

The backend uses the Flask application factory pattern.

The `create_app()` function:

* Creates and configures the Flask application
* Loads the JWT secret key
* Registers the authentication and task blueprints
* Registers JWT error handlers
* Initializes the SQLite database
* Serves the OpenAPI specification
* Configures Swagger UI

The backend is divided into separate modules for authentication, task management, database access, JWT handling, and general routes.

## Backend Installation

Clone the repository and enter it:

```bash
git clone https://github.com/yossichakim/task-manager-api.git
cd task-manager-api
```

Create and activate a virtual environment from the repository root:

```bash
python -m venv venv
```

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

Install backend dependencies from `backend/`:

```bash
cd backend
python -m pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the repository root:

```env
JWT_SECRET_KEY=your-secure-secret-key
```

Generate a secure secret key with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the generated value into the `.env` file.

Do not commit the `.env` file to GitHub.

An example configuration is available in `backend/.env.example`.

## Database

The backend uses SQLite. The database and its required tables are initialized automatically when the Flask application starts.

No manual database setup command is required.

The main tables are:

* `users`: `id`, `username`, `password_hash`
* `tasks`: `id`, `title`, `description`, `category`, `status`, `user_id`

Each task is connected to the user who created it.

## Run Backend Locally

Start the development server from `backend/`:

```bash
cd backend
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

The production deployment uses Gunicorn and the WSGI entry point from `backend/`:

```bash
cd backend
gunicorn wsgi:app
```

The `backend/wsgi.py` file creates the Flask application instance used by the production server.

## Frontend

Install frontend dependencies from `frontend/`:

```bash
cd frontend
npm install
```

Run the frontend development server:

```bash
npm run dev
```

Build the frontend:

```bash
npm run build
```

Lint the frontend:

```bash
npm run lint
```

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

Register:

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

Log in:

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

A successful login returns an access token.

Create a task:

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

Get all tasks:

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

Update a task:

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

Delete a task:

```http
DELETE /tasks/1
Authorization: Bearer <access_token>
```

## Backend Testing

Run the complete backend test suite from `backend/`:

```bash
cd backend
python -m pytest
```

Run the tests with verbose output:

```bash
cd backend
python -m pytest -v
```

The test suite covers registration, login, password validation, JWT handling, logout and revocation, task CRUD operations, filtering, ownership, and access isolation.

## Testing with REST Client

The `backend/requests.http` file contains example HTTP requests that can be executed with the REST Client extension in Visual Studio Code.

Update the access token in the file after logging in.

## Deployment

The API is deployed on Render.

Render configuration:

```text
Root Directory:
backend
```

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

The backend project is complete and includes RESTful API design, user authentication, JWT authorization, task CRUD operations, user-specific data ownership, automated testing, OpenAPI documentation, Swagger UI, and public deployment.

## Author

Yossi Hakim

Computer Science graduate focused on backend development and software engineering.
