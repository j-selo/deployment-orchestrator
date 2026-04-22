# Deployment Orchestrator Service

## NOTE: CURRENTLY IN DEVELOPMENT

A FastAPI service that orchestrates containerized deployments across environments (dev, staging, prod) with policy enforcement, conflict detection, and Temporal-based workflow execution.

## Stack

- **FastAPI** — HTTP API
- **Temporal** — durable workflow execution for deployment lifecycles
- **SQLAlchemy (async) + asyncpg** — async PostgreSQL persistence
- **Pydantic v2** — request validation and settings

## Prerequisites

The following must be installed and running before starting the service:

- **PostgreSQL** — primary database
- **Temporal Server** — workflow engine, listening on `localhost:7233`
- **Kubernetes cluster** — target environment for deployments
- **Helm** — used by the worker to deploy and rollback releases
- **kubectl** — required for Kubernetes cluster interaction

## Environment variables

| Variable | Purpose | Example |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:password@localhost:5432/deployments` |
| `SLACK_BOT_TOKEN` | Slack API token for deployment notifications | `xoxb-...` |
| `SLACK_CHANNEL` | Slack channel to post notifications to | `#deployments` |

## Setup and starting the service

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Apply the database schema
psql $DATABASE_URL -f db/01_create_migrations.sql

# 3. Start the API server
uvicorn app.api.main:app --reload

# 4. Start the Temporal worker (separate terminal)
python -m worker.worker
```

PostgreSQL and Temporal Server must already be running before steps 3 and 4.

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

## Project structure

```
deployment-orchestrator/
├── app/
│   ├── api/
│   │   ├── main.py                 # FastAPI app entry point, router registration
│   │   └── routes/
│   │       └── deploy.py           # POST /deploy/ endpoint
│   ├── core/
│   │   └── db.py                   # Async database connection
│   ├── domain/
│   │   ├── conflict.py             # Concurrent deployment conflict detection
│   │   ├── policies.py             # Deployment policy enforcement
│   │   └── validators.py           # Request validation rules
│   ├── integrations/
│   │   ├── helm.py                 # Helm release management
│   │   ├── kubernetes.py           # Kubernetes cluster interaction
│   │   ├── rollback.py             # Rollback logic
│   │   └── slack.py                # Slack notifications
│   ├── orchestrator/
│   │   └── client.py               # Temporal client wrapper
│   ├── repositories/
│   │   └── deploy_repo.py          # Database access layer
│   ├── schemas/
│   │   └── schema.py               # Pydantic request/response models
│   ├── services/
│   │   └── deploy_service.py       # Deployment business logic
│   └── state/
│       └── status.py               # Deployment status tracking
├── db/
│   └── 01_create_migrations.sql    # Database schema
├── worker/
│   ├── activities/
│   │   └── deploy_activities.py    # Temporal activity definitions
│   ├── workflows/
│   │   └── deploy_workflows.py     # Temporal workflow definitions
│   └── worker.py                   # Temporal worker entry point
├── requirements.txt
└── README.md
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
