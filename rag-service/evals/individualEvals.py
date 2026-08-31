"""
Per-template retrieval debug.

Unlike retrievalEvals.py (which tests the MERGED result across all
templates for an attribute), this runs each individual template query
on its own and shows exactly what it retrieves. Use this to find:
  - dud templates that never surface true positives
  - true positives that rank just outside limit_per_query, before merging

"""

import requests
 
from fixtures import FIXTURES
 
RAG_BASE_URL = "http://localhost:8000"
LIMIT_PER_QUERY = 8
MIN_FIXTURE_ID = 9000  # filter out pre-existing real journal entries
 
# Keep this in sync with attribute_search.py's ATTRIBUTE_QUERY_TEMPLATES.
ATTRIBUTE_QUERY_TEMPLATES = {
    "vitality": ["physical health", "exercise and movement", "sleep and energy", "eating habits"],
    "focus": ["discipline and consistency", "procrastination", "concentration and productivity", "unfinished tasks"],
    "intellect": ["learning something new", "studying or practicing a skill", "reading or research"],
    "balance": ["stress and rest", "emotional wellbeing", "feeling overwhelmed", "relaxation"],
    "connection": ["time with friends or family", "relationships", "social interactions"],
    "progress": ["career or project progress", "goals and achievements", "work accomplishments"],
}
 
 
def ground_truth_for(attribute: str) -> set[int]:
    return {f["journal_id"] for f in FIXTURES if f["expected_attribute"] == attribute}
 
 
def search(query: str, limit: int):
    response = requests.post(f"{RAG_BASE_URL}/search", json={"query": query, "limit": limit})
    if not response.ok:
        print(f"    ERROR: {response.status_code} {response.text}")
        return []
    return response.json().get("embeddings", [])
 
 
def run():
    for attribute, templates in ATTRIBUTE_QUERY_TEMPLATES.items():
        relevant_ids = ground_truth_for(attribute)
        print(f"\n=== {attribute} (expects fixtures: {sorted(relevant_ids)}) ===")
 
        found_by_any_template = set()
 
        for query in templates:
            results = search(query, LIMIT_PER_QUERY)
            results = [r for r in results if r["journal_id"] >= MIN_FIXTURE_ID]
 
            hit_ids = {r["journal_id"] for r in results if r["journal_id"] in relevant_ids}
            found_by_any_template |= hit_ids
 
            print(f"  \"{query}\"")
            if not results:
                print(f"    -> no fixture results at all")
            for r in results:
                marker = "v" if r["journal_id"] in relevant_ids else " "
                sim = r.get("similarity_score", "?")
                print(f"    [{marker}] id={r['journal_id']} sim={sim}  {r['content'][:70]}")
 
        missed = relevant_ids - found_by_any_template
        if missed:
            print(f"  >>> NEVER retrieved by ANY template for this attribute: {sorted(missed)}")
        else:
            print(f"  >>> all relevant fixtures were found by at least one template")
 
 
if __name__ == "__main__":
    run()