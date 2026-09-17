import os
from typing import Dict

from dotenv import load_dotenv
from groq import Groq

from src.prompts import build_rag_prompt


load_dotenv()

MODEL_NAME = "openai/gpt-oss-120b"


def load_groq_client() -> Groq:
    """Create and return the Groq client."""

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found. Please check your .env file."
        )

    return Groq(api_key=api_key)


def generate_answer(
    question: str,
    context: str,
    client: Groq
) -> str:
    """Generate a grounded answer using the retrieved policy context."""

    prompt = build_rag_prompt(
        question=question,
        context=context
    )

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    answer = response.choices[0].message.content

    return answer.strip()


def answer_question(
    question: str,
    rag_result: Dict,
    client: Groq
) -> Dict:
    """Generate an answer and return it with source information."""

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


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("GROQ LLM TEST")
    print("=" * 60)

    client = load_groq_client()

    test_question = "What is the maximum surge multiplier at SFO?"

    test_context = """
Source: sfo_pricing.md

SFO pricing policy:
The maximum permitted surge multiplier at SFO is 1.5x.
Surge multipliers of 1.3x or higher are considered high-risk
and require explicit human approval before activation.
"""

    answer = generate_answer(
        question=test_question,
        context=test_context,
        client=client
    )

    print("\nQuestion:")
    print(test_question)

    print("\nGenerated Answer:")
    print(answer)

    print("\n" + "=" * 60)
    print("GROQ LLM TEST COMPLETED")
    print("=" * 60)
