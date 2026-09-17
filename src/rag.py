from typing import Dict, List

from src.document_loader import load_documents
from src.chunking import create_document_chunks
from src.embeddings import load_embedding_model
from src.vector_store import load_faiss_index
from src.retrieval import retrieve_chunks
from src.llm import load_groq_client, generate_answer


def build_context(results: List[Dict]) -> str:
    """
    Build the policy context that will be provided to the LLM.
    """

    context_parts = []

    for result in results:
        context_parts.append(
            f"Source: {result['source']}\n"
            f"Content:\n{result['content']}"
        )

    return "\n\n".join(context_parts)


def retrieve_for_question(
    question: str,
    model,
    index,
    chunks: List[Dict],
    top_k: int = 3
) -> Dict:
    """
    Retrieve the most relevant policy chunks for a question.
    """

    results = retrieve_chunks(
        query=question,
        model=model,
        index=index,
        chunks=chunks,
        top_k=top_k
    )

    context = build_context(results)

    sources = []

    for result in results:
        if result["source"] not in sources:
            sources.append(result["source"])

    return {
        "question": question,
        "results": results,
        "context": context,
        "sources": sources
    }


def answer_with_rag(
    question: str,
    model,
    index,
    chunks: List[Dict],
    client,
    top_k: int = 3
) -> Dict:
    """
    Run the complete RAG pipeline.

    Question
        ↓
    Semantic Retrieval
        ↓
    Context Construction
        ↓
    Groq LLM
        ↓
    Grounded Answer
    """

    rag_result = retrieve_for_question(
        question=question,
        model=model,
        index=index,
        chunks=chunks,
        top_k=top_k
    )

    answer = generate_answer(
        question=question,
        context=rag_result["context"],
        client=client
    )

    return {
        "question": question,
        "answer": answer,
        "sources": rag_result["sources"],
        "retrieved_chunks": rag_result["results"]
    }


def evaluate_retrieval(
    retrieved_chunks: List[Dict],
    expected_source: str
) -> bool:
    """
    Check whether the expected policy document
    appears in the retrieved results.
    """

    retrieved_sources = [
        chunk["source"]
        for chunk in retrieved_chunks
    ]

    return expected_source in retrieved_sources


def print_result(
    result: Dict,
    expected_source: str = None,
    retrieval_correct: bool = None
) -> None:
    """
    Display the result of one evaluation question.
    """

    print("\n" + "=" * 60)
    print("TEST QUESTION")
    print("=" * 60)

    print(result["question"])

    print("\n" + "-" * 60)
    print("GENERATED ANSWER")
    print("-" * 60)

    print(result["answer"])

    print("\n" + "-" * 60)
    print("SOURCE DOCUMENTS")
    print("-" * 60)

    for source in result["sources"]:
        print(f"- {source}")

    print("\n" + "-" * 60)
    print("RETRIEVED CHUNKS")
    print("-" * 60)

    for retrieved in result["retrieved_chunks"]:
        print(
            f"Rank {retrieved['rank']} | "
            f"Score {retrieved['score']:.4f} | "
            f"Source {retrieved['source']} | "
            f"Chunk ID {retrieved['chunk_id']}"
        )

    if expected_source is not None:

        print("\n" + "-" * 60)
        print("RETRIEVAL EVALUATION")
        print("-" * 60)

        print(f"Expected source: {expected_source}")

        if retrieval_correct:
            print("Result: PASS")
            print("Expected policy document was retrieved.")
        else:
            print("Result: FAIL")
            print("Expected policy document was not retrieved.")


