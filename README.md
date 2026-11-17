# IncidentOps-AI

AI-powered incident response platform. Watches alerts (Prometheus / Grafana / Datadog webhooks), investigates with a LangGraph multi-agent pipeline, proposes remediations, and requires human approval before execution.

## Features

- Alert ingestion: webhook + polling watchers (metric, log, health)
- AI investigation: triage -> diagnosis -> remediation proposal -> verifier
- Approval workflow: every destructive action is gated
- Remediation: Docker / Kubernetes / cloud actions with safety policies
- Audit log: every decision and action recorded
- Runbooks: searchable knowledge base used by the AI
- Floating assistant: chat widget on every page; full-page at /assistant/
- Simulator: demo failures (cpu_spike, crash, memory_leak)

## Stack

- Python 3.12 + Django 5.2 + DRF
- LangChain / LangGraph + OpenAI (gpt-4o-mini)
- PostgreSQL 18 + Redis + Celery
- Vanilla HTML/CSS/JS frontend (no build step)
- uv for dependency management

## Prerequisites

- Python 3.12
- uv (pip install uv, or winget install astral-sh.uv)
- PostgreSQL 15+
- Redis (optional, for Celery)

## Quick start

```bash
uv sync
cp .env.example .env      # then edit SECRET_KEY, DB_PASSWORD, OPENAI_API_KEY
createdb incidentops
uv run python manage.py migrate
uv run python scripts/seed_runbooks.py
uv run python manage.py createsuperuser
uv run python manage.py runserver 8000
```

Open http://localhost:8000 and log in. Click the chat button bottom-right to talk to the assistant.

## Tests

```bash
uv run pytest -q
```

## Layout

```
apps/           Django apps
ai_engine/      LangGraph agents, nodes, tools, prompts
integrations/   docker, kubernetes, prometheus, grafana, cloudwatch
simulator/      demo failure scenarios
tasks/          Celery tasks
frontend/       HTML/CSS/JS (served via STATICFILES_DIRS)
config/         Django settings, urls, celery
tests/          unit, integration, security, ai_engine
infra/          docker, nginx, prometheus, grafana configs
docs/           architecture, api, ai_workflow, deployment
```

## Docs

- docs/architecture.md
- docs/ai_workflow.md
- docs/api.md
- docs/deployment.md
