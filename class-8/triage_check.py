"""Check the four required shipment exception routing examples."""

from pipeline import process_exception


class FakeChain:
    """Return a fixed answer so the checks do not call the language model."""

    def __init__(self, answer):
        self.answer = answer

    def invoke(self, inputs):
        return self.answer


def check_report(
    report_name,
    report_text,
    shipment_value,
    category,
    expected_escalation,
    days_delayed=None,
    damage_severity=None,
):
    """Run one report through the pipeline and compare its expected route."""
    classify_chain = FakeChain(category)
    escalate_chain = FakeChain("Test manager note")
    draft_email_chain = FakeChain("Test customer email")

    result = process_exception(
        exception_report=report_text,
        shipment_value=shipment_value,
        customer_tier="standard",
        classify_chain=classify_chain,
        escalate_chain=escalate_chain,
        draft_email_chain=draft_email_chain,
        days_delayed=days_delayed,
        damage_severity=damage_severity,
    )

    actual_escalation = result["should_escalate"]
    compensation_amount = result["compensation"]["compensation_amount"]

    print(f"\n{report_name}")
    print(f"Category: {result['category']}")
    print(f"Compensation: ${compensation_amount}")
    print(f"Expected escalation: {expected_escalation}")
    print(f"Actual escalation: {actual_escalation}")

    if result["category"] != category:
        raise AssertionError(
            f"{report_name}: expected category {category}, "
            f"got {result['category']}."
        )

    if actual_escalation != expected_escalation:
        raise AssertionError(
            f"{report_name}: expected escalation {expected_escalation}, "
            f"got {actual_escalation}."
        )

    print("PASS")


def main():
    print("Checking the four required shipment exception routes...")

    # A one-day delay costs $10, below the standard $100 threshold.
    check_report(
        "Mild delay",
        "The shipment arrived one day late.",
        100,
        "delayed",
        False,
        days_delayed=1,
    )

    # A lost shipment pays its value plus the $50 goodwill credit.
    check_report(
        "High-value loss",
        "The high-value shipment has been lost.",
        500,
        "lost",
        True,
    )

    # Minor damage pays 25% of the value, below the standard threshold.
    check_report(
        "Minor damage",
        "The shipment arrived with minor damage.",
        100,
        "damaged",
        False,
        damage_severity="minor",
    )

    # Unknown reports must escalate even when compensation is zero.
    check_report(
        "Unclassifiable report",
        "Blue yesterday, box said maybe.",
        10,
        "unknown",
        True,
    )

    print("\nAll four routing checks passed.")


if __name__ == "__main__":
    main()
