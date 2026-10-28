"""Simple checks for the daily triage summary."""

from session import TriageSession


def make_result(category, amount, should_escalate):
    return {
        "category": category,
        "compensation": {
            "category": category,
            "compensation_amount": amount,
        },
        "should_escalate": should_escalate,
        "response_type": "manager_note" if should_escalate else "customer_email",
        "response": "Test response",
    }


def test_summary_totals_and_escalation_rate():
    session = TriageSession()
    session.add_exception(make_result("delayed", 10, False))
    session.add_exception(make_result("lost", 150, True))
    session.add_exception(make_result("damaged", 25, False))
    session.add_exception(make_result("unknown", 0, True))

    summary = session.generate_daily_summary()

    assert summary["number_of_exceptions"] == 4
    assert summary["total_compensation_paid"] == 185
    assert summary["escalated_count"] == 2
    assert summary["escalation_rate"] == 50
    assert summary["costliest_category"] == "lost"
    print("Summary totals and escalation rate test passed.")


def test_costliest_category_adds_category_totals():
    session = TriageSession()
    session.add_exception(make_result("delayed", 10, False))
    session.add_exception(make_result("delayed", 10, False))
    session.add_exception(make_result("delayed", 10, False))
    session.add_exception(make_result("damaged", 25, False))

    summary = session.generate_daily_summary()

    # Three small delay payments total more than the single damage payment.
    assert summary["category_totals"]["delayed"] == 30
    assert summary["category_totals"]["damaged"] == 25
    assert summary["costliest_category"] == "delayed"
    print("Costliest category aggregation test passed.")


def test_empty_session_has_zero_totals():
    session = TriageSession()

    summary = session.generate_daily_summary()

    assert summary["number_of_exceptions"] == 0
    assert summary["total_compensation_paid"] == 0
    assert summary["escalated_count"] == 0
    assert summary["escalation_rate"] == 0
    assert summary["costliest_category"] is None
    print("Empty session test passed.")


if __name__ == "__main__":
    test_summary_totals_and_escalation_rate()
    test_costliest_category_adds_category_totals()
    test_empty_session_has_zero_totals()
    print("All session tests passed.")
