from pathlib import Path
from typing import List, Dict


def clean_text(text: str) -> str:
    """
    Clean document text by removing unnecessary whitespace.
    """
    lines = [line.strip() for line in text.splitlines()]

    cleaned_lines = []

    for line in lines:
        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def load_documents(data_path: str = "data/airport_policies") -> List[Dict]:
    """
    Load all Markdown policy documents from the specified directory.
    """

    documents = []

    policy_path = Path(data_path)

    if not policy_path.exists():
        raise FileNotFoundError(
            f"Policy directory not found: {data_path}"
        )

    for file_path in sorted(policy_path.glob("*.md")):
        with open(file_path, "r", encoding="utf-8") as file:
            raw_text = file.read()

        cleaned_text = clean_text(raw_text)

        document = {
            "source": file_path.name,
            "content": cleaned_text
        }

        documents.append(document)

    return documents


if __name__ == "__main__":
    documents = load_documents()

    print(f"\nDocuments loaded: {len(documents)}\n")

    for document in documents:
        print(f"Source: {document['source']}")
        print(f"Characters: {len(document['content'])}")
        print("-" * 50)
