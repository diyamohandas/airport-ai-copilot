import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

DATA_PATH = "data/operational/airport_metrics.csv"

VALID_AIRPORTS = {"SFO", "LAX", "JFK"}

VALID_SEVERITY_LEVELS = {
    "low",
    "medium",
    "high",
    "critical"
}

# Synthetic project limits based on the Day 1 policy documents
MAX_SURGE_MULTIPLIER = {
    "SFO": 1.5,
    "LAX": 1.6,
    "JFK": 1.5
}

# Surge values at or above this level require human approval
HIGH_RISK_SURGE_THRESHOLD = 1.3


# ============================================================
# TOOL 1: GET AIRPORT METRICS
# ============================================================

def get_airport_metrics(airport_code: str) -> dict:
    """
    Retrieve the latest operational metrics for an airport.
    """

    airport_code = airport_code.strip().upper()

    if airport_code not in VALID_AIRPORTS:
        return {
            "status": "error",
            "message": (
                f"Invalid airport code: {airport_code}. "
                "Valid airport codes are: SFO, LAX, JFK."
            )
        }

    try:
        df = pd.read_csv(DATA_PATH)

    except FileNotFoundError:
        return {
            "status": "error",
            "message": (
                f"Operational data file not found: {DATA_PATH}"
            )
        }

    except Exception as error:
        return {
            "status": "error",
            "message": (
                f"Error loading operational data: {str(error)}"
            )
        }

    airport_data = df[
        df["airport_code"].str.upper() == airport_code
    ].copy()

    if airport_data.empty:
        return {
            "status": "error",
            "message": (
                f"No operational data found for {airport_code}."
            )
        }

    try:
        airport_data["timestamp"] = pd.to_datetime(
            airport_data["timestamp"]
        )

    except Exception as error:
        return {
            "status": "error",
            "message": (
                f"Invalid timestamp data: {str(error)}"
            )
        }

    latest_record = airport_data.sort_values(
        "timestamp"
    ).iloc[-1]

    return {
        "status": "success",
        "airport_code": airport_code,
        "timestamp": latest_record["timestamp"].strftime(
            "%Y-%m-%d %H:%M"
        ),
        "completion_rate": float(
            latest_record["completion_rate"]
        ),
        "average_eta": float(
            latest_record["average_eta"]
        ),
        "active_drivers": int(
            latest_record["active_drivers"]
        ),
        "cancellation_rate": float(
            latest_record["cancellation_rate"]
        ),
        "queue_size": int(
            latest_record["queue_size"]
        ),
        "surge_multiplier": float(
            latest_record["surge_multiplier"]
        ),
        "request_volume": int(
            latest_record["request_volume"]
        )
    }


# ============================================================
# TOOL 2: CALCULATE DRIVER INCENTIVE
# ============================================================

def calculate_driver_incentive(
    driver_count: int,
    severity_level: str
) -> dict:
    """
    Calculate a recommended driver incentive.
    """

    if not isinstance(driver_count, int):
        return {
            "status": "error",
            "message": "Driver count must be an integer."
        }

    if driver_count < 0:
        return {
            "status": "error",
            "message": "Driver count cannot be negative."
        }

    severity_level = severity_level.strip().lower()

    if severity_level not in VALID_SEVERITY_LEVELS:
        return {
            "status": "error",
            "message": (
                f"Invalid severity level: {severity_level}. "
                "Valid levels are: low, medium, high, critical."
            )
        }

    # Synthetic project incentive rules
    if severity_level == "low":
        incentive = 5

    elif severity_level == "medium":
        incentive = 10

    elif severity_level == "high":
        incentive = 20

    else:
        incentive = 30

    # Additional incentive when driver availability is low
    if driver_count < 300:
        incentive += 10

    reason = (
        f"Recommended incentive based on "
        f"{severity_level} severity and "
        f"{driver_count} active drivers."
    )

    if driver_count < 300:
        reason += (
            " An additional incentive was added because "
            "active driver count is below 300."
        )

    return {
        "status": "success",
        "driver_count": driver_count,
        "severity_level": severity_level,
        "recommended_incentive": incentive,
        "currency": "USD",
        "reason": reason
    }


# ============================================================
# TOOL 3: TRIGGER SURGE OVERRIDE
# ============================================================

