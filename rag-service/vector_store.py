import chromadb
import os

CHROMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_data")

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = client.get_or_create_collection(
    name = "journal_emmbeddings"
)

def store_journal_embeddings(
    journal_id: int,
    chunk_id: int,
    content: str,
    embeddings: list[float],
    created_at: str
):
    vector_id= f"journal_{journal_id}_chunk_{chunk_id}"
    collection.upsert(
        ids=[vector_id],
        documents=[content],
        embeddings=[embeddings],
        metadatas=[
            {
                "journal_id": journal_id,
                "chunk_id": chunk_id,
                "created_at": created_at
            }
        ]
    )

def search_journal_embeddings(
    query_embeddings: list[float],
    limit: int=5):
    result = collection.query(
        query_embeddings=[query_embeddings],
        n_results=limit,
        include=["documents", "metadatas", "distances"]
    )
    return result

def get_memory_count():
    return collection.count()