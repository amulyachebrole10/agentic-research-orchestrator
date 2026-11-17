from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from app.graph import ResearchWorkflow

app=FastAPI(title="Agentic Research Orchestrator",version="0.1.0")
workflow=ResearchWorkflow()

class ResearchRequest(BaseModel):
    question: str=Field(min_length=5,max_length=2000)
    max_sources: int=Field(default=3,ge=1,le=10)

@app.get("/health")
def health(): return {"status":"ok"}

@app.post("/research")
def research(request: ResearchRequest):
    try:
        result=workflow.run(request.question,request.max_sources)
        return {"question":result["question"],"plan":result.get("plan",[]),"sources":[s.__dict__ for s in result.get("sources",[])],"review":result.get("review",""),"report":result.get("report",""),"provider_mode":"demo"}
    except Exception as exc:
        raise HTTPException(status_code=500,detail="Research workflow failed") from exc
