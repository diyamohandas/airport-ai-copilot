from src.tools import (
    get_airport_metrics,
    calculate_driver_incentive,
    trigger_surge_override
)


# ============================================================
# TEST 1: AIRPORT METRICS
# ============================================================

def test_get_airport_metrics_valid():

    result = get_airport_metrics("SFO")

    assert result["status"] == "success"
    assert result["airport_code"] == "SFO"
    assert result["active_drivers"] == 350
    assert result["queue_size"] == 68


def test_get_airport_metrics_invalid():

    result = get_airport_metrics("ABC")

    assert result["status"] == "error"


# ============================================================
# TEST 2: DRIVER INCENTIVE
# ============================================================

def test_driver_incentive_high_severity():

    result = calculate_driver_incentive(
        driver_count=350,
        severity_level="high"
    )

    assert result["status"] == "success"
    assert result["recommended_incentive"] == 20


def test_driver_incentive_low_driver_count():

    result = calculate_driver_incentive(
        driver_count=250,
        severity_level="high"
    )

    assert result["status"] == "success"
    assert result["recommended_incentive"] == 30


def test_driver_incentive_invalid_severity():

    result = calculate_driver_incentive(
        driver_count=350,
        severity_level="unknown"
    )

    assert result["status"] == "error"


# ============================================================
# TEST 3: SURGE OVERRIDE
# ============================================================

def test_surge_override_low_risk():

    result = trigger_surge_override(
        airport_code="SFO",
        new_multiplier=1.2,
        reason="Temporary increase due to high demand"
    )

    assert result["status"] == "ready"
    assert result["approval_required"] is False


def test_surge_override_requires_approval():

    result = trigger_surge_override(
        airport_code="SFO",
        new_multiplier=1.3,
        reason="High queue and insufficient drivers"
    )

    assert result["status"] == "approval_required"
    assert result["approval_required"] is True


def test_surge_override_above_maximum():

    result = trigger_surge_override(
        airport_code="SFO",
        new_multiplier=1.6,
        reason="Severe demand"
    )

    assert result["status"] == "blocked"


def test_surge_override_invalid_airport():

    result = trigger_surge_override(
        airport_code="ABC",
        new_multiplier=1.2,
        reason="Test"
    )

    assert result["status"] == "error"
