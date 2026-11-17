# Agentic Research Orchestrator

A modular research workflow built with **LangGraph** and **FastAPI**. It separates planning, evidence retrieval, evidence review, and report synthesis while retaining source metadata.

## Workflow
Question → Planner → Research provider → Evidence review → Synthesis → Report

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs.

```bash
curl -X POST http://127.0.0.1:8000/research -H 'Content-Type: application/json' -d '{"question":"How should teams evaluate RAG systems?","max_sources":3}'
```

## Docker
```bash
docker build -t research-orchestrator .
docker run -p 8000:8000 research-orchestrator
```

## Tests
```bash
pytest
```

## Structure
- `app/graph.py`: LangGraph state machine.
- `app/providers.py`: provider protocol and offline demo provider.
- `app/main.py`: REST API.
- `tests/`: API tests.

## Live integrations
Implement `ResearchProvider` with a search API and LLM. Preserve title, URL, and excerpt for every source; cite only retrieved evidence. Store credentials in environment variables or a secrets manager.

## Scope and limitations
The included provider returns illustrative demo sources. This is an executable integration foundation, not live web research or autonomous fact verification. Add real providers, authentication, persistence, observability, rate limits, and human approval before production use.
