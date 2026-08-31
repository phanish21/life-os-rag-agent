from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np

from embeddings import generate_embedding
from vector_store import (store_journal_embeddings, search_journal_embeddings, get_memory_count)
from semantic_chunking import semantic_chunking
from retrieval import rerank_by_recency
from attributeSearch import retrieve_for_attribute, ATTRIBUTE_QUERY_TEMPLATES

app = FastAPI(
    title="Life OS RAG service",
    description="AI memory and retrieval service for Life OS"
)

class EmbedRequest(BaseModel):
    text: str

class JournalIndexRequest(BaseModel):
    journal_id: int
    content: str
    created_at: str

class SearchRequest(BaseModel):
    query: str
    limit: int=5

class AttributeSearchRequest(BaseModel):
    attribute: str
    limit_per_query: int = 5
    final_limit: int = 8
    similarity_weight: float = 0.7
    recency_weight: float = 0.3
    half_life_days: float = 7.0

@app.get("/")
def health_check():
    return{
        "status": "active",
        "message": "[SYSTEM]: RAG service is online."
    }

@app.post("/embed")
def create_embeddings(request: EmbedRequest):
    embedding = generate_embedding(request.text)
    return {
        "dimensions":len(embedding),
        "embedding": embedding
    }

@app.post("/index")
def index_journal(request: JournalIndexRequest):
    chunks = semantic_chunking(request.content, similarity_threshold=0.50)

    for chunk_id, chunk in enumerate(chunks):
        embedding = generate_embedding(chunk)

        print(f"""store_journal_embeddings:journal_id={request.journal_id},
chunk_id={chunk_id},
content={chunk},
created_at={request.created_at}""")

        store_journal_embeddings(
            journal_id=request.journal_id,
            chunk_id=chunk_id,
            content=chunk,
            embeddings=embedding,
            created_at=request.created_at
        )

    return {
        "message": "[SYSTEM]: Memory indexed successfully.",
        "journal_id": request.journal_id
    }

@app.post("/search")
def search_embedding(request: SearchRequest):
    query_embedding = generate_embedding(request.query)

    candidate_count = max(request.limit*4, 20)
    result = search_journal_embeddings(
        query_embeddings=query_embedding,
        limit=candidate_count)

    candidates = []

    documents = result.get("documents",[[]])[0]
    metadatas = result.get("metadatas",[[]])[0]
    distances = result.get("distances",[[]])[0]

    for document, metadata, distance in zip(documents,metadatas,distances):
        candidates.append({
            "journal_id": metadata["journal_id"],
            "content": document,
            "created_at": metadata["created_at"],
            "distance": distance
        })

    reranker = rerank_by_recency(candidates, limit=request.limit)

    return {
        "query": request.query,
        "count": len(reranker),
        "embeddings": reranker
    }

@app.post("/search/attribute")
def search_by_attribute(request: AttributeSearchRequest):
    try:
        chunks = retrieve_for_attribute(
            attribute=request.attribute,
            limit_per_query=request.limit_per_query,
            final_limit=request.final_limit,
            similarity_weight=request.similarity_weight,
            recency_weight=request.recency_weight,
            half_life_days=request.half_life_days
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "attribute": request.attribute,
        "count": len(chunks),
        "chunks": chunks
    }
    
@app.get("/debug/memory-count")
def memory_count():
    return {
        "indexed_memories": get_memory_count()
    }

@app.post("/chunk")
def chunk_journal(request: EmbedRequest):
    chunks = semantic_chunking(request.text)

    return {
        "chunks count": len(chunks),
        "chunks": [
            {
                "chunk_id": index,
                "content": chunk
            }
            for index, chunk in enumerate(chunks)
        ]
    }