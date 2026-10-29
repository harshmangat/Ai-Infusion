"""Simple checks for the shipment exception desk interface callbacks."""

from app import (
    build_log_rows,
    clear_session,
    create_demo,
    format_daily_summary,
    submit_exception,
)


class FakeChain:
    def __init__(self, answer):
        self.answer = answer

    def invoke(self, inputs):
        return self.answer


def test_submission_updates_result_and_daily_log():
    result = submit_exception(
        "The shipment arrived one day late.",
        100,
        "standard",
        1,
        "minor",
        [],
        FakeChain("delayed"),
        FakeChain("Manager note"),
        FakeChain("Customer email"),
    )

    outcome, log_rows, history = result

    assert "Category:** delayed" in outcome
    assert "Compensation:** $10.00" in outcome
    assert "Resolved automatically" in outcome
    assert len(log_rows) == 1
    assert log_rows[0][1] == "The shipment arrived one day late."
    assert log_rows[0][2] == "delayed"
    assert log_rows[0][4] == 10
    assert log_rows[0][5] == "Customer email"
    assert len(history) == 1
    print("Submission and log test passed.")


def test_daily_summary_uses_session_results():
    history = [
        {
            "report": "Lost report",
            "category": "lost",
            "compensation": {
                "category": "lost",
                "compensation_amount": 150,
                "shipment_value": 100,
            },
            "should_escalate": True,
            "response_type": "manager_note",
            "response": "Review this loss.",
        },
        {
            "report": "Small delay",
            "category": "delayed",
            "compensation": {
                "category": "delayed",
                "compensation_amount": 10,
                "shipment_value": 100,
            },
            "should_escalate": False,
            "response_type": "customer_email",
            "response": "Sorry for the delay.",
        },
    ]

    summary = format_daily_summary(history)

    assert "Reports processed:** 2" in summary
    assert "Total compensation:** $160.00" in summary
    assert "Escalation rate:** 50.0%" in summary
    assert "Costliest category:** lost" in summary
    assert "delayed: $10.00" in summary
    assert "lost: $150.00" in summary
    print("Daily summary display test passed.")


def test_log_builder_handles_empty_history():
    assert build_log_rows([]) == []
    print("Empty log test passed.")


def test_start_new_session_clears_all_outputs():
    assert clear_session() == ("", [], [], "")
    print("New session clear test passed.")


def test_gradio_demo_builds():
    demo = create_demo()
    config = demo.get_config_file()

    assert config["title"] == "Northwind Shipment Exception Desk"
    assert len(config["components"]) > 0
    print("Gradio interface build test passed.")


if __name__ == "__main__":
    test_submission_updates_result_and_daily_log()
    test_daily_summary_uses_session_results()
    test_log_builder_handles_empty_history()
    test_start_new_session_clears_all_outputs()
    test_gradio_demo_builds()
    print("All app tests passed.")
