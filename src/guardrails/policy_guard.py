from src.guardrails.risk_classifier import classify_risk


MAX_SURGE_MULTIPLIER = {
    "SFO": 1.5,
    "LAX": 1.6,
    "JFK": 1.5
}

HIGH_RISK_SURGE_THRESHOLD = 1.3


class PolicyGuard:
    """
    Enforces policy and risk decisions before an operational action
    can proceed.
    """

    def __init__(self):
        self.max_surge_multiplier = MAX_SURGE_MULTIPLIER

    def validate_action(
        self,
        airport_code,
        action,
        compliance_status="compliant",
        requested_multiplier=None
    ):
        """
        Validate an operational action against policy and risk rules.
        """

        airport_code = str(airport_code).strip().upper()
        action = str(action).strip().lower()
        compliance_status = str(compliance_status).strip().lower()

        findings = []

        # ---------------------------------------------------------
        # Validate airport
        # ---------------------------------------------------------
        if airport_code not in self.max_surge_multiplier:
            return {
                "status": "blocked",
                "compliance_status": "violation",
                "risk_level": "critical",
                "approval_required": False,
                "blocked": True,
                "findings": [
                    f"Unsupported airport code: {airport_code}"
                ]
            }

        # ---------------------------------------------------------
        # Policy violation from Policy Compliance Agent
        # ---------------------------------------------------------
        if compliance_status in {"violation", "blocked"}:

            findings.append(
                "Requested action violates the applicable policy."
            )

            return {
                "status": "blocked",
                "compliance_status": "violation",
                "risk_level": "critical",
                "approval_required": False,
                "blocked": True,
                "findings": findings
            }

        # ---------------------------------------------------------
        # Validate surge multiplier
        # ---------------------------------------------------------
        if requested_multiplier is not None:

            try:
                multiplier = float(requested_multiplier)
            except (TypeError, ValueError):

                return {
                    "status": "blocked",
                    "compliance_status": "violation",
                    "risk_level": "critical",
                    "approval_required": False,
                    "blocked": True,
                    "findings": [
                        "Requested surge multiplier is invalid."
                    ]
                }

            maximum = self.max_surge_multiplier[airport_code]

            # Above airport maximum
            if multiplier > maximum:

                findings.append(
                    f"Requested surge {multiplier}x exceeds "
                    f"{airport_code} maximum of {maximum}x."
                )

                return {
                    "status": "blocked",
                    "compliance_status": "violation",
                    "risk_level": "critical",
                    "approval_required": False,
                    "blocked": True,
                    "requested_multiplier": multiplier,
                    "maximum_allowed": maximum,
                    "findings": findings
                }

            # High-risk surge
            if multiplier >= HIGH_RISK_SURGE_THRESHOLD:

                risk_result = classify_risk(
                    action=action,
                    requested_multiplier=multiplier,
                    compliance_status=compliance_status
                )

                findings.append(
                    f"Surge {multiplier}x requires human approval."
                )

                return {
                    "status": "approval_required",
                    "compliance_status": "compliant",
                    "risk_level": risk_result["risk_level"],
                    "approval_required": True,
                    "blocked": False,
                    "requested_multiplier": multiplier,
                    "maximum_allowed": maximum,
                    "findings": findings
                }

        # ---------------------------------------------------------
        # Normal / low-risk action
        # ---------------------------------------------------------
        risk_result = classify_risk(
            action=action,
            requested_multiplier=requested_multiplier,
            compliance_status=compliance_status
        )

        return {
            "status": "approved_for_next_step",
            "compliance_status": "compliant",
            "risk_level": risk_result["risk_level"],
            "approval_required": risk_result["approval_required"],
            "blocked": risk_result["blocked"],
            "findings": [
                "Action passed policy validation."
            ]
        }


if __name__ == "__main__":

    print("=" * 70)
    print("POLICY GUARD TEST")
    print("=" * 70)

    guard = PolicyGuard()

    test_cases = [
        {
            "name": "Normal metrics request",
            "airport_code": "SFO",
            "action": "get_airport_metrics",
            "compliance_status": "compliant",
            "requested_multiplier": None
        },
        {
            "name": "Low surge",
            "airport_code": "SFO",
            "action": "trigger_surge_override",
            "compliance_status": "compliant",
            "requested_multiplier": 1.2
        },
        {
            "name": "High-risk surge",
            "airport_code": "SFO",
            "action": "trigger_surge_override",
            "compliance_status": "compliant",
            "requested_multiplier": 1.4
        },
        {
            "name": "Surge above policy maximum",
            "airport_code": "SFO",
            "action": "trigger_surge_override",
            "compliance_status": "compliant",
            "requested_multiplier": 1.6
        },
        {
            "name": "Explicit policy violation",
            "airport_code": "JFK",
            "action": "trigger_surge_override",
            "compliance_status": "violation",
            "requested_multiplier": 1.3
        }
    ]

    for i, test in enumerate(test_cases, start=1):

        print(f"\nTest {i}: {test['name']}")
        print("-" * 50)

        result = guard.validate_action(
            airport_code=test["airport_code"],
            action=test["action"],
            compliance_status=test["compliance_status"],
            requested_multiplier=test["requested_multiplier"]
        )

        print(result)

    print("\n" + "=" * 70)
    print("POLICY GUARD TEST COMPLETED")
    print("=" * 70)
