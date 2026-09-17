HIGH_RISK_SURGE_THRESHOLD = 1.3

VALID_RISK_LEVELS = {
    "low",
    "medium",
    "high",
    "critical"
}


def classify_risk(
    action,
    requested_multiplier=None,
    compliance_status="compliant"
):
    """
    Classify the risk level of an operational action.

    Rules:
    - Policy violations are CRITICAL.
    - Surge >= 1.3x is HIGH risk.
    - Sensitive operational actions are HIGH risk.
    - Normal monitoring/incentive actions are LOW risk.
    """

    action = str(action).strip().lower()
    compliance_status = str(compliance_status).strip().lower()

    # ---------------------------------------------------------
    # Rule 1: Policy violations are critical
    # ---------------------------------------------------------
    if compliance_status in {"violation", "blocked"}:
        return {
            "risk_level": "critical",
            "approval_required": False,
            "blocked": True,
            "reason": "The requested action violates policy."
        }

    # ---------------------------------------------------------
    # Rule 2: Surge >= 1.3x requires human approval
    # ---------------------------------------------------------
    if requested_multiplier is not None:
        try:
            multiplier = float(requested_multiplier)

            if multiplier >= HIGH_RISK_SURGE_THRESHOLD:
                return {
                    "risk_level": "high",
                    "approval_required": True,
                    "blocked": False,
                    "reason": (
                        f"Surge multiplier {multiplier}x meets or exceeds "
                        f"the high-risk threshold of "
                        f"{HIGH_RISK_SURGE_THRESHOLD}x."
                    )
                }

        except (TypeError, ValueError):
            return {
                "risk_level": "critical",
                "approval_required": False,
                "blocked": True,
                "reason": "Invalid surge multiplier."
            }

    # ---------------------------------------------------------
    # Rule 3: Sensitive operational actions
    # ---------------------------------------------------------
    high_risk_actions = {
        "trigger_surge_override",
        "surge_override",
        "change_surge",
        "modify_pricing",
        "pricing_override"
    }

    if action in high_risk_actions:
        return {
            "risk_level": "high",
            "approval_required": True,
            "blocked": False,
            "reason": "This is a sensitive operational action."
        }

    # ---------------------------------------------------------
    # Rule 4: Medium-risk actions
    # ---------------------------------------------------------
    medium_risk_actions = {
        "calculate_driver_incentive",
        "driver_incentive",
        "increase_incentive"
    }

    if action in medium_risk_actions:
        return {
            "risk_level": "medium",
            "approval_required": False,
            "blocked": False,
            "reason": "This action affects operational incentives."
        }

    # ---------------------------------------------------------
    # Rule 5: Normal actions
    # ---------------------------------------------------------
    low_risk_actions = {
        "get_airport_metrics",
        "monitor",
        "retrieve_policy",
        "investigate",
        "analyze"
    }

    if action in low_risk_actions:
        return {
            "risk_level": "low",
            "approval_required": False,
            "blocked": False,
            "reason": "This is a read-only or analytical action."
        }

    # ---------------------------------------------------------
    # Default
    # ---------------------------------------------------------
    return {
        "risk_level": "medium",
        "approval_required": False,
        "blocked": False,
        "reason": "Action does not match a predefined high-risk rule."
    }


if __name__ == "__main__":

    print("=" * 70)
    print("RISK CLASSIFIER TEST")
    print("=" * 70)

    test_cases = [
        {
            "action": "get_airport_metrics",
            "requested_multiplier": None,
            "compliance_status": "compliant"
        },
        {
            "action": "calculate_driver_incentive",
            "requested_multiplier": None,
            "compliance_status": "compliant"
        },
        {
            "action": "trigger_surge_override",
            "requested_multiplier": 1.2,
            "compliance_status": "compliant"
        },
        {
            "action": "trigger_surge_override",
            "requested_multiplier": 1.4,
            "compliance_status": "compliant"
        },
        {
            "action": "trigger_surge_override",
            "requested_multiplier": 1.6,
            "compliance_status": "blocked"
        }
    ]

    for i, test in enumerate(test_cases, start=1):

        result = classify_risk(
            action=test["action"],
            requested_multiplier=test["requested_multiplier"],
            compliance_status=test["compliance_status"]
        )

        print(f"\nTest {i}")
        print("-" * 40)
        print("Input:", test)
        print("Result:", result)

    print("\n" + "=" * 70)
    print("RISK CLASSIFIER TEST COMPLETED")
    print("=" * 70)
