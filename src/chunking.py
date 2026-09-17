from typing import List, Dict


def chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100
) -> List[str]:
    """
    Split text into overlapping chunks.

    Args:
        text: Cleaned document text.
        chunk_size: Maximum number of characters in each chunk.
        chunk_overlap: Number of characters shared between chunks.

    Returns:
        List of text chunks.
    """

    if not text:
        return []

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size"
        )

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = end - chunk_overlap

    return chunks


def create_document_chunks(
    documents: List[Dict],
    chunk_size: int = 500,
    chunk_overlap: int = 100
) -> List[Dict]:
    """
    Create chunks while preserving source-document metadata.
    """

    all_chunks = []

    for document in documents:

        chunks = chunk_text(
            document["content"],
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        for chunk_id, chunk in enumerate(chunks):

            all_chunks.append(
                {
                    "chunk_id": len(all_chunks),
                    "source": document["source"],
                    "content": chunk,
                    "document_chunk_id": chunk_id
                }
            )

    return all_chunks


if __name__ == "__main__":

    from src.document_loader import load_documents

    documents = load_documents()

    chunks = create_document_chunks(
        documents,
        chunk_size=500,
        chunk_overlap=100
    )

    print(f"\nDocuments: {len(documents)}")
    print(f"Total chunks: {len(chunks)}\n")

    for chunk in chunks:
        print(f"Chunk ID: {chunk['chunk_id']}")
        print(f"Source: {chunk['source']}")
        print(f"Document Chunk: {chunk['document_chunk_id']}")
        print(f"Characters: {len(chunk['content'])}")
        print(f"Content:\n{chunk['content']}")
        print("=" * 70)
