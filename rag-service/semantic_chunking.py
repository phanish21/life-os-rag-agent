import re
import numpy as np

from embeddings import model

def split_into_sentences(text: str) -> list[str]:
    """
    Basic sentence splitting for MVP.
    """
    sentences = re.split(r'(?<=[.!?])\s+',text.strip())
    return [ sentence.strip() for sentence in sentences if sentence.strip() ]

def semantic_chunking(
    text: str,
    similarity_threshold: float= 0.50,
    max_sentences: int= 5
) -> list[str]:
    """
    Groups consecutive sentences based on semantic similarity.

    A new chunk starts when the current sentence is
    sufficiently different from the previous sentence.
    """
    sentences = split_into_sentences(text)

    if not sentences:
        return

    if len(sentences) == 1:
        return sentences

    embeddings = model.encode(
        sentences, normalize_embeddings=True
    )

    chunks = []
    current_chunk_sentences = [sentences[0]]
    current_chunk_embeddings = [embeddings[0]]

    for i in range(1, len(sentences)):
        current_embedding = embeddings[i]

        # Calculate the semantic representation
        # of everything currently in the chunk
        chunk_embedding = np.mean(current_chunk_embeddings,axis=0)

        # Normalize because we're using cosine similarity
        chunk_embedding = (chunk_embedding/ np.linalg.norm(chunk_embedding))

        similarity = float(np.dot(chunk_embedding, current_embedding))

        # Debug: inspect what the embedding model thinks
        print(f"\nSentence {i}: {sentences[i]}")
        print(f"Similarity with current chunk: {current_chunk_sentences} {similarity:.3f}")

        # Split when the meaning changes or the chunk
        # becomes too large
        should_split = (
            similarity < similarity_threshold or len(current_chunk_sentences) >= max_sentences
        )

        if should_split:
            chunks.append(" ".join(current_chunk_sentences))
            current_chunk_sentences = [sentences[i]]
            current_chunk_embeddings = [embeddings[i]]
        else:
            current_chunk_sentences.append(sentences[i])
            current_chunk_embeddings.append(current_embedding)

    # Add the final chunk
    if current_chunk_sentences:
        chunks.append(" ".join(current_chunk_sentences))

    return chunks