from embeddings import generate_embedding
from vector_store import search_journal_embeddings
from retrieval import rerank_by_recency

ATTRIBUTE_QUERY_TEMPLATES = {
    "vitality": [
        "physical health",
        "exercise and movement",
        "sleep and energy",
        "eating habits",
    ],
    "focus": [
        "discipline and consistency",
        "procrastination",
        "concentration and productivity",
        "unfinished tasks",
    ],
    "intellect": [
        "learning something new",
        "studying or practicing a skill",
        "reading or research",
    ],
    "balance": [
        "stress and rest",
        "emotional wellbeing",
        "feeling overwhelmed",
        "relaxation",
    ],
    "connection": [
        "time with friends or family",
        "relationships",
        "social interactions",
    ],
    "progress": [
        "career or project progress",
        "goals and achievements",
        "work accomplishments",
    ],
}

def _search_single_query(
    query: str,
    limit: int, 
    similarity_weight: float, 
    recency_weight: float, 
    half_life_days: float
) -> list[dict]:
    query_embedding = generate_embedding(query)
    candidate_count = max(limit*4, 20)

    result = search_journal_embeddings(
        query_embeddings= query_embedding,
        limit= candidate_count
    )

    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances  = result.get("distances", [[]])[0]

    candidates = []

    for document, metadata, distance in zip(documents, metadatas, distances):
        candidates.append({
            "journal_id": metadata["journal_id"],
            "content": document,
            "created_at": metadata["created_at"],
            "distance": distance
        })
    return rerank_by_recency(
        candidates,
        limit=limit,
        similarity_Weight=similarity_weight,
        recency_weight=recency_weight,
        half_life_days=half_life_days
    )

def retrieve_for_attribute(
    attribute: str,
    limit_per_query: int = 5,
    final_limit: int = 8,
    similarity_weight: float = 0.7,
    recency_weight: float = 0.3,
    half_life_days: float = 7.0,
) -> list[dict]:
    attribute = attribute.lower()
    if attribute not in ATTRIBUTE_QUERY_TEMPLATES:
        raise ValueError(f"Unknown attribute: {attribute}")

    queries = ATTRIBUTE_QUERY_TEMPLATES[attribute]
    best_by_chunks = {}

    for query in queries:
        results = _search_single_query(
            query, limit_per_query, similarity_weight, recency_weight, half_life_days 
        )

        for r in results:
            key = (r["journal_id"], r["content"])

            if key not in best_by_chunks or r["combined_score"] > best_by_chunks[key]["combined_score"]:
                best_by_chunks[key] = r

    merged = sorted(best_by_chunks.values(), key=lambda r: r["combined_score"], reverse=True)

    return merged[:final_limit]