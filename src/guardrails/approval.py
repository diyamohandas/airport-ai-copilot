from datetime import datetime


class HumanApproval:

    def request_approval(
        self,
        airport_code,
        action,
        risk_level,
        reason,
        requested_multiplier=None
    ):
        """
        Request explicit human approval for a high-risk action.

        This method does not execute the action.
        It only creates an approval request.
        """

        approval_request = {
            "approval_id": (
                f"APR-"
                f"{datetime.now().strftime('%Y%m%d%H%M%S')}"
            ),
            "timestamp": datetime.now().isoformat(),
            "airport_code": airport_code,
            "action": action,
            "risk_level": risk_level,
            "reason": reason,
            "requested_multiplier": requested_multiplier,
            "status": "pending",
            "approved_by": None
        }

        return approval_request

    def process_approval(
        self,
        approval_request,
        decision,
        approver="human_operator"
    ):
        """
        Process the human's approval decision.

        Valid decisions:
        - approve
        - reject
        """

        decision = str(decision).strip().lower()

        if decision not in {"approve", "reject"}:
            return {
                "status": "error",
                "message": (
                    "Invalid approval decision. "
                    "Use 'approve' or 'reject'."
                )
            }

        updated_request = approval_request.copy()

        if decision == "approve":
            updated_request["status"] = "approved"
            updated_request["approved_by"] = approver
            updated_request["approval_timestamp"] = (
                datetime.now().isoformat()
            )

        else:
            updated_request["status"] = "rejected"
            updated_request["approved_by"] = approver
            updated_request["approval_timestamp"] = (
                datetime.now().isoformat()
            )

        return updated_request


if __name__ == "__main__":

    print("=" * 70)
    print("HUMAN-IN-THE-LOOP APPROVAL TEST")
    print("=" * 70)

    approval = HumanApproval()

    # ---------------------------------------------------------
    # Create approval request
    # ---------------------------------------------------------

    request = approval.request_approval(
        airport_code="SFO",
        action="trigger_surge_override",
        risk_level="high",
        reason="Surge multiplier of 1.4x requires human approval.",
        requested_multiplier=1.4
    )

    print("\nApproval Request:")
    print(request)

    # ---------------------------------------------------------
    # Simulate human approval
    # ---------------------------------------------------------

    approved = approval.process_approval(
        approval_request=request,
        decision="approve",
        approver="airport_operations_manager"
    )

    print("\nAfter Human Approval:")
    print(approved)

    # ---------------------------------------------------------
    # Test rejection
    # ---------------------------------------------------------

    request_2 = approval.request_approval(
        airport_code="JFK",
        action="trigger_surge_override",
        risk_level="high",
        reason="Surge multiplier of 1.3x requires human approval.",
        requested_multiplier=1.3
    )

    rejected = approval.process_approval(
        approval_request=request_2,
        decision="reject",
        approver="airport_operations_manager"
    )

    print("\nAfter Human Rejection:")
    print(rejected)

    # ---------------------------------------------------------
    # Test invalid decision
    # ---------------------------------------------------------

    invalid = approval.process_approval(
        approval_request=request,
        decision="maybe"
    )

    print("\nInvalid Decision:")
    print(invalid)

    print("\n" + "=" * 70)
    print("HUMAN-IN-THE-LOOP APPROVAL TEST COMPLETED")
    print("=" * 70)
