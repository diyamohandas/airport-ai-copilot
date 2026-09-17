from typing import List, Dict

import faiss
import numpy as np

from src.document_loader import load_documents
from src.chunking import create_document_chunks
from src.embeddings import load_embedding_model
from src.vector_store import load_faiss_index


def retrieve_chunks(
    query: str,
    model,
    index,
    chunks: List[Dict],
    top_k: int = 3
) -> List[Dict]:
    """
    Retrieve the most relevant document chunks for a query.
    """

    if not query.strip():
        return []

    # Convert query into an embedding
    query_embedding = model.encode(
        [query],
        convert_to_numpy=True
    )

    query_embedding = query_embedding.astype("float32")

    # Search FAISS
    distances, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for rank, (distance, index_id) in enumerate(
        zip(distances[0], indices[0]),
        start=1
    ):

        if index_id == -1:
            continue

        chunk = chunks[index_id]

        results.append(
            {
                "rank": rank,
                "score": float(distance),
                "source": chunk["source"],
                "chunk_id": chunk["chunk_id"],
                "document_chunk_id": chunk["document_chunk_id"],
                "content": chunk["content"]
            }
        )

    return results


if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("SEMANTIC RETRIEVAL TEST")
    print("=" * 60)

    # Load documents
    documents = load_documents()

    # Recreate chunks in the same order used to build FAISS
    chunks = create_document_chunks(
        documents,
        chunk_size=500,
        chunk_overlap=100
    )

    # Load embedding model
    model = load_embedding_model()

    # Load FAISS index
    index = load_faiss_index()

    print(f"\nDocuments: {len(documents)}")
    print(f"Chunks: {len(chunks)}")
    print(f"FAISS vectors: {index.ntotal}")

    # Test question
    query = "What is the maximum surge multiplier at SFO?"

    print(f"\nQuery: {query}")
    print("\nRetrieved chunks:")
    print("-" * 60)

    results = retrieve_chunks(
        query=query,
        model=model,
        index=index,
        chunks=chunks,
        top_k=3
    )

    for result in results:

        print(f"\nRank: {result['rank']}")
        print(f"Score: {result['score']:.4f}")
        print(f"Source: {result['source']}")
        print(f"Chunk ID: {result['chunk_id']}")
        print(f"Document Chunk: {result['document_chunk_id']}")
        print("\nContent:")
        print(result["content"])
        print("-" * 60)

    print("\nSemantic retrieval test completed.")
