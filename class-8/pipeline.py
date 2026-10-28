"""Connect report classification, compensation, and response drafting."""

from chains import create_chains
from tools import (
    calculate_damage_compensation,
    calculate_delay_compensation,
    calculate_lost_compensation,
)


STANDARD_ESCALATION_THRESHOLD = 100
PREMIUM_ESCALATION_THRESHOLD = 50


def process_exception(
    exception_report: str,
    shipment_value: float,
    customer_tier: str,
    classify_chain=None,
    escalate_chain=None,
    draft_email_chain=None,
    days_delayed: int | None = None,
    damage_severity: str | None = None,
) -> dict[str, object]:
    """Classify a report, calculate compensation, and draft the response.

    LangChain chains are created automatically unless test chains are provided.
    """
    if customer_tier == "premium":
        escalation_threshold = PREMIUM_ESCALATION_THRESHOLD
    elif customer_tier == "standard":
        escalation_threshold = STANDARD_ESCALATION_THRESHOLD
    else:
        raise ValueError("Customer tier must be premium or standard.")

    if (
        classify_chain is None
        or escalate_chain is None
        or draft_email_chain is None
    ):
        created_chains = create_chains()
        if classify_chain is None:
            classify_chain = created_chains[0]
        if escalate_chain is None:
            escalate_chain = created_chains[1]
        if draft_email_chain is None:
            draft_email_chain = created_chains[2]

    category = classify_chain.invoke({"report": exception_report})
    category = category.strip().lower()
    if category == "delayed":
        if days_delayed is None:
            raise ValueError("Provide the number of days the shipment was delayed.")
        compensation = calculate_delay_compensation(
            shipment_value, days_delayed
        )
    elif category == "damaged":
        if damage_severity is None:
            raise ValueError("Provide the severity of the shipment damage.")
        compensation = calculate_damage_compensation(
            shipment_value, damage_severity
        )
    elif category == "lost":
        compensation = calculate_lost_compensation(shipment_value)
    else:
        category = "unknown"
        compensation = {
            "category": "unknown",
            "compensation_amount": 0,
            "shipment_value": shipment_value,
        }

    compensation_amount = compensation["compensation_amount"]
    if category == "unknown":
        should_escalate = True
    elif compensation_amount > escalation_threshold:
        should_escalate = True
    else:
        should_escalate = False

    if should_escalate:
        response = escalate_chain.invoke(
            {
                "report": exception_report,
                "category": category,
                "compensation_amount": compensation_amount,
                "customer_tier": customer_tier,
            }
        )
        response_type = "manager_note"
    else:
        response = draft_email_chain.invoke(
            {
                "report": exception_report,
                "category": category,
                "compensation_amount": compensation_amount,
                "customer_tier": customer_tier,
            }
        )
        response_type = "customer_email"

    return {
        "category": category,
        "compensation": compensation,
        "should_escalate": should_escalate,
        "response_type": response_type,
        "response": response,
    }
