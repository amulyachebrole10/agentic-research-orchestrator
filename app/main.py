from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from app.graph import ResearchWorkflow
from app.local_rag import LocalRAG

app = FastAPI(title="Agentic Research Orchestrator", version="0.2.0")
workflow = ResearchWorkflow()
rag = LocalRAG()

class ResearchRequest(BaseModel):
    question: str = Field(min_length=5, max_length=2000)
    max_sources: int = Field(default=3, ge=1, le=10)

class DocumentRequest(BaseModel):
    text: str = Field(min_length=20, max_length=100000)
    source: str = Field(default="manual-input", max_length=200)

class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    top_k: int = Field(default=4, ge=1, le=10)

@app.get("/health")
def health():
    return {"status": "ok", "mode": "local-first", "vector_store": "FAISS"}

@app.post("/research")
def research(request: ResearchRequest):
    try:
        result = workflow.run(request.question, request.max_sources)
        return {"question": result["question"], "plan": result.get("plan", []),
                "sources": [s.__dict__ for s in result.get("sources", [])],
                "review": result.get("review", ""), "report": result.get("report", ""),
                "provider_mode": "demo"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Research workflow failed") from exc

@app.post("/documents/text")
def add_document(request: DocumentRequest):
    try:
        count = rag.add_text(request.text, request.source)
        return {"status": "indexed", "source": request.source, "chunks_added": count}
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Document indexing failed") from exc

@app.post("/ask")
def ask(request: AskRequest):
    try:
        return rag.answer(request.question, request.top_k)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Local RAG failed. Check Ollama and model availability.") from exc
