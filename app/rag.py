"""
Lightweight retrieval-augmented generation layer.

Uses TF-IDF + cosine similarity instead of a hosted embeddings API or a
vector database. That's a deliberate tradeoff for a support-bot demo of
this size: it needs zero API keys and no external services to run, while
still exercising the real RAG pattern (chunk -> index -> retrieve ->
ground the LLM's answer in retrieved text). Swapping in OpenAI/Gemini
embeddings + a vector DB (e.g. Chroma, pgvector) later only touches this
file - the agents call `retriever.search()` and don't care how it works
under the hood.
"""
from __future__ import annotations

import glob
import os
from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.config import settings


@dataclass
class Chunk:
    text: str
    source: str


def _chunk_text(text: str, source: str, max_words: int = 120) -> list[Chunk]:
    """Split a markdown doc into paragraph-based chunks capped at max_words."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[Chunk] = []
    buffer: list[str] = []
    word_count = 0

    for para in paragraphs:
        words = para.split()
        if word_count + len(words) > max_words and buffer:
            chunks.append(Chunk(text="\n\n".join(buffer), source=source))
            buffer, word_count = [], 0
        buffer.append(para)
        word_count += len(words)

    if buffer:
        chunks.append(Chunk(text="\n\n".join(buffer), source=source))
    return chunks


class Retriever:
    def __init__(self, kb_dir: str | None = None):
        self.kb_dir = kb_dir or settings.knowledge_base_dir
        self.chunks: list[Chunk] = []
        self.vectorizer: TfidfVectorizer | None = None
        self._matrix = None
        self.reload()

    def reload(self) -> None:
        self.chunks = []
        for path in sorted(glob.glob(os.path.join(self.kb_dir, "*.md"))):
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            self.chunks.extend(_chunk_text(text, source=os.path.basename(path)))

        if not self.chunks:
            self.vectorizer = None
            self._matrix = None
            return

        self.vectorizer = TfidfVectorizer(stop_words="english")
        self._matrix = self.vectorizer.fit_transform([c.text for c in self.chunks])

    def search(self, query: str, top_k: int | None = None) -> list[tuple[Chunk, float]]:
        """Return up to top_k (chunk, similarity_score) pairs, highest first."""
        if not self.chunks or self.vectorizer is None:
            return []

        top_k = top_k or settings.top_k
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self._matrix)[0]
        ranked = sorted(zip(self.chunks, scores), key=lambda pair: pair[1], reverse=True)
        return ranked[:top_k]


retriever = Retriever()
