"""Simple tests for the exception processing pipeline."""

from pipeline import process_exception


class FakeChain:
    """A small stand-in for a chain so tests do not call an LLM."""

    def __init__(self, answer):
        self.answer = answer
        self.inputs = []

    def invoke(self, inputs):
        self.inputs.append(inputs)
        return self.answer


def test_delayed_report_uses_daily_compensation():
    classify_chain = FakeChain("delayed")
    escalate_chain = FakeChain("Manager note")
    draft_email_chain = FakeChain("Customer email")

    result = process_exception(
        "The package arrived one day late.",
        100,
        "standard",
        classify_chain,
        escalate_chain,
        draft_email_chain,
        days_delayed=1,
    )

    assert result["category"] == "delayed"
    assert result["compensation"]["compensation_amount"] == 10
    assert result["should_escalate"] is False
    assert result["response_type"] == "customer_email"
    assert result["response"] == "Customer email"
    assert classify_chain.inputs[0] == {
        "report": "The package arrived one day late."
    }
    assert len(escalate_chain.inputs) == 0
    assert len(draft_email_chain.inputs) == 1
    print("Delayed report test passed.")


def test_damaged_report_uses_severity():
    classify_chain = FakeChain("damaged")
    escalate_chain = FakeChain("Manager note")
    draft_email_chain = FakeChain("Customer email")

    result = process_exception(
        "The package arrived with minor damage.",
        200,
        "premium",
        classify_chain,
        escalate_chain,
        draft_email_chain,
        damage_severity="minor",
    )

    assert result["category"] == "damaged"
    assert result["compensation"]["compensation_amount"] == 50
    # Compensation equal to the threshold does not exceed it.
    assert result["should_escalate"] is False
    assert len(draft_email_chain.inputs) == 1
    print("Damaged report test passed.")


def test_lost_report_over_standard_threshold_escalates():
    classify_chain = FakeChain("lost")
    escalate_chain = FakeChain("Manager note")
    draft_email_chain = FakeChain("Customer email")

    result = process_exception(
        "The shipment is lost.",
        100,
        "standard",
        classify_chain,
        escalate_chain,
        draft_email_chain,
    )

    assert result["category"] == "lost"
    assert result["compensation"]["compensation_amount"] == 150
    assert result["should_escalate"] is True
    assert result["response_type"] == "manager_note"
    assert len(escalate_chain.inputs) == 1
    assert len(draft_email_chain.inputs) == 0
    print("High-value lost report test passed.")


def test_unknown_report_always_escalates():
    classify_chain = FakeChain("unknown")
    escalate_chain = FakeChain("Manager note")
    draft_email_chain = FakeChain("Customer email")

    result = process_exception(
        "This report cannot be understood.",
        10,
        "standard",
        classify_chain,
        escalate_chain,
        draft_email_chain,
    )

    assert result["category"] == "unknown"
    assert result["compensation"]["compensation_amount"] == 0
    assert result["should_escalate"] is True
    assert result["response_type"] == "manager_note"
    assert len(escalate_chain.inputs) == 1
    assert len(draft_email_chain.inputs) == 0
    print("Unknown report test passed.")


def test_standard_threshold_is_strictly_more_than_100():
    classify_chain = FakeChain("damaged")
    escalate_chain = FakeChain("Manager note")
    draft_email_chain = FakeChain("Customer email")

    result = process_exception(
        "The package is severely damaged.",
        100,
        "standard",
        classify_chain,
        escalate_chain,
        draft_email_chain,
        damage_severity="severe",
    )

    assert result["compensation"]["compensation_amount"] == 100
    assert result["should_escalate"] is False
    print("Standard threshold test passed.")


def test_premium_customer_escalates_over_50():
    classify_chain = FakeChain("damaged")
    escalate_chain = FakeChain("Manager note")
    draft_email_chain = FakeChain("Customer email")

    result = process_exception(
        "The package is severely damaged.",
        60,
        "premium",
        classify_chain,
        escalate_chain,
        draft_email_chain,
        damage_severity="severe",
    )

    assert result["compensation"]["compensation_amount"] == 60
    assert result["should_escalate"] is True
    print("Premium threshold test passed.")


def test_invalid_customer_tier_is_rejected():
    classify_chain = FakeChain("delayed")
    escalate_chain = FakeChain("Manager note")
    draft_email_chain = FakeChain("Customer email")

    try:
        process_exception(
            "The package arrived late.",
            100,
            "gold",
            classify_chain,
            escalate_chain,
            draft_email_chain,
        )
        assert False, "Unknown customer tier should be rejected."
    except ValueError:
        pass

    print("Invalid customer tier test passed.")


def test_missing_delay_details_are_rejected():
    classify_chain = FakeChain("delayed")
    escalate_chain = FakeChain("Manager note")
    draft_email_chain = FakeChain("Customer email")

    try:
        process_exception(
            "The package arrived late.",
            100,
            "standard",
            classify_chain,
            escalate_chain,
            draft_email_chain,
        )
        assert False, "Missing delay details should be rejected."
    except ValueError:
        pass

    print("Missing delay details test passed.")


def test_missing_damage_severity_is_rejected():
    classify_chain = FakeChain("damaged")
    escalate_chain = FakeChain("Manager note")
    draft_email_chain = FakeChain("Customer email")

    try:
        process_exception(
            "The package arrived damaged.",
            100,
            "standard",
            classify_chain,
            escalate_chain,
            draft_email_chain,
        )
        assert False, "Missing damage severity should be rejected."
    except ValueError:
        pass

    print("Missing damage severity test passed.")


if __name__ == "__main__":
    test_delayed_report_uses_daily_compensation()
    test_damaged_report_uses_severity()
    test_lost_report_over_standard_threshold_escalates()
    test_unknown_report_always_escalates()
    test_standard_threshold_is_strictly_more_than_100()
    test_premium_customer_escalates_over_50()
    test_invalid_customer_tier_is_rejected()
    test_missing_delay_details_are_rejected()
    test_missing_damage_severity_is_rejected()
    print("All pipeline tests passed.")