def trigger_surge_override(
    airport_code: str,
    new_multiplier: float,
    reason: str
) -> dict:
    """
    Request a surge pricing override.

    High-risk surge values require human approval.
    Values above the airport's maximum are blocked.
    """

    # --------------------------------------------------------
    # Validate airport
    # --------------------------------------------------------

    airport_code = airport_code.strip().upper()

    if airport_code not in VALID_AIRPORTS:
        return {
            "status": "error",
            "message": (
                f"Invalid airport code: {airport_code}. "
                "Valid airport codes are: SFO, LAX, JFK."
            )
        }

    # --------------------------------------------------------
    # Validate multiplier
    # --------------------------------------------------------

    if not isinstance(new_multiplier, (int, float)):
        return {
            "status": "error",
            "message": "Surge multiplier must be a number."
        }

    new_multiplier = float(new_multiplier)

    if new_multiplier <= 0:
        return {
            "status": "error",
            "message": "Surge multiplier must be greater than 0."
        }

    # --------------------------------------------------------
    # Validate reason
    # --------------------------------------------------------

    if not isinstance(reason, str) or not reason.strip():
        return {
            "status": "error",
            "message": "A reason is required for a surge override."
        }

    reason = reason.strip()

    # --------------------------------------------------------
    # Get airport maximum
    # --------------------------------------------------------

    maximum_allowed = MAX_SURGE_MULTIPLIER[airport_code]

    # --------------------------------------------------------
    # Block values above policy maximum
    # --------------------------------------------------------

    if new_multiplier > maximum_allowed:
        return {
            "status": "blocked",
            "airport_code": airport_code,
            "requested_multiplier": new_multiplier,
            "maximum_allowed": maximum_allowed,
            "risk_level": "high",
            "message": (
                f"Requested surge multiplier "
                f"{new_multiplier}x exceeds the maximum "
                f"allowed multiplier of {maximum_allowed}x "
                f"for {airport_code}."
            )
        }

    # --------------------------------------------------------
    # High-risk surge requires human approval
    # --------------------------------------------------------

    if new_multiplier >= HIGH_RISK_SURGE_THRESHOLD:
        return {
            "status": "approval_required",
            "airport_code": airport_code,
            "requested_multiplier": new_multiplier,
            "maximum_allowed": maximum_allowed,
            "risk_level": "high",
            "reason": reason,
            "approval_required": True,
            "message": (
                f"Surge override of {new_multiplier}x at "
                f"{airport_code} is within the allowed maximum "
                f"but requires explicit human approval."
            )
        }

    # --------------------------------------------------------
    # Low-risk request
    # --------------------------------------------------------

    return {
        "status": "ready",
        "airport_code": airport_code,
        "requested_multiplier": new_multiplier,
        "maximum_allowed": maximum_allowed,
        "risk_level": "low",
        "reason": reason,
        "approval_required": False,
        "message": (
            f"Surge override of {new_multiplier}x at "
            f"{airport_code} passed validation and is ready "
            f"for execution."
        )
    }


# ============================================================
# TOOL TESTING
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("AIRPORT OPERATIONS AI COPILOT")
    print("DAY 2 - OPERATIONAL TOOLS")
    print("=" * 60)

    # ========================================================
    # TEST 1: AIRPORT METRICS
    # ========================================================

    print("\n" + "-" * 60)
    print("TEST 1: GET AIRPORT METRICS")
    print("-" * 60)

    for airport in ["SFO", "LAX", "JFK", "ABC"]:

        print(f"\nTesting airport: {airport}")

        result = get_airport_metrics(airport)

        print(result)

    # ========================================================
    # TEST 2: DRIVER INCENTIVE
    # ========================================================

    print("\n" + "-" * 60)
    print("TEST 2: CALCULATE DRIVER INCENTIVE")
    print("-" * 60)

    incentive_test_cases = [
        (420, "low"),
        (350, "medium"),
        (350, "high"),
        (250, "high"),
        (200, "critical"),
        (350, "unknown"),
        (-10, "high")
    ]

    for driver_count, severity in incentive_test_cases:

        print(
            f"\nDrivers: {driver_count} | "
            f"Severity: {severity}"
        )

        result = calculate_driver_incentive(
            driver_count=driver_count,
            severity_level=severity
        )

        print(result)

    # ========================================================
    # TEST 3: SURGE OVERRIDE
    # ========================================================

    print("\n" + "-" * 60)
    print("TEST 3: TRIGGER SURGE OVERRIDE")
    print("-" * 60)

    surge_test_cases = [
        ("SFO", 1.2, "Temporary increase due to high airport demand"),
        ("SFO", 1.3, "High queue and insufficient driver availability"),
        ("SFO", 1.6, "Severe operational demand"),
        ("LAX", 1.5, "High request volume"),
        ("JFK", 1.3, "Driver shortage during peak period"),
        ("ABC", 1.2, "Invalid airport test"),
        ("SFO", -1.0, "Invalid multiplier test"),
        ("SFO", 1.2, "")
    ]

    for airport, multiplier, reason in surge_test_cases:

        print(
            f"\nAirport: {airport} | "
            f"Multiplier: {multiplier}x"
        )

        result = trigger_surge_override(
            airport_code=airport,
            new_multiplier=multiplier,
            reason=reason
        )

        print(result)

    # ========================================================
    # COMPLETION
    # ========================================================

    print("\n" + "=" * 60)
    print("DAY 2 OPERATIONAL TOOLS TESTING COMPLETED")
    print("=" * 60)
