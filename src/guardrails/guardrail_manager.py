from src.guardrails.validation import validate_query, validate_airport_code
from src.guardrails.risk_classifier import classify_risk
from src.guardrails.policy_guard import PolicyGuard
from src.guardrails.approval import HumanApproval
from src.guardrails.audit import AuditTrail


class GuardrailManager:
    """
    Central coordinator for all Day 4 guardrails.

    Workflow:
        Input Validation
        -> Policy Guard
        -> Risk Classification
        -> Human Approval
        -> Execution Decision
        -> Audit
    """

    def __init__(self):
        self.policy_guard = PolicyGuard()
        self.approval = HumanApproval()
        self.audit = AuditTrail()

    def evaluate_request(
        self,
        query,
        airport_code,
        action,
        compliance_status="compliant",
        requested_multiplier=None
    ):
        """
        Evaluate an operational request before execution.
        """

        # ---------------------------------------------------------
        # STEP 1: Validate query
        # ---------------------------------------------------------

        query_result = validate_query(query)

        if not query_result["valid"]:

            self.audit.log_event(
                event_type="validation_failed",
                query=query,
                airport_code=airport_code,
                action=action,
                details={
                    "errors": query_result["errors"]
                }
            )

            return {
                "status": "blocked",
                "stage": "input_validation",
                "blocked": True,
                "approval_required": False,
                "reason": "Input validation failed.",
                "errors": query_result["errors"]
            }

        # ---------------------------------------------------------
        # STEP 2: Validate airport
        # ---------------------------------------------------------

        airport_result = validate_airport_code(
            airport_code
        )

        if not airport_result["valid"]:

            self.audit.log_event(
                event_type="airport_validation_failed",
                query=query,
                airport_code=airport_code,
                action=action,
                details={
                    "error": airport_result["error"]
                }
            )

            return {
                "status": "blocked",
                "stage": "airport_validation",
                "blocked": True,
                "approval_required": False,
                "reason": airport_result["error"]
            }

        airport_code = airport_result["airport_code"]

        # ---------------------------------------------------------
        # STEP 3: Policy Guard
        # ---------------------------------------------------------

        policy_result = self.policy_guard.validate_action(
            airport_code=airport_code,
            action=action,
            compliance_status=compliance_status,
            requested_multiplier=requested_multiplier
        )

        # ---------------------------------------------------------
        # STEP 4: Audit policy decision
        # ---------------------------------------------------------

        self.audit.log_event(
            event_type="policy_check",
            query=query,
            airport_code=airport_code,
            action=action,
            risk_level=policy_result.get("risk_level"),
            policy_status=policy_result.get(
                "compliance_status"
            ),
            approval_status=(
                "required"
                if policy_result.get("approval_required")
                else "not_required"
            ),
            details={
                "findings": policy_result.get(
                    "findings", []
                ),
                "requested_multiplier": requested_multiplier
            }
        )

        # ---------------------------------------------------------
        # STEP 5: BLOCK policy violations
        # ---------------------------------------------------------

        if policy_result.get("blocked"):

            self.audit.log_event(
                event_type="action_blocked",
                query=query,
                airport_code=airport_code,
                action=action,
                risk_level=policy_result.get(
                    "risk_level"
                ),
                policy_status="violation",
                execution_status="blocked",
                details={
                    "reason": policy_result.get(
                        "findings", []
                    )
                }
            )

            return {
                "status": "blocked",
                "stage": "policy_guard",
                "blocked": True,
                "approval_required": False,
                "risk_level": policy_result.get(
                    "risk_level"
                ),
                "policy_result": policy_result,
                "reason": "Action blocked by policy guard."
            }

        # ---------------------------------------------------------
        # STEP 6: Human approval for high-risk action
        # ---------------------------------------------------------

        if policy_result.get("approval_required"):

            approval_request = self.approval.request_approval(
                airport_code=airport_code,
                action=action,
                risk_level=policy_result.get(
                    "risk_level"
                ),
                reason="High-risk action requires human approval.",
                requested_multiplier=requested_multiplier
            )

            self.audit.log_event(
                event_type="approval_requested",
                query=query,
                airport_code=airport_code,
                action=action,
                risk_level=policy_result.get(
                    "risk_level"
                ),
                policy_status=policy_result.get(
                    "compliance_status"
                ),
                approval_status="pending",
                execution_status="pending",
                details={
                    "approval_id": approval_request[
                        "approval_id"
                    ],
                    "reason": approval_request[
                        "reason"
                    ]
                }
            )

            return {
                "status": "approval_required",
                "stage": "human_approval",
                "blocked": False,
                "approval_required": True,
                "risk_level": policy_result.get(
                    "risk_level"
                ),
                "policy_result": policy_result,
                "approval_request": approval_request
            }

        # ---------------------------------------------------------
        # STEP 7: Safe action can continue
        # ---------------------------------------------------------

        self.audit.log_event(
            event_type="action_validated",
            query=query,
            airport_code=airport_code,
            action=action,
            risk_level=policy_result.get(
                "risk_level"
            ),
            policy_status=policy_result.get(
                "compliance_status"
            ),
            approval_status="not_required",
            execution_status="ready",
            details={
                "message": "Action passed guardrails."
            }
        )

        return {
            "status": "approved_for_execution",
            "stage": "execution",
            "blocked": False,
            "approval_required": False,
            "risk_level": policy_result.get(
                "risk_level"
            ),
            "policy_result": policy_result,
            "message": "Action passed all guardrails."
        }

    def process_human_decision(
        self,
        approval_request,
        decision,
        query=None
    ):
        """
        Process an explicit human approval/rejection.
        """

        result = self.approval.process_approval(
            approval_request=approval_request,
            decision=decision,
            approver="airport_operations_manager"
        )

        if result.get("status") == "approved":

            execution_status = "approved"

        elif result.get("status") == "rejected":

            execution_status = "rejected"

        else:

            execution_status = "error"

        self.audit.log_event(
            event_type="human_approval_decision",
            query=query,
            airport_code=approval_request.get(
                "airport_code"
            ),
            action=approval_request.get(
                "action"
            ),
            risk_level=approval_request.get(
                "risk_level"
            ),
            approval_status=result.get(
                "status"
            ),
            execution_status=execution_status,
            details={
                "approval_id": approval_request.get(
                    "approval_id"
                ),
                "approved_by": result.get(
                    "approved_by"
                )
            }
        )

        return result


