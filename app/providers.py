from dataclasses import dataclass
from typing import Protocol

@dataclass
class Source:
    title: str
    url: str
    excerpt: str

class ResearchProvider(Protocol):
    def search(self, query: str, limit: int) -> list[Source]: ...
    def synthesize(self, question: str, sources: list[Source]) -> str: ...

class DemoResearchProvider:
    """Offline demo provider; replace with live search and LLM integrations."""
    def search(self, query: str, limit: int) -> list[Source]:
        samples = [
            Source("RAG evaluation dimensions","https://example.com/rag-evaluation","Evaluate retrieval relevance, groundedness, completeness, latency, and cost."),
            Source("Reliable research workflows","https://example.com/research-workflows","Separate planning, evidence collection, review, and synthesis; preserve provenance."),
            Source("Human review for AI research","https://example.com/human-review","Review high-impact claims, conflicting evidence, and unsupported conclusions."),
        ]
        return samples[:max(0, limit)]

    def synthesize(self, question: str, sources: list[Source]) -> str:
        if not sources: return "No evidence returned. Configure a live research provider."
        lines = "\n".join(f"- {s.title}: {s.excerpt} [Source: {s.url}]" for s in sources)
        return f"Question: {question}\n\nEvidence summary (demo data):\n{lines}\n\nCaution: sample evidence is illustrative; verify sources before relying on this report."
