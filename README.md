# Task Manager API

A RESTful API built with Flask and SQLite for managing personal tasks securely.

Users can register, log in, receive a JWT access token, and manage only their own tasks.

## Features

* User registration
* User login
* Password hashing
* JWT authentication
* Create tasks
* View all tasks
* Filter tasks by status or category
* View a single task
* Update tasks
* Mark tasks as pending or completed
* Delete tasks
* User-specific task ownership

## Technologies

* Python
* Flask
* SQLite
* Flask-JWT-Extended
* Werkzeug
* python-dotenv

## Project Structure

```text
Task Manager API/
├── app.py
├── database.py
├── requests.http
├── requirements.txt
├── README.md
├── .env.example
└── .gitignore
```

## Installation

Clone the repository:

```bash
git clone <repository-url>
```

Navigate to the project directory:

```bash
cd "Task Manager API"
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment on Windows:

```bash
venv\Scripts\activate
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root:

```env
JWT_SECRET_KEY=your-secret-key
```

You can generate a secure key with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Database Setup

Create the database tables:

```bash
python database.py
```

## Run the Application

```bash
python app.py
```

The API will run at:

```text
http://127.0.0.1:5000
```

## API Endpoints

### Register

```http
POST /register
```

Example request body:

```json
{
  "username": "yossi",
  "password": "123456"
}
```

### Login

```http
POST /login
```

Example request body:

```json
{
  "username": "yossi",
  "password": "123456"
}
```

A successful login returns a JWT access token.

### Get All Tasks

```http
GET /tasks
Authorization: Bearer <access_token>
```

Optional filters:

```http
GET /tasks?status=pending
GET /tasks?category=study
GET /tasks?status=completed&category=work
```

### Get One Task

```http
GET /tasks/<task_id>
Authorization: Bearer <access_token>
```

### Create a Task

```http
POST /tasks
Authorization: Bearer <access_token>
Content-Type: application/json
```

Example request body:

```json
{
  "title": "Learn Flask",
  "description": "Build a REST API",
  "category": "study"
}
```

### Update a Task

```http
PUT /tasks/<task_id>
Authorization: Bearer <access_token>
Content-Type: application/json
```

Example request body:

```json
{
  "status": "completed"
}
```

### Delete a Task

```http
DELETE /tasks/<task_id>
Authorization: Bearer <access_token>
```

## Security

* Passwords are stored as hashes.
* JWT is required for all task routes.
* Each user can access only their own tasks.
* Secrets are stored in environment variables.
* The local database and `.env` file are excluded from Git.

## Status

The first working version of the project is complete.
