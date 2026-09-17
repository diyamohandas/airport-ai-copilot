import json

from src.agents.orchestrator import AirportOperationsOrchestrator
from src.memory import ConversationMemory


class ReActAgent:
    """
    ReAct-style agent for the Airport Operations AI Copilot.

    Workflow:
        Thought
            ↓
        Action
            ↓
        Observation
            ↓
        Thought
            ↓
        Final Action

    The maximum number of iterations is limited to 5.
    """

    MAX_ITERATIONS = 5

    def __init__(self):
        self.orchestrator = AirportOperationsOrchestrator()
        self.memory = ConversationMemory()

    def run(self, query):
        """
        Run the ReAct workflow for a user query.
        """

        trace = []

        # =========================================================
        # ITERATION 1 — UNDERSTAND THE REQUEST
        # =========================================================

        # Store the user query in short-term memory.
        self.memory.add_message(
            role="user",
            content=query
        )

        # Identify the airport from the query.
        airport_code = self.orchestrator.extract_airport_code(
            query
        )

        # Retrieve any previous long-term memories
        # associated with this airport.
        previous_memories = []

        if airport_code:
            previous_memories = (
                self.memory.get_long_term_memory(
                    airport_code
                )
            )

        trace.append({
            "iteration": 1,
            "type": "thought",
            "content": (
                "I identified the airport and checked "
                "whether previous operational memories "
                "are available."
            )
        })

        # =========================================================
        # VALIDATE AIRPORT
        # =========================================================

        if airport_code is None:

            error_response = {
                "status": "error",
                "query": query,
                "message": (
                    "Could not identify an airport. "
                    "Please specify SFO, LAX, or JFK."
                ),
                "iterations": len(trace),
                "max_iterations": self.MAX_ITERATIONS,
                "trace": trace,
            }

            self.memory.add_message(
                role="assistant",
                content=json.dumps(error_response)
            )

            return error_response

        # =========================================================
        # ITERATION 2 — ACTION / INVESTIGATION
        # =========================================================

        trace.append({
            "iteration": 2,
            "type": "action",
            "tool": "AirportOperationsOrchestrator",
            "content": (
                "Investigating current airport operational "
                "metrics and applicable policies."
            )
        })

        # Run the complete orchestrator.
        result = self.orchestrator.run(query)

        # Handle orchestrator errors.
        if result.get("status") != "success":

            error_response = {
                "status": "error",
                "query": query,
                "airport_code": airport_code,
                "iterations": len(trace),
                "max_iterations": self.MAX_ITERATIONS,
                "trace": trace,
                "result": result,
            }

            self.memory.add_message(
                role="assistant",
                content=json.dumps(error_response)
            )

            return error_response

        # =========================================================
        # ITERATION 3 — OBSERVATION
        # =========================================================

        investigation = result.get(
            "investigation",
            {}
        )

        compliance = result.get(
            "compliance",
            {}
        )

        resolution = result.get(
            "resolution",
            {}
        )

        operational_status = investigation.get(
            "overall_status"
        )

        compliance_status = compliance.get(
            "compliance_status"
        )

        recommended_action = resolution.get(
            "recommended_action"
        )

        trace.append({
            "iteration": 3,
            "type": "observation",
            "content": (
                f"Operational status: "
                f"{operational_status}; "
                f"Compliance status: "
                f"{compliance_status}; "
                f"Recommended action: "
                f"{recommended_action}."
            )
        })

        # =========================================================
        # ITERATION 4 — REASONING
        # =========================================================

        trace.append({
            "iteration": 4,
            "type": "thought",
            "content": (
                "I have enough operational and policy "
                "information to determine the appropriate "
                "resolution. High-risk or policy-sensitive "
                "actions must not be executed without "
                "the required approval."
            )
        })

        # =========================================================
        # ITERATION 5 — FINAL ACTION
        # =========================================================

        trace.append({
            "iteration": 5,
            "type": "action",
            "content": (
                f"Final recommendation: "
                f"{recommended_action}"
            )
        })

        # =========================================================
        # FINAL RESPONSE
        # =========================================================

        final_response = {
            "status": "success",
            "query": query,
            "airport_code": airport_code,
            "iterations": 5,
            "max_iterations": self.MAX_ITERATIONS,
            "previous_memories": previous_memories,
            "trace": trace,
            "result": result,
        }

        # =========================================================
        # SHORT-TERM MEMORY
        # =========================================================

        self.memory.add_message(
            role="assistant",
            content=json.dumps(final_response)
        )

        # =========================================================
        # LONG-TERM MEMORY
        # =========================================================

        self.memory.add_long_term_memory(
            airport_code=airport_code,
            memory_type="agent_decision",
            content=(
                f"Query: {query} | "
                f"Recommended action: "
                f"{recommended_action} | "
                f"Compliance status: "
                f"{compliance_status}"
            )
        )

        return final_response


def print_result(result):
    """
    Pretty-print the result.
    """

    print(
        json.dumps(
            result,
            indent=2
        )
    )


# =============================================================
# TEST
# =============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("REACT AGENT WITH MEMORY TEST")
    print("=" * 70)

    agent = ReActAgent()

    query = (
        "SFO operations are experiencing high cancellations "
        "and large queues. Can we increase surge pricing "
        "to 1.4x?"
    )

    result = agent.run(query)

    print_result(result)

    print("=" * 70)
    print("REACT AGENT WITH MEMORY TEST COMPLETED")
    print("=" * 70)
