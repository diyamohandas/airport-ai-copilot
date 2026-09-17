import json

from src.agents.operations_investigator import OperationsInvestigator
from src.agents.policy_compliance import PolicyComplianceAgent
from src.agents.resolution import ResolutionAgent


class AirportOperationsOrchestrator:
    """
    Coordinates the Airport Operations AI Copilot agents.

    Workflow:
        User Query
            ↓
        Operations Investigator
            ↓
        Policy & Compliance
            ↓
        Resolution
            ↓
        Final Recommendation
    """

    def __init__(self):
        self.operations_agent = OperationsInvestigator()
        self.policy_agent = PolicyComplianceAgent()
        self.resolution_agent = ResolutionAgent()

    def extract_airport_code(self, query):
        """
        Extract airport code from the user query.
        """

        query_upper = query.upper()

        for airport in ["SFO", "LAX", "JFK"]:
            if airport in query_upper:
                return airport

        return None

    def extract_surge_multiplier(self, query):
        """
        Extract a surge multiplier such as 1.3x or 1.5x.
        """

        import re

        match = re.search(r"(\d+(?:\.\d+)?)\s*x", query.lower())

        if match:
            return float(match.group(1))

        return None

    def run(self, query):
        """
        Execute the complete agentic workflow.
        """

        # ---------------------------------------------------------
        # STEP 1: Understand the request
        # ---------------------------------------------------------

        airport_code = self.extract_airport_code(query)
        requested_multiplier = self.extract_surge_multiplier(query)

        if airport_code is None:
            return {
                "status": "error",
                "message": (
                    "Could not identify an airport. "
                    "Please specify SFO, LAX, or JFK."
                ),
            }

        # ---------------------------------------------------------
        # STEP 2: Investigate operational conditions
        # ---------------------------------------------------------

        investigation_result = self.operations_agent.investigate(
            airport_code
        )

        if investigation_result.get("status") != "success":
            return {
                "status": "error",
                "stage": "operations_investigation",
                "result": investigation_result,
            }

        # ---------------------------------------------------------
        # STEP 3: Check policy and compliance
        # ---------------------------------------------------------

        policy_question = query

        compliance_result = self.policy_agent.check_policy(
            question=policy_question,
            airport_code=airport_code,
            requested_multiplier=requested_multiplier,
        )

        if compliance_result.get("status") != "success":
            return {
                "status": "error",
                "stage": "policy_compliance",
                "result": compliance_result,
            }

        # ---------------------------------------------------------
        # STEP 4: Generate resolution
        # ---------------------------------------------------------

        resolution_result = self.resolution_agent.recommend(
            investigation_result=investigation_result,
            compliance_result=compliance_result,
        )

        if resolution_result.get("status") != "success":
            return {
                "status": "error",
                "stage": "resolution",
                "result": resolution_result,
            }

        # ---------------------------------------------------------
        # STEP 5: Build final response
        # ---------------------------------------------------------

        return {
            "status": "success",
            "query": query,
            "airport_code": airport_code,
            "requested_multiplier": requested_multiplier,
            "investigation": investigation_result,
            "compliance": compliance_result,
            "resolution": resolution_result,
        }


def print_result(result):
    print(json.dumps(result, indent=2))


if __name__ == "__main__":

    print("=" * 70)
    print("AIRPORT OPERATIONS ORCHESTRATOR TEST")
    print("=" * 70)

    orchestrator = AirportOperationsOrchestrator()

    query = (
        "SFO operations are experiencing high cancellations and queue size. "
        "Can we increase surge pricing to 1.4x?"
    )

    result = orchestrator.run(query)

    print_result(result)

    print("=" * 70)
    print("ORCHESTRATOR TEST COMPLETED")
    print("=" * 70)
