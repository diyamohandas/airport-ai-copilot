from typing import Any, Dict

from src.tools import get_airport_metrics


class OperationsInvestigator:
    """
    Investigates airport operational conditions using
    the operational metrics tool.
    """

    def __init__(self):
        self.name = "Operations Investigator"

    def investigate(
        self,
        airport_code: str
    ) -> Dict[str, Any]:
        """
        Retrieve the latest airport metrics and identify
        important operational signals.
        """

        # ---------------------------------------------------------
        # Retrieve operational data
        # ---------------------------------------------------------

        metrics = get_airport_metrics(airport_code)

        if metrics.get("status") != "success":
            return {
                "agent": self.name,
                "status": "error",
                "airport_code": airport_code,
                "metrics": metrics,
                "findings": [],
            }

        # ---------------------------------------------------------
        # Extract metrics
        # ---------------------------------------------------------

        completion_rate = metrics["completion_rate"]
        average_eta = metrics["average_eta"]
        active_drivers = metrics["active_drivers"]
        cancellation_rate = metrics["cancellation_rate"]
        queue_size = metrics["queue_size"]
        surge_multiplier = metrics["surge_multiplier"]
        request_volume = metrics["request_volume"]

        findings = []

        # ---------------------------------------------------------
        # Identify operational signals
        # These thresholds are synthetic project rules.
        # ---------------------------------------------------------

        if completion_rate < 75:
            findings.append(
                {
                    "metric": "completion_rate",
                    "value": completion_rate,
                    "signal": "low",
                    "description": (
                        "Completion rate is below the "
                        "75% investigation threshold."
                    ),
                }
            )

        if average_eta > 20:
            findings.append(
                {
                    "metric": "average_eta",
                    "value": average_eta,
                    "signal": "high",
                    "description": (
                        "Average ETA is above the "
                        "20-minute investigation threshold."
                    ),
                }
            )

        if cancellation_rate > 10:
            findings.append(
                {
                    "metric": "cancellation_rate",
                    "value": cancellation_rate,
                    "signal": "high",
                    "description": (
                        "Cancellation rate is above the "
                        "10% investigation threshold."
                    ),
                }
            )

        if queue_size > 50:
            findings.append(
                {
                    "metric": "queue_size",
                    "value": queue_size,
                    "signal": "high",
                    "description": (
                        "Queue size is above the "
                        "50-unit investigation threshold."
                    ),
                }
            )

        if surge_multiplier >= 1.3:
            findings.append(
                {
                    "metric": "surge_multiplier",
                    "value": surge_multiplier,
                    "signal": "high_risk",
                    "description": (
                        "Surge multiplier is at or above "
                        "the 1.3x high-risk threshold."
                    ),
                }
            )

        # ---------------------------------------------------------
        # Overall status
        # ---------------------------------------------------------

        if len(findings) == 0:
            overall_status = "normal"
        elif any(
            finding["signal"] == "high_risk"
            for finding in findings
        ):
            overall_status = "high_risk"
        else:
            overall_status = "attention_required"

        # ---------------------------------------------------------
        # Return structured investigation
        # ---------------------------------------------------------

        return {
            "agent": self.name,
            "status": "success",
            "airport_code": metrics["airport_code"],
            "timestamp": metrics["timestamp"],
            "metrics": {
                "completion_rate": completion_rate,
                "average_eta": average_eta,
                "active_drivers": active_drivers,
                "cancellation_rate": cancellation_rate,
                "queue_size": queue_size,
                "surge_multiplier": surge_multiplier,
                "request_volume": request_volume,
            },
            "overall_status": overall_status,
            "findings": findings,
        }


# -------------------------------------------------------------------
# Manual test
# -------------------------------------------------------------------

if __name__ == "__main__":

    import json

    print("\n" + "=" * 70)
    print("OPERATIONS INVESTIGATOR TEST")
    print("=" * 70)

    investigator = OperationsInvestigator()

    result = investigator.investigate("SFO")

    print("\nInvestigation Result:")

    print(
        json.dumps(
            result,
            indent=2
        )
    )

    print("\n" + "=" * 70)
    print("OPERATIONS INVESTIGATOR TEST COMPLETED")
    print("=" * 70)
