# Agentic Research Orchestrator — Local Edition

A local-first research and document-question-answering foundation using LangGraph, FastAPI, Ollama, Sentence Transformers and FAISS. Designed for Windows 10/11 with Docker Desktop + WSL2 and an 8 GB RAM development machine.

## Architecture

- LangGraph: planning → research → review → synthesis workflow.
- Ollama + Qwen 2.5 1.5B: local answer generation (no LLM API key).
- Sentence Transformers (all-MiniLM-L6-v2): local CPU embeddings.
- FAISS: local vector index persisted under data/index.
- FastAPI: REST endpoints.
- Docker Compose: runs the API; Ollama runs natively on Windows to avoid duplicating model memory inside Docker.

## Windows setup

1. Install Docker Desktop and enable the WSL2 backend.
2. Install Ollama for Windows from https://ollama.com/download.
3. In PowerShell, download the small model:

~~~powershell
ollama pull qwen2.5:1.5b
ollama serve
~~~

4. Copy .env.example to .env.
5. Start the API:

~~~powershell
docker compose up --build
~~~

Open http://localhost:8000/docs.

## API

Add text to the local vector store:

~~~powershell
Invoke-RestMethod -Method Post http://localhost:8000/documents/text -ContentType "application/json" -Body '{"text":"FAISS is a library for efficient similarity search.","source":"notes.txt"}'
~~~

Ask a question over indexed documents:

~~~powershell
Invoke-RestMethod -Method Post http://localhost:8000/ask -ContentType "application/json" -Body '{"question":"What is FAISS?"}'
~~~

/research currently remains an explicitly labelled offline demo workflow. It does not claim to search the live web. Public-source adapters and PDF upload are planned next.

## Run without Docker

~~~powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
~~~

Set OLLAMA_BASE_URL=http://localhost:11434 in .env for a native Python run.

## Resource guidance

Use Qwen 2.5 1.5B, a short context window and CPU embeddings. The first embedding-model run downloads model weights. Keep other model-heavy applications closed. Ollama runs on Windows while the API container connects through host.docker.internal.

## Tests

~~~powershell
pytest
~~~

## Security and limitations

This is a local development portfolio project, not a production research service. Add authentication, upload validation, persistence controls, observability, source freshness checks, citation evaluation and human review before deployment. Never commit .env, private documents or model weights.
