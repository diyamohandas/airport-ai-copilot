from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
import numpy as np


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def load_embedding_model() -> SentenceTransformer:
    """
    Load the Sentence Transformer embedding model.
    """
    print(f"Loading embedding model: {MODEL_NAME}")

    model = SentenceTransformer(MODEL_NAME)

    print("Embedding model loaded successfully.")

    return model


def create_embeddings(
    chunks: List[Dict],
    model: SentenceTransformer
) -> Tuple[np.ndarray, List[Dict]]:
    """
    Create embeddings for all document chunks.

    Returns:
        embeddings: NumPy array containing chunk embeddings.
        chunks: Original chunks with metadata.
    """

    texts = [chunk["content"] for chunk in chunks]

    print(f"\nCreating embeddings for {len(texts)} chunks...")

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True
    )

    embeddings = embeddings.astype("float32")

    print("\nEmbeddings created successfully.")
    print(f"Embedding shape: {embeddings.shape}")

    return embeddings, chunks


if __name__ == "__main__":

    from src.document_loader import load_documents
    from src.chunking import create_document_chunks

    # Step 1: Load documents
    documents = load_documents()

    # Step 2: Create chunks
    chunks = create_document_chunks(
        documents,
        chunk_size=500,
        chunk_overlap=100
    )

    # Step 3: Load embedding model
    model = load_embedding_model()

    # Step 4: Create embeddings
    embeddings, chunks = create_embeddings(
        chunks,
        model
    )

    print("\n" + "=" * 60)
    print("EMBEDDING TEST")
    print("=" * 60)

    print(f"Number of chunks: {len(chunks)}")
    print(f"Embedding shape: {embeddings.shape}")
    print(f"Embedding dimension: {embeddings.shape[1]}")

    print("\nFirst chunk:")
    print(chunks[0]["content"][:300])

    print("\nFirst embedding:")
    print(embeddings[0][:10])

    print("\nEmbedding pipeline test completed.")
