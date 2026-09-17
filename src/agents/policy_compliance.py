from typing import Any, Dict, List

from src.embeddings import load_embedding_model
from src.rag import retrieve_for_question
from src.vector_store import load_faiss_index


class PolicyComplianceAgent:
    """
    Retrieves relevant airport policies and evaluates
    a proposed operational action against the retrieved policy.
    """

    def __init__(self):
        self.name = "Policy & Compliance Agent"

        # Load the existing Day 1 RAG components.
        self.model = load_embedding_model()
        self.index = load_faiss_index()

        # Rebuild the chunk list used by the existing RAG pipeline.
        from src.document_loader import load_documents
        from src.chunking import create_document_chunks

        documents = load_documents()

        self.chunks = create_document_chunks(
            documents,
            chunk_size=500,
            chunk_overlap=100
        )

    def check_policy(
        self,
        question: str,
        airport_code: str = None,
        requested_multiplier: float = None
    ) -> Dict[str, Any]:
        """
        Retrieve relevant policy information and perform
        a structured compliance assessment.
        """

        # ---------------------------------------------------------
        # Retrieve policy information using the existing RAG system
        # ---------------------------------------------------------

        rag_result = retrieve_for_question(
            question=question,
            model=self.model,
            index=self.index,
            chunks=self.chunks,
            top_k=3
        )

        context = rag_result["context"]

        # ---------------------------------------------------------
        # Extract relevant policy information from retrieved text
        # ---------------------------------------------------------

        relevant_sources = rag_result["sources"]

        policy_text = context.lower()

        findings: List[Dict[str, Any]] = []

        # ---------------------------------------------------------
        # Surge policy validation
        # ---------------------------------------------------------

        if requested_multiplier is not None:

            # Determine maximum allowed multiplier from the
            # synthetic project policies.
            maximum_allowed = None

            if airport_code == "SFO":
                maximum_allowed = 1.5

            elif airport_code == "LAX":
                maximum_allowed = 1.6

            elif airport_code == "JFK":
                maximum_allowed = 1.5

            # -----------------------------------------------------
            # Maximum multiplier check
            # -----------------------------------------------------

            if maximum_allowed is not None:

                if requested_multiplier > maximum_allowed:

                    findings.append(
                        {
                            "rule": "maximum_surge_limit",
                            "status": "violation",
                            "description": (
                                f"Requested surge multiplier "
                                f"{requested_multiplier}x exceeds "
                                f"the synthetic maximum of "
                                f"{maximum_allowed}x for "
                                f"{airport_code}."
                            ),
                        }
                    )

                else:

                    findings.append(
                        {
                            "rule": "maximum_surge_limit",
                            "status": "compliant",
                            "description": (
                                f"Requested surge multiplier "
                                f"{requested_multiplier}x is within "
                                f"the synthetic maximum of "
                                f"{maximum_allowed}x for "
                                f"{airport_code}."
                            ),
                        }
                    )

            # -----------------------------------------------------
            # High-risk approval check
            # -----------------------------------------------------

            if requested_multiplier >= 1.3:

                approval_required = True

                findings.append(
                    {
                        "rule": "high_risk_surge_approval",
                        "status": "approval_required",
                        "description": (
                            "Surge multipliers of 1.3x or higher "
                            "require explicit human approval."
                        ),
                    }
                )

            else:

                approval_required = False

                findings.append(
                    {
                        "rule": "high_risk_surge_approval",
                        "status": "no_approval_required",
                        "description": (
                            "Requested surge multiplier is below "
                            "the 1.3x high-risk threshold."
                        ),
                    }
                )

        else:
            approval_required = False

        # ---------------------------------------------------------
        # Determine overall compliance status
        # ---------------------------------------------------------

        has_violation = any(
            finding["status"] == "violation"
            for finding in findings
        )

        if has_violation:
            compliance_status = "blocked"

        elif approval_required:
            compliance_status = "approval_required"

        else:
            compliance_status = "compliant"

        # ---------------------------------------------------------
        # Return structured compliance result
        # ---------------------------------------------------------

        return {
            "agent": self.name,
            "status": "success",
            "airport_code": airport_code,
            "question": question,
            "compliance_status": compliance_status,
            "approval_required": approval_required,
            "findings": findings,
            "sources": relevant_sources,
            "retrieved_chunks": rag_result["results"],
            "policy_context": context,
        }


# -------------------------------------------------------------------
# Manual test
# -------------------------------------------------------------------

if __name__ == "__main__":

    import json

    print("\n" + "=" * 70)
    print("POLICY & COMPLIANCE AGENT TEST")
    print("=" * 70)

    agent = PolicyComplianceAgent()

    # ---------------------------------------------------------------
    # Test 1 — SFO 1.4x
    # ---------------------------------------------------------------

    print("\n" + "-" * 70)
    print("TEST 1: SFO 1.4x SURGE")
    print("-" * 70)

    result = agent.check_policy(
        question=(
            "What is the policy for surge pricing at SFO "
            "and does a 1.4x multiplier require approval?"
        ),
        airport_code="SFO",
        requested_multiplier=1.4
    )

    print(
        json.dumps(
            result,
            indent=2
        )
    )

    # ---------------------------------------------------------------
    # Test 2 — SFO above maximum
    # ---------------------------------------------------------------

    print("\n" + "-" * 70)
    print("TEST 2: SFO 1.6x SURGE")
    print("-" * 70)

    result = agent.check_policy(
        question=(
            "Can SFO use a 1.6x surge multiplier?"
        ),
        airport_code="SFO",
        requested_multiplier=1.6
    )

    print(
        json.dumps(
            result,
            indent=2
        )
    )

    # ---------------------------------------------------------------
    # Test 3 — JFK 1.3x
    # ---------------------------------------------------------------

    print("\n" + "-" * 70)
    print("TEST 3: JFK 1.3x SURGE")
    print("-" * 70)

    result = agent.check_policy(
        question=(
            "What approval is required for a 1.3x surge "
            "multiplier at JFK?"
        ),
        airport_code="JFK",
        requested_multiplier=1.3
    )

    print(
        json.dumps(
            result,
            indent=2
        )
    )

    print("\n" + "=" * 70)
    print("POLICY & COMPLIANCE AGENT TEST COMPLETED")
    print("=" * 70)
