"""
Retrieval evaluation harness.

Seeds the known-attribute fixtures into the RAG service, then for each
attribute checks whether /search/attribute actually surfaces the chunks
that are truly about that attribute (recall), how much noise comes back
(precision), and whether chunks meant for OTHER attributes leak in
(cross-attribute leakage - a sign the query templates or embeddings
aren't discriminating well between topics).

"""

import requests
from collections import defaultdict

from fixtures import FIXTURES, FIXED_TIMESTAMP

RAG_BASE_URL = "http://localhost:8000"
FINAL_LIMIT = 6

SIMILARITY_WEIGHT = 1.0
RECENCY_WEIGHT = 0.0


def seed_fixtures():
    print(f"Seeding {len(FIXTURES)} fixture entries into the RAG service...\n")
    for fixture in FIXTURES:
        response = requests.post(f"{RAG_BASE_URL}/index", json={
            "journal_id": fixture["journal_id"],
            "content": fixture["content"],
            "created_at": FIXED_TIMESTAMP,
        })
        if not response.ok:
            print(f"  FAILED to index journal_id={fixture['journal_id']}: {response.status_code} {response.text}")
    print("Seeding done.\n")


def run_attribute_query(attribute: str):
    response = requests.post(f"{RAG_BASE_URL}/search/attribute", json={
        "attribute": attribute,
        "final_limit": FINAL_LIMIT,
        "similarity_weight": SIMILARITY_WEIGHT,
        "recency_weight": RECENCY_WEIGHT,
    })
    if not response.ok:
        print(f"  ERROR querying attribute={attribute}: {response.status_code} {response.text}")
        return []
    return response.json().get("chunks", [])


def evaluate():
    ground_truth = defaultdict(set)
    for fixture in FIXTURES:
        ground_truth[fixture["expected_attribute"]].add(fixture["journal_id"])

    attributes = sorted(ground_truth.keys())
    results = []

    for attribute in attributes:
        relevant_ids = ground_truth[attribute]
        chunks = run_attribute_query(attribute)
        chunks = [c for c in chunks if c["journal_id"] >= 9000]  # ignore pre-existing real data
        retrieved_ids = {c["journal_id"] for c in chunks}

        true_positives = relevant_ids & retrieved_ids
        leaked_ids = retrieved_ids - relevant_ids  

        recall = len(true_positives) / len(relevant_ids) if relevant_ids else None
        precision = len(true_positives) / len(retrieved_ids) if retrieved_ids else None

        results.append({
            "attribute": attribute,
            "relevant_count": len(relevant_ids),
            "retrieved_count": len(retrieved_ids),
            "true_positives": len(true_positives),
            "leaked_ids": leaked_ids,
            "recall": recall,
            "precision": precision,
        })

    return results


def print_report(results):
    print(f"{'Attribute':<12} {'Recall':<8} {'Precision':<10} {'Hits':<6} {'Leaked journal_ids'}")
    print("-" * 70)
    for r in results:
        recall_str = f"{r['recall']:.2f}" if r["recall"] is not None else "n/a"
        precision_str = f"{r['precision']:.2f}" if r["precision"] is not None else "n/a"
        leaked = sorted(r["leaked_ids"]) if r["leaked_ids"] else "-"
        print(f"{r['attribute']:<12} {recall_str:<8} {precision_str:<10} {r['true_positives']:<6} {leaked}")

    avg_recall = sum(r["recall"] for r in results if r["recall"] is not None) / len(results)
    avg_precision = sum(r["precision"] for r in results if r["precision"] is not None) / len(results)
    print("-" * 70)
    print(f"Average recall:    {avg_recall:.2f}")
    print(f"Average precision: {avg_precision:.2f}")

    print("\nWhat these numbers mean:")
    print("  Recall < 1.0   -> some genuinely relevant memories are NOT being retrieved for this attribute")
    print("  Precision < 1.0 -> irrelevant/cross-topic memories ARE being retrieved (noise)")
    print("  Non-empty leaked_ids -> a specific chunk from another attribute is leaking in; worth reading it")


if __name__ == "__main__":
    seed_fixtures()
    results = evaluate()
    print_report(results)