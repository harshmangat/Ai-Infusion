"""Simple compensation calculations for shipment exceptions."""


def calculate_delay_compensation(
    shipment_value: float, days_delayed: int
) -> dict[str, object]:
    """Pay $10 per delayed day, up to 20% of the shipment value."""
    if shipment_value < 0:
        raise ValueError("Shipment value cannot be negative.")
    if days_delayed < 0:
        raise ValueError("Days delayed cannot be negative.")

    daily_compensation = days_delayed * 10
    maximum_compensation = shipment_value * 0.20

    # Use the cap when the daily compensation is higher than 20% of the value.
    if daily_compensation > maximum_compensation:
        compensation_amount = maximum_compensation
    else:
        compensation_amount = daily_compensation

    return {
        "category": "delayed",
        "compensation_amount": compensation_amount,
        "shipment_value": shipment_value,
        "days_delayed": days_delayed,
        "cap_amount": maximum_compensation,
    }


def calculate_damage_compensation(
    shipment_value: float, severity: str
) -> dict[str, object]:
    """Pay a percentage of the shipment value based on damage severity."""
    if shipment_value < 0:
        raise ValueError("Shipment value cannot be negative.")

    if severity == "minor":
        compensation_rate = 0.25
    elif severity == "moderate":
        compensation_rate = 0.50
    elif severity == "severe":
        compensation_rate = 1.00
    else:
        raise ValueError("Severity must be minor, moderate, or severe.")

    compensation_amount = shipment_value * compensation_rate

    return {
        "category": "damaged",
        "compensation_amount": compensation_amount,
        "shipment_value": shipment_value,
        "severity": severity,
        "compensation_rate": compensation_rate,
    }


def calculate_lost_compensation(
    shipment_value: float,
) -> dict[str, object]:
    """Pay the shipment value plus a $50 logistics credit."""
    if shipment_value < 0:
        raise ValueError("Shipment value cannot be negative.")

    goodwill_credit = 50
    compensation_amount = shipment_value + goodwill_credit

    return {
        "category": "lost",
        "compensation_amount": compensation_amount,
        "shipment_value": shipment_value,
        "goodwill_credit": goodwill_credit,
    }
