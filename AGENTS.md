# Task Manager Project Instructions

## Project Overview

This repository contains a full-stack task management application.

The project is organized as a monorepo:

* `backend/` contains a Flask REST API.
* `frontend/` contains a React application built with Vite.

The backend is considered complete and stable.

## Primary Goal

Use AI tools to improve the frontend, documentation, project presentation, and development workflow without introducing regressions into the existing backend.

## Critical Backend Safety Rule

Do not modify files inside `backend/` unless the user explicitly requests a backend change.

This includes, but is not limited to:

* `backend/app/`
* `backend/tests/`
* `backend/app.py`
* `backend/wsgi.py`
* `backend/openapi.yaml`
* `backend/requirements.txt`
* `backend/requests.http`
* `backend/.env.example`

Reading and analyzing backend files is allowed.

Editing backend files is not allowed unless the user gives explicit permission for the specific change.

## Allowed Areas

Unless instructed otherwise, changes should be limited to:

* `frontend/`
* `README.md`
* `AGENTS.md`
* AI skill and instruction files
* Documentation files
* Repository configuration files that do not alter backend runtime behavior

## Change Strategy

Before changing files:

1. Inspect the relevant files.
2. Explain the intended change.
3. Identify every file that will be modified.
4. Prefer the smallest possible change.
5. Avoid unrelated refactoring.
6. Preserve existing behavior.

Do not rewrite working files unnecessarily.

Do not replace complete files when a small targeted edit is sufficient.

## Frontend Guidelines

When working inside `frontend/`:

* Keep the existing React and Vite structure.
* Reuse existing components and styles when practical.
* Do not change API endpoint paths without verifying them against the backend.
* Do not duplicate backend business logic in the frontend.
* Keep authentication tokens and API communication consistent with the existing implementation.
* Do not hard-code secrets.
* Preserve environment-variable-based API configuration.
* Keep the interface simple, responsive, and accessible.
* Avoid adding dependencies unless they provide clear value.

## Backend API Contract

The frontend should use the existing API contract.

Main endpoints include:

* `POST /register`
* `POST /login`
* `DELETE /logout`
* `GET /tasks`
* `POST /tasks`
* `GET /tasks/{task_id}`
* `PUT /tasks/{task_id}`
* `DELETE /tasks/{task_id}`

Protected endpoints require:

```http
Authorization: Bearer <access_token>
```

Do not invent new endpoints.

Do not change endpoint names, request fields, response assumptions, or authentication behavior without explicit approval.

## Validation

After frontend changes, run:

```bash
cd frontend
npm run lint
npm run build
```

After an explicitly approved backend change, run:

```bash
cd backend
python -m pytest
```

Do not claim that validation passed unless the commands were actually executed successfully.

If validation cannot be run, state that clearly.

## Git Safety

Before making changes, inspect:

```bash
git status
git diff
```

After making changes, inspect:

```bash
git diff
git status
```

Never:

* Delete user work without explicit approval.
* Discard unrelated changes.
* Run destructive Git commands.
* Use `git reset --hard`.
* Force-push.
* Commit secrets or `.env` files.
* Modify previous commits unless explicitly requested.

Do not create a commit or push changes unless the user explicitly requests it.

## Documentation Rules

Documentation and code comments must be written in English.

Documentation must describe the project as it actually exists.

Do not claim that a feature, test, deployment, or integration exists unless it has been verified.

Keep setup commands compatible with the repository structure.

## Communication Style

When presenting work:

1. Summarize what was inspected.
2. Explain what changed.
3. List modified files.
4. Report validation commands and results.
5. Mention remaining risks or unverified assumptions.

Prefer clear explanations suitable for a developer learning the workflow.

## Completion Criteria

A task is complete only when:

* The requested change is implemented.
* No unauthorized backend files were modified.
* Relevant validation commands were run when possible.
* The final diff contains no unrelated changes.
* The result is clearly explained.
