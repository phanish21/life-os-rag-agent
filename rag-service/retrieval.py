from datetime import datetime, timezone
import numpy as np

def compute_recency_score(create_at: str, half_life_days: float = 7.0)-> float:
    """
    Exponential decay. A memory exactly `half_life_days` old scores 0.5.
    Older = closer to 0, newer = closer to 1.
    """
    created = datetime.fromisoformat(create_at.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    age_days = (now - created).total_seconds() / 86400

    decay_rate = np.log(2) / half_life_days
    return float(np.exp(-decay_rate*age_days))

def rerank_by_recency(
    candidates: list[dict],
    limit: int=5,
    similarity_Weight: float=0.7,
    recency_weight: float=0.3,
    half_life_days: float=7.0,
    min_similiarity: float=0.40,
) -> list[dict]:
    filtered = []
    for c in candidates:
        similarty = 1 - (c["distance"]/2)
        if similarty < min_similiarity:
            continue
        recency = compute_recency_score(c["created_at"], half_life_days)

        c["similarity_score"] = round(similarty, 4)
        c["recency_score"] = round(recency, 4)
        c["combined_score"] = round( similarity_Weight*similarty + recency_weight*recency, 4)
        filtered.append(c)

    filtered.sort(key=lambda c: c["combined_score"], reverse=True)
    return filtered[:limit]

# def rerank_by_recency(
#     candidates: list[dict],
#     limit: int = 5,
#     similarity_weight: float = 0.7,
#     recency_weight: float = 0.3,
#     half_life_days: float = 7.0,
#     max_similarity_gap: float = 0.25,  # drop anything this much worse than the best match
# ) -> list[dict]:
#     scored = []
#     for c in candidates:
#         similarity = 1 - (c["distance"] / 2)
#         recency = compute_recency_score(c["created_at"], half_life_days)
#         c["similarity_score"] = round(similarity, 4)
#         c["recency_score"] = round(recency, 4)
#         c["combined_score"] = round(
#             similarity_weight * similarity + recency_weight * recency, 4
#         )
#         scored.append(c)

#     if not scored:
#         return []

#     best_similarity = max(c["similarity_score"] for c in scored)
#     filtered = [
#         c for c in scored
#         if best_similarity - c["similarity_score"] <= max_similarity_gap
#     ]

#     filtered.sort(key=lambda c: c["combined_score"], reverse=True)
#     return filtered[:limit]