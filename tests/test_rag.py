from app.rag import retriever


def test_retriever_loads_knowledge_base():
    assert len(retriever.chunks) > 0


def test_search_returns_relevant_chunk_for_cancellation_query():
    results = retriever.search("How do I cancel my booking?", top_k=3)
    assert results, "expected at least one result"
    top_chunk, score = results[0]
    assert "cancel" in top_chunk.text.lower()
    assert score > 0


def test_search_returns_relevant_chunk_for_payment_query():
    results = retriever.search("Why did my payment get declined?", top_k=3)
    assert results
    top_chunk, _ = results[0]
    assert "payment" in top_chunk.text.lower() or "declined" in top_chunk.text.lower()


def test_search_on_gibberish_query_has_low_confidence():
    results = retriever.search("zzqx flarn wobble unrelated nonsense", top_k=3)
    # Either no results, or the top score is very low (near zero similarity).
    if results:
        assert results[0][1] < 0.2
