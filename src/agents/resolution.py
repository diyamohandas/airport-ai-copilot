from src.tools import (
    calculate_driver_incentive,
    trigger_surge_override,
)


class ResolutionAgent:
    """
    Resolution Agent

    Combines operational findings and policy/compliance results
    to recommend an appropriate action.

    High-risk actions are never executed automatically.
    """

    def __init__(self):
        self.agent_name = "Resolution Agent"

    def recommend(self, investigation_result, compliance_result):
        airport_code = investigation_result.get("airport_code")

        findings = investigation_result.get("findings", [])
        operational_status = investigation_result.get("overall_status")

        compliance_status = compliance_result.get("compliance_status")
        approval_required = compliance_result.get("approval_required", False)

        recommendations = []

        # ---------------------------------------------------------
        # CASE 1: POLICY VIOLATION
        # ---------------------------------------------------------
        if compliance_status == "blocked":
            recommendations.append({
                "action": "block_requested_action",
                "priority": "high",
                "reason": (
                    "The requested action violates the applicable "
                    "airport policy and must not be executed."
                ),
                "execution_allowed": False,
            })

            return {
                "agent": self.agent_name,
                "status": "success",
                "airport_code": airport_code,
                "operational_status": operational_status,
                "compliance_status": compliance_status,
                "approval_required": True,
                "recommendations": recommendations,
                "recommended_action": "block_requested_action",
            }

        # ---------------------------------------------------------
        # CASE 2: HIGH-RISK SURGE REQUIRING APPROVAL
        # ---------------------------------------------------------
        if compliance_status == "approval_required":
            recommendations.append({
                "action": "request_human_approval",
                "priority": "high",
                "reason": (
                    "The proposed surge change is within the permitted "
                    "limit but requires explicit human approval."
                ),
                "execution_allowed": False,
            })

            return {
                "agent": self.agent_name,
                "status": "success",
                "airport_code": airport_code,
                "operational_status": operational_status,
                "compliance_status": compliance_status,
                "approval_required": True,
                "recommendations": recommendations,
                "recommended_action": "request_human_approval",
            }

        # ---------------------------------------------------------
        # CASE 3: OPERATIONAL PROBLEM
        # ---------------------------------------------------------
        high_severity_findings = [
            finding
            for finding in findings
            if finding.get("severity") in {"high", "critical"}
        ]

        if high_severity_findings:
            # Estimate an incentive based on driver availability.
            metrics = investigation_result.get("metrics", {})
            driver_count = metrics.get("active_drivers", 0)

            incentive_result = calculate_driver_incentive(
                driver_count=driver_count,
                severity_level="high",
            )

            recommendations.append({
                "action": "driver_incentive",
                "priority": "high",
                "reason": (
                    "Operational metrics show significant service pressure. "
                    "A driver incentive is recommended to improve available supply."
                ),
                "tool_result": incentive_result,
                "execution_allowed": True,
            })

            return {
                "agent": self.agent_name,
                "status": "success",
                "airport_code": airport_code,
                "operational_status": operational_status,
                "compliance_status": compliance_status,
                "approval_required": False,
                "recommendations": recommendations,
                "recommended_action": "driver_incentive",
            }

        # ---------------------------------------------------------
        # CASE 4: NO SIGNIFICANT ISSUE
        # ---------------------------------------------------------
        recommendations.append({
            "action": "monitor",
            "priority": "low",
            "reason": (
                "No high-severity operational issue or policy violation "
                "was identified."
            ),
            "execution_allowed": True,
        })

        return {
            "agent": self.agent_name,
            "status": "success",
            "airport_code": airport_code,
            "operational_status": operational_status,
            "compliance_status": compliance_status,
            "approval_required": False,
            "recommendations": recommendations,
            "recommended_action": "monitor",
        }


def print_result(result):
    import json

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    print("=" * 70)
    print("RESOLUTION AGENT TEST")
    print("=" * 70)

    investigator_result = {
        "agent": "Operations Investigator",
        "status": "success",
        "airport_code": "SFO",
        "overall_status": "high_risk",
        "metrics": {
            "completion_rate": 72,
            "average_eta": 21,
            "active_drivers": 350,
            "cancellation_rate": 15,
            "queue_size": 68,
            "surge_multiplier": 1.4,
            "request_volume": 720,
        },
        "findings": [
            {
                "metric": "completion_rate",
                "value": 72,
                "severity": "high",
                "description": "Completion rate is below 75%.",
            },
            {
                "metric": "average_eta",
                "value": 21,
                "severity": "high",
                "description": "Average ETA is above 20 minutes.",
            },
            {
                "metric": "cancellation_rate",
                "value": 15,
                "severity": "high",
                "description": "Cancellation rate is above 10%.",
            },
        ],
    }

    compliance_result = {
        "agent": "Policy & Compliance Agent",
        "status": "success",
        "airport_code": "SFO",
        "compliance_status": "approval_required",
        "approval_required": True,
        "findings": [
            {
                "rule": "maximum_surge_limit",
                "status": "compliant",
                "description": "Requested surge is within the permitted maximum.",
            },
            {
                "rule": "high_risk_surge_approval",
                "status": "approval_required",
                "description": "Surge of 1.3x or higher requires human approval.",
            },
        ],
    }

    agent = ResolutionAgent()

    result = agent.recommend(
        investigation_result=investigator_result,
        compliance_result=compliance_result,
    )

    print_result(result)

    print("=" * 70)
    print("RESOLUTION AGENT TEST COMPLETED")
    print("=" * 70)
