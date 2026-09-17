from pathlib import Path
from typing import List, Dict, Tuple

import faiss
import numpy as np


ARTIFACTS_DIR = Path("artifacts")
INDEX_PATH = ARTIFACTS_DIR / "policy.index"


def create_faiss_index(
    embeddings: np.ndarray
) -> faiss.Index:
    """
    Create a FAISS index using L2 distance.
    """

    embedding_dimension = embeddings.shape[1]

    print(f"Embedding dimension: {embedding_dimension}")

    index = faiss.IndexFlatL2(embedding_dimension)

    index.add(embeddings)

    print(f"FAISS index created.")
    print(f"Vectors stored: {index.ntotal}")

    return index


def save_faiss_index(
    index: faiss.Index,
    index_path: Path = INDEX_PATH
) -> None:
    """
    Save the FAISS index to disk.
    """

    index_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    faiss.write_index(
        index,
        str(index_path)
    )

    print(f"FAISS index saved to: {index_path}")


def load_faiss_index(
    index_path: Path = INDEX_PATH
) -> faiss.Index:
    """
    Load an existing FAISS index from disk.
    """

    if not index_path.exists():
        raise FileNotFoundError(
            f"FAISS index not found: {index_path}"
        )

    index = faiss.read_index(
        str(index_path)
    )

    return index


if __name__ == "__main__":

    from src.document_loader import load_documents
    from src.chunking import create_document_chunks
    from src.embeddings import (
        load_embedding_model,
        create_embeddings
    )

    print("\n" + "=" * 60)
    print("FAISS VECTOR STORE")
    print("=" * 60)

    # Step 1: Load policy documents
    documents = load_documents()

    # Step 2: Create chunks
    chunks = create_document_chunks(
        documents,
        chunk_size=500,
        chunk_overlap=100
    )

    print(f"\nDocuments: {len(documents)}")
    print(f"Chunks: {len(chunks)}")

    # Step 3: Load embedding model
    model = load_embedding_model()

    # Step 4: Create embeddings
    embeddings, _ = create_embeddings(
        chunks,
        model
    )

    # Step 5: Create FAISS index
    index = create_faiss_index(
        embeddings
    )

    # Step 6: Save index
    save_faiss_index(
        index
    )

    print("\n" + "=" * 60)
    print("FAISS VECTOR STORE TEST COMPLETED")
    print("=" * 60)
