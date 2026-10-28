"""Compensation calculators for shipment exceptions."""

import math


DELAY_DAILY_RATE = 10.0
DELAY_VALUE_CAP_RATE = 0.20
DAMAGE_RATES = {
    "minor": 0.25,
    "moderate": 0.50,
    "severe": 1.00,
}
LOST_SHIPMENT_GOODWILL_CREDIT = 50.0


def _validate_shipment_value(shipment_value: float) -> None:
    if (
        isinstance(shipment_value, bool)
        or not isinstance(shipment_value, (int, float))
        or not math.isfinite(shipment_value)
        or shipment_value < 0
    ):
        raise ValueError("shipment_value must be a finite, non-negative number.")


def calculate_delay_compensation(
    shipment_value: float, days_delayed: int
) -> dict[str, object]:
    """Pay $10 per delayed day, capped at 20% of the shipment value."""
    _validate_shipment_value(shipment_value)
    if isinstance(days_delayed, bool) or not isinstance(days_delayed, int):
        raise ValueError("days_delayed must be a non-negative integer.")
    if days_delayed < 0:
        raise ValueError("days_delayed must be a non-negative integer.")

    cap_amount = round(shipment_value * DELAY_VALUE_CAP_RATE, 2)
    amount = round(min(days_delayed * DELAY_DAILY_RATE, cap_amount), 2)
    return {
        "category": "delayed",
        "compensation_amount": amount,
        "shipment_value": round(shipment_value, 2),
        "days_delayed": days_delayed,
        "cap_amount": cap_amount,
    }


def calculate_damage_compensation(
    shipment_value: float, severity: str
) -> dict[str, object]:
    """Compensate 25%, 50%, or 100% of value based on damage severity."""
    _validate_shipment_value(shipment_value)
    if not isinstance(severity, str):
        raise ValueError("severity must be minor, moderate, or severe.")

    normalized_severity = severity.strip().lower()
    if normalized_severity not in DAMAGE_RATES:
        raise ValueError("severity must be minor, moderate, or severe.")

    rate = DAMAGE_RATES[normalized_severity]
    return {
        "category": "damaged",
        "compensation_amount": round(shipment_value * rate, 2),
        "shipment_value": round(shipment_value, 2),
        "severity": normalized_severity,
        "compensation_rate": rate,
    }


def calculate_lost_compensation(shipment_value: float) -> dict[str, object]:
    """Compensate the full shipment value plus a $50 logistics credit."""
    _validate_shipment_value(shipment_value)

    shipment_value = round(shipment_value, 2)
    return {
        "category": "lost",
        "compensation_amount": round(
            shipment_value + LOST_SHIPMENT_GOODWILL_CREDIT, 2
        ),
        "shipment_value": shipment_value,
        "goodwill_credit": LOST_SHIPMENT_GOODWILL_CREDIT,
    }
