import json
from datetime import datetime
from pathlib import Path


AUDIT_PATH = Path("data/audit/audit_trail.jsonl")


class AuditTrail:
    """
    Stores operational decisions and actions as JSONL records.
    """

    def __init__(self, audit_path=AUDIT_PATH):
        self.audit_path = Path(audit_path)

        # Create the parent directory if it does not exist
        self.audit_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

    def log_event(
        self,
        event_type,
        query=None,
        airport_code=None,
        action=None,
        risk_level=None,
        policy_status=None,
        approval_status=None,
        execution_status=None,
        details=None
    ):
        """
        Write one event to the JSONL audit trail.
        """

        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "query": query,
            "airport_code": airport_code,
            "action": action,
            "risk_level": risk_level,
            "policy_status": policy_status,
            "approval_status": approval_status,
            "execution_status": execution_status,
            "details": details or {}
        }

        with self.audit_path.open(
            "a",
            encoding="utf-8"
        ) as file:

            file.write(
                json.dumps(
                    event,
                    ensure_ascii=False
                ) + "\n"
            )

        return event

    def read_events(self):
        """
        Read all audit events.
        """

        if not self.audit_path.exists():
            return []

        events = []

        with self.audit_path.open(
            "r",
            encoding="utf-8"
        ) as file:

            for line in file:

                line = line.strip()

                if not line:
                    continue

                try:
                    events.append(
                        json.loads(line)
                    )

                except json.JSONDecodeError:
                    continue

        return events


if __name__ == "__main__":

    print("=" * 70)
    print("AUDIT TRAIL TEST")
    print("=" * 70)

    audit = AuditTrail()

    # ---------------------------------------------------------
    # Event 1: User request
    # ---------------------------------------------------------

    event_1 = audit.log_event(
        event_type="user_request",
        query="Increase SFO surge to 1.4x",
        airport_code="SFO",
        action="trigger_surge_override",
        details={
            "source": "test"
        }
    )

    print("\nEvent 1:")
    print(event_1)

    # ---------------------------------------------------------
    # Event 2: Policy decision
    # ---------------------------------------------------------

    event_2 = audit.log_event(
        event_type="policy_check",
        query="Increase SFO surge to 1.4x",
        airport_code="SFO",
        action="trigger_surge_override",
        risk_level="high",
        policy_status="compliant",
        approval_status="required",
        details={
            "requested_multiplier": 1.4,
            "maximum_allowed": 1.5
        }
    )

    print("\nEvent 2:")
    print(event_2)

    # ---------------------------------------------------------
    # Event 3: Human approval
    # ---------------------------------------------------------

    event_3 = audit.log_event(
        event_type="human_approval",
        query="Increase SFO surge to 1.4x",
        airport_code="SFO",
        action="trigger_surge_override",
        risk_level="high",
        policy_status="compliant",
        approval_status="approved",
        execution_status="pending",
        details={
            "approved_by": "airport_operations_manager"
        }
    )

    print("\nEvent 3:")
    print(event_3)

    # ---------------------------------------------------------
    # Read audit trail
    # ---------------------------------------------------------

    events = audit.read_events()

    print("\nTotal audit events:", len(events))

    print("\nAudit Trail:")
    for event in events:
        print(json.dumps(event, indent=2))

    print("\n" + "=" * 70)
    print("AUDIT TRAIL TEST COMPLETED")
    print("=" * 70)
