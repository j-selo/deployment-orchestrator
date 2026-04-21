# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the development server
uvicorn api.main:app --reload

# Run with a specific host/port
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

No test runner or linter is configured yet. When adding tests, use `pytest` with `pytest-asyncio` for async test support. When adding a linter, use `ruff`.

## Architecture

This is a FastAPI-based deployment orchestration service using Domain-Driven Design. The flow for every deployment request:

```
POST /deploy/  →  DeployService.schedule()  →  repo.create() + orchestrator.start_workflow()
```

**`DeployService.schedule()`** runs a strict gate sequence in order:
1. `validators.validate_request` — basic input sanity (env names, service names)
2. `conflict.ensure_no_conflicts` — no concurrent deployments in the same environment
3. `policies.require_prod_approval` / `block_business_hours` — sync policy checks
4. `policies.ensure_single_prod_deploy` / `enforce_deploy_frequency` / `check_error_rate` — async policy checks requiring repo access
5. `repo.create()` then `orchestrator.start_workflow()` — persist and hand off to Temporal

**Layer responsibilities:**
- `api/` — FastAPI app and route definitions only; no business logic
- `domain/` — pure business rules with no framework dependencies; `policies.py` raises `Exception` on violations
- `services/` — coordinates domain layer with infrastructure; `DeployService` takes `repo` and `orchestrator` as constructor args (dependency injection)
- `schemas/` — Pydantic models for request/response shapes

**Infrastructure dependencies (not yet implemented):**
- `repo` — async SQLAlchemy repository over PostgreSQL (asyncpg driver)
- `orchestrator` — Temporal workflow client (`temporalio`)

## Known gaps

- `schemas/schema.py` `DeployRequest` is missing the `approved: bool` field that `policies.require_prod_approval` reads
- `api/routes/deploy.py` route handler is a stub — it doesn't instantiate `DeployService` or parse `DeployRequest`
- `services/deploy-service.py` uses a hyphen in the filename, which prevents standard Python imports; rename to `deploy_service.py`
- No `__init__.py` files exist in any package directory
- No database models or migrations are defined yet
