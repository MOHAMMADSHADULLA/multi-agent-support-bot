from dataclasses import dataclass

from app.config import settings
from app.rag import retriever


@dataclass
class RetrievalResult:
    context: str
    sources: list[str]
    confident: bool


class RetrievalAgent:
    """Finds relevant knowledge-base passages and judges whether they're
    strong enough to ground an answer, or whether the query should be
    handed to the Escalation agent instead."""

    def run(self, query: str) -> RetrievalResult:
        hits = retriever.search(query)
        if not hits:
            return RetrievalResult(context="", sources=[], confident=False)

        best_score = hits[0][1]
        context = "\n\n---\n\n".join(chunk.text for chunk, _ in hits)
        sources = sorted({chunk.source for chunk, _ in hits})
        return RetrievalResult(
            context=context,
            sources=sources,
            confident=best_score >= settings.similarity_threshold,
        )


retrieval_agent = RetrievalAgent()
