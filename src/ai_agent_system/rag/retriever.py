def retrieve_context(query: str) -> list[str]:
    # Placeholder for vector DB lookup. Replace with pgvector/Qdrant retrieval in production.
    if not query.strip():
        return []
    return [
        "Retrieved snippet about system design trade-offs.",
        "Retrieved snippet about observability and guardrails.",
    ]