if __name__ == "__main__":

    print("=" * 70)
    print("GUARDRAIL MANAGER END-TO-END TEST")
    print("=" * 70)

    manager = GuardrailManager()

    # =========================================================
    # TEST 1: Normal request
    # =========================================================

    print("\nTEST 1: Normal Metrics Request")
    print("-" * 50)

    result_1 = manager.evaluate_request(
        query="What are the latest SFO metrics?",
        airport_code="SFO",
        action="get_airport_metrics"
    )

    print(result_1)

    # =========================================================
    # TEST 2: High-risk request
    # =========================================================

    print("\nTEST 2: High-Risk Surge Request")
    print("-" * 50)

    result_2 = manager.evaluate_request(
        query="Increase SFO surge to 1.4x",
        airport_code="SFO",
        action="trigger_surge_override",
        requested_multiplier=1.4
    )

    print(result_2)

    # =========================================================
    # TEST 3: Policy violation
    # =========================================================

    print("\nTEST 3: Policy Violation")
    print("-" * 50)

    result_3 = manager.evaluate_request(
        query="Increase SFO surge to 1.6x",
        airport_code="SFO",
        action="trigger_surge_override",
        requested_multiplier=1.6
    )

    print(result_3)

    # =========================================================
    # TEST 4: Human approval
    # =========================================================

    if result_2.get("approval_required"):

        print("\nTEST 4: Human Approval")
        print("-" * 50)

        approval_result = manager.process_human_decision(
            approval_request=result_2[
                "approval_request"
            ],
            decision="approve",
            query="Increase SFO surge to 1.4x"
        )

        print(approval_result)

    print("\n" + "=" * 70)
    print("GUARDRAIL MANAGER TEST COMPLETED")
    print("=" * 70)
