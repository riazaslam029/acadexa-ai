# Contributing Guide

## Development workflow
1. Create a feature branch.
2. Keep changes aligned with existing architecture (API -> Service -> CRUD).
3. Add or update tests for changed behavior.
4. Run checks before opening PR.

## Backend checks
- python -m pytest -q
- python -m compileall app

## Frontend checks
- npm run typecheck
- npm run lint
- npm run test
- npm run build

## Coding standards
- Prefer small reusable services and avoid duplicated logic.
- Validate user input at schema layer.
- Handle exceptions with clear HTTP status messages.
- Keep route handlers thin and push logic into services.
