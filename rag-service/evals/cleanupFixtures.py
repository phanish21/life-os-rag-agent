"""
Deletes fixture/test entries from Chroma so eval runs don't leave
synthetic data lying around to contaminate later real usage or crash
quest_generation_eval.py with foreign key errors.

Imports `collection` directly from vector_store.py rather than
reconstructing a new client, so this is guaranteed to point at the
exact same persistent data your server uses - no risk of a name/path
mismatch silently doing nothing.

Run from the rag-service directory (or adjust the sys.path insert
below to point at wherever vector_store.py lives):

    python cleanup_fixtures.py

Requires the server to be STOPPED, or at least not mid-write, since
this opens the same persistent Chroma directory directly.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from vector_store import collection, get_memory_count

MIN_FIXTURE_ID = 9000


def preview_fixture_entries():
    """Chroma's `where` filters need an explicit numeric comparison -
    fetch everything and filter in Python for a clear before/after count,
    since collection.get() with no filter is cheap for a personal-scale index."""
    all_entries = collection.get(include=["metadatas"])
    fixture_ids_found = [
        (entry_id, meta.get("journal_id"))
        for entry_id, meta in zip(all_entries["ids"], all_entries["metadatas"])
        if meta.get("journal_id", 0) >= MIN_FIXTURE_ID
    ]
    return fixture_ids_found


def run():
    print(f"Total entries in collection before cleanup: {get_memory_count()}")

    fixture_entries = preview_fixture_entries()
    if not fixture_entries:
        print(f"No entries with journal_id >= {MIN_FIXTURE_ID} found. Nothing to clean up.")
        return

    print(f"\nFound {len(fixture_entries)} fixture entries to delete:")
    for vector_id, journal_id in fixture_entries:
        print(f"  {vector_id}  (journal_id={journal_id})")

    confirm = input(f"\nDelete these {len(fixture_entries)} entries? [y/N] ").strip().lower()
    if confirm != "y":
        print("Aborted. Nothing was deleted.")
        return

    ids_to_delete = [vector_id for vector_id, _ in fixture_entries]
    collection.delete(ids=ids_to_delete)

    print(f"\nDeleted {len(ids_to_delete)} entries.")
    print(f"Total entries in collection after cleanup: {get_memory_count()}")


if __name__ == "__main__":
    run()