if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("AIRPORT OPERATIONS AI COPILOT")
    print("DAY 1 - RAG EVALUATION")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. LOAD DOCUMENTS
    # ---------------------------------------------------------

    print("\nLoading policy documents...")

    documents = load_documents()

    print(f"Documents loaded: {len(documents)}")

    # ---------------------------------------------------------
    # 2. CREATE CHUNKS
    # ---------------------------------------------------------

    print("\nCreating document chunks...")

    chunks = create_document_chunks(
        documents,
        chunk_size=500,
        chunk_overlap=100
    )

    print(f"Chunks created: {len(chunks)}")

    # ---------------------------------------------------------
    # 3. LOAD EMBEDDING MODEL
    # ---------------------------------------------------------

    model = load_embedding_model()

    # ---------------------------------------------------------
    # 4. LOAD FAISS INDEX
    # ---------------------------------------------------------

    print("\nLoading FAISS index...")

    index = load_faiss_index()

    print(f"FAISS vectors: {index.ntotal}")

    # ---------------------------------------------------------
    # 5. LOAD GROQ CLIENT
    # ---------------------------------------------------------

    print("\nLoading Groq client...")

    client = load_groq_client()

    print("Groq client loaded successfully.")

    # ---------------------------------------------------------
    # 6. TEST QUESTIONS
    # ---------------------------------------------------------

    test_cases = [
        {
            "question": "What is the maximum surge multiplier at SFO?",
            "expected_source": "sfo_pricing.md"
        },
        {
            "question": (
                "What completion rate is considered "
                "a significant anomaly at SFO?"
            ),
            "expected_source": "sfo_operations.md"
        },
        {
            "question": "What is the maximum surge multiplier at LAX?",
            "expected_source": "lax_pricing.md"
        },
        {
            "question": (
                "What approval is required for surge pricing "
                "of 1.3x or higher at JFK?"
            ),
            "expected_source": "jfk_pricing.md"
        },
        {
            "question": "What is the normal driver queue target at SFO?",
            "expected_source": None
        }
    ]

    # ---------------------------------------------------------
    # 7. RUN EVALUATION
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("RUNNING DAY 1 RAG EVALUATION")
    print("=" * 60)

    correct_retrievals = 0
    evaluated_questions = 0
    results = []

    for question_number, test_case in enumerate(
        test_cases,
        start=1
    ):

        print("\n\n" + "#" * 60)
        print(
            f"TEST {question_number} "
            f"OF {len(test_cases)}"
        )
        print("#" * 60)

        question = test_case["question"]
        expected_source = test_case["expected_source"]

        result = answer_with_rag(
            question=question,
            model=model,
            index=index,
            chunks=chunks,
            client=client,
            top_k=3
        )

        results.append(result)

        # -----------------------------------------------------
        # Evaluate only questions with a known expected source
        # -----------------------------------------------------

        if expected_source is not None:

            evaluated_questions += 1

            retrieval_correct = evaluate_retrieval(
                retrieved_chunks=result["retrieved_chunks"],
                expected_source=expected_source
            )

            if retrieval_correct:
                correct_retrievals += 1

        else:
            retrieval_correct = None

        print_result(
            result=result,
            expected_source=expected_source,
            retrieval_correct=retrieval_correct
        )

        # -----------------------------------------------------
        # Special evaluation for unsupported question
        # -----------------------------------------------------

        if expected_source is None:

            print("\n" + "-" * 60)
            print("GROUNDING / UNKNOWN INFORMATION TEST")
            print("-" * 60)

            answer_lower = result["answer"].lower()

            if (
                "not provide enough information"
                in answer_lower
                or "not enough information"
                in answer_lower
                or "do not provide"
                in answer_lower
            ):
                print("Result: PASS")
                print(
                    "The system correctly avoided "
                    "inventing unsupported policy information."
                )
            else:
                print("Result: REVIEW")
                print(
                    "Check whether the answer is fully "
                    "supported by the policy context."
                )

    # ---------------------------------------------------------
    # 8. CALCULATE SUCCESS RATE
    # ---------------------------------------------------------

    if evaluated_questions > 0:
        success_rate = (
            correct_retrievals / evaluated_questions
        ) * 100
    else:
        success_rate = 0

    # ---------------------------------------------------------
    # 9. FINAL DAY 1 RESULT
    # ---------------------------------------------------------

    print("\n\n" + "=" * 60)
    print("DAY 1 RAG EVALUATION SUMMARY")
    print("=" * 60)

    print(f"\nDocuments loaded: {len(documents)}")
    print(f"Chunks created: {len(chunks)}")
    print(f"FAISS vectors: {index.ntotal}")

    print(
        f"\nQuestions with expected policy source: "
        f"{evaluated_questions}"
    )

    print(
        f"Correct policy retrievals: "
        f"{correct_retrievals}/{evaluated_questions}"
    )

    print(
        f"Retrieval success rate: "
        f"{success_rate:.0f}%"
    )

    print("\nDay 1 success criterion:")
    print(
        "Correct policy retrieval for at least "
        "4 out of 5 test questions."
    )

    if correct_retrievals >= 4:
        print("\nSTATUS: PASS")
        print(
            "Day 1 RAG retrieval criterion has been satisfied."
        )
    else:
        print("\nSTATUS: NEEDS IMPROVEMENT")
        print(
            "The retrieval system needs further evaluation "
            "or improvement."
        )

    print("\n" + "=" * 60)
    print("DAY 1 RAG EVALUATION COMPLETED")
    print("=" * 60)
