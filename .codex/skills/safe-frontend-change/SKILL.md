---
name: safe-frontend-change
description: Safely implement minimal frontend-only changes in this Task Manager repository. Use when Codex is asked to modify files under frontend/ while preserving the backend, following repository instructions, inspecting Git state, validating the React/Vite application, and reporting all changes.
---

# Safe Frontend Change

Follow this workflow for every change.

## Enforce scope

1. Locate the repository root and read its `AGENTS.md` completely before acting.
2. Treat `frontend/` as the only writable project area.
3. Never create, edit, move, or delete files outside `frontend/`.
4. Never modify anything in `backend/`.
5. Read files outside `frontend/` only when needed to verify existing behavior or the API contract.
6. If the requested change requires a write outside `frontend/`, stop and request explicit direction instead of expanding scope.

## Inspect before editing

1. Run `git status --short`.
2. Run `git diff --`.
3. Identify existing user changes and preserve them.
4. Inspect the relevant frontend files and any read-only contract sources required for accuracy.
5. Before editing, explain the intended targeted change and list every file expected to be modified.

## Make the change

1. Implement the smallest targeted change that satisfies the request.
2. Reuse the existing React, Vite, component, styling, API, authentication, and environment-variable patterns.
3. Avoid unrelated refactoring, dependency additions, generated files, and full-file rewrites.
4. Do not alter API endpoint paths, request fields, response assumptions, or authentication behavior without explicit approval and contract verification.
5. Do not hard-code secrets.

## Validate and review

1. From `frontend/`, run `npm run lint`.
2. From `frontend/`, run `npm run build`.
3. Do not claim either validation passed unless its command completed successfully.
4. If validation cannot run or fails, report the exact command and result.
5. Run `git diff --` after validation and review the final patch for scope and unrelated changes.
6. Run `git status --short` after validation.
7. Verify that no file outside `frontend/` was modified by this workflow.

## Report

Report:

- What was inspected.
- What changed.
- Every modified file.
- The result of `npm run lint`.
- The result of `npm run build`.
- Any remaining risk, failed validation, or unverified assumption.
- Confirmation that no backend files were modified.

Never commit, amend, push, force-push, or otherwise publish changes without explicit user permission.
