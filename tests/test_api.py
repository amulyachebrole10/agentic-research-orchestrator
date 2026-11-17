from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)

def test_health():
    assert client.get("/health").json()=={"status":"ok"}

def test_research_pipeline():
    r=client.post("/research",json={"question":"How should RAG quality be evaluated?","max_sources":2})
    assert r.status_code==200
    body=r.json()
    assert len(body["plan"])==4 and len(body["sources"])==2
    assert "Evidence summary" in body["report"]

def test_short_question_rejected():
    assert client.post("/research",json={"question":"Hi"}).status_code==422
