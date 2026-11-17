from typing import TypedDict
from langgraph.graph import END, START, StateGraph
from app.providers import DemoResearchProvider, ResearchProvider, Source

class ResearchState(TypedDict, total=False):
    question: str
    max_sources: int
    plan: list[str]
    sources: list[Source]
    review: str
    report: str

class ResearchWorkflow:
    def __init__(self, provider: ResearchProvider | None = None):
        self.provider = provider or DemoResearchProvider()
        graph = StateGraph(ResearchState)
        graph.add_node("plan", self.plan)
        graph.add_node("research", self.research)
        graph.add_node("review", self.review)
        graph.add_node("synthesize", self.synthesize)
        graph.add_edge(START, "plan")
        graph.add_edge("plan", "research")
        graph.add_edge("research", "review")
        graph.add_edge("review", "synthesize")
        graph.add_edge("synthesize", END)
        self.graph = graph.compile()

    def plan(self, state: ResearchState) -> dict:
        return {"plan":[f"Clarify scope for: {state['question']}","Collect evidence and preserve source metadata","Review evidence coverage and limitations","Synthesize a concise cited report"]}

    def research(self, state: ResearchState) -> dict:
        limit=max(1,min(int(state.get("max_sources",3)),10))
        return {"sources":self.provider.search(state["question"],limit)}

    def review(self, state: ResearchState) -> dict:
        return {"review":f"Collected {len(state.get('sources',[]))} source(s). Verify relevance, dates, and claims."}

    def synthesize(self, state: ResearchState) -> dict:
        return {"report":self.provider.synthesize(state["question"],state.get("sources",[]))}

    def run(self, question: str, max_sources: int=3) -> dict:
        return self.graph.invoke({"question":question,"max_sources":max_sources})
