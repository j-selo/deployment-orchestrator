# Deployment Orchestrator Service

## NOTE: CURRENTLY IN DEVELOPMENT

A FastAPI service that orchestrates containerized deployments across environments (dev, staging, prod) with policy enforcement, conflict detection, and Temporal-based workflow execution.

## Stack

- **FastAPI** — HTTP API
- **Temporal** — durable workflow execution for deployment lifecycles
- **SQLAlchemy (async) + asyncpg** — async PostgreSQL persistence
- **Pydantic v2** — request validation and settings

## Setup

```bash
pip install -r requirements.txt
uvicorn api.main:app --reload
```

Requires a running PostgreSQL database and a Temporal server. Configure connection details via environment variables (pydantic-settings).

## API

### `POST /deploy/`

Trigger a deployment. Runs validation, conflict checks, and policy enforcement before creating a deployment record and starting a Temporal workflow.

**Request body:**
```json
{
  "service": "my-service",
  "image": "my-service:v1.2.3",
  "env": "prod",
  "time": "2024-01-01T10:00:00Z",
  "approved": true
}
```

## Deployment policies

| Policy | Rule |
|--------|------|
| Prod approval | `approved: true` required for prod |
| Business hours | Prod deploys only allowed 09:00–17:00 local time |
| Single prod deploy | Only one active prod deployment at a time |
| Deploy frequency | No more than one deploy per service per 10 minutes |
| Error rate gate | Blocked if service error rate exceeds 5% |
| Conflict detection | No concurrent deployments in the same environment |
