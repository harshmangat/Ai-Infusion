"""Gradio interface for the Northwind shipment exception desk."""

import gradio as gr

from pipeline import process_exception
from session import TriageSession


APP_CSS = """
:root,
body,
.gradio-container {
    color-scheme: light !important;
}

body {
    background: #f2f6fa !important;
}

.gradio-container {
    background:
        radial-gradient(ellipse at 12% 0%, #dceef2 0, transparent 34%),
        #f2f6fa !important;
    color: #1b2d3d !important;
    width: 100% !important;
    max-width: none !important;
    margin: 0 !important;
}

main.contain {
    box-sizing: border-box !important;
    width: calc(100% - 48px) !important;
    max-width: 1180px !important;
    margin-left: auto !important;
    margin-right: auto !important;
}

#app-header {
    background: linear-gradient(120deg, #102d43, #174c5a) !important;
    border: 1px solid #28596a !important;
    border-radius: 22px !important;
    box-shadow: 0 16px 38px #173a4a24 !important;
    margin: 20px 0 18px !important;
    padding: 28px 32px !important;
}

#app-header,
#app-header * {
    color: #f5fbfc !important;
}

#app-header h1 {
    font-size: clamp(1.8rem, 4vw, 2.5rem) !important;
    letter-spacing: -0.035em !important;
    margin-bottom: 8px !important;
}

#app-header p {
    color: #d3e6e9 !important;
    font-size: 1rem !important;
    max-width: 760px !important;
}

#report-card,
#outcome-card,
#log-card,
#summary-card {
    background: #ffffff !important;
    border: 1px solid #dce6ed !important;
    border-radius: 18px !important;
    box-shadow: 0 8px 24px #203c5010 !important;
    margin: 14px 0 !important;
    padding: 20px 22px !important;
}

#report-card > .styler,
#outcome-card > .styler,
#log-card > .styler,
#summary-card > .styler {
    background: #ffffff !important;
    color: #1b2d3d !important;
}

#report-card .form,
#report-card .wrap,
#report-card .block,
#report-card .styler,
#outcome-card .form,
#outcome-card .wrap,
#outcome-card .block,
#outcome-card .styler,
#log-card .form,
#log-card .wrap,
#log-card .block,
#log-card .styler,
#summary-card .form,
#summary-card .wrap,
#summary-card .block,
#summary-card .styler {
    background-color: #ffffff !important;
    color: #1b2d3d !important;
}

#report-card h2,
#outcome-card h2,
#log-card h2,
#summary-card h2 {
    color: #17364b !important;
    letter-spacing: -0.02em !important;
}

#outcome-card p,
#summary-card p {
    color: #64788b !important;
}

.gradio-container label,
.gradio-container .prose,
.gradio-container p,
.gradio-container h1,
.gradio-container h2,
.gradio-container h3 {
    color: #1b2d3d;
}

.gradio-container input,
.gradio-container textarea,
.gradio-container [role="listbox"],
.gradio-container [data-testid="dropdown"] {
    background-color: #fbfdfe !important;
    border-color: #d4e0e8 !important;
    color: #1b2d3d !important;
}

.gradio-container input::placeholder,
.gradio-container textarea::placeholder {
    color: #788b9b !important;
}

.gradio-container button.primary {
    background: #087f75 !important;
    border: 1px solid #087f75 !important;
    border-radius: 11px !important;
    color: #ffffff !important;
    font-weight: 650 !important;
}

.gradio-container button.primary:hover {
    background: #066b63 !important;
    border-color: #066b63 !important;
}

.gradio-container button:not(.primary) {
    background: #eef4f7 !important;
    border: 1px solid #d4e0e8 !important;
    border-radius: 11px !important;
    color: #25465b !important;
}

.gradio-container button:not(.primary):hover {
    background: #e2edf1 !important;
}

.gradio-container table {
    background: #ffffff !important;
    color: #1b2d3d !important;
}

.gradio-container #log-card table,
.gradio-container #log-card th,
.gradio-container #log-card td,
.gradio-container #log-card .header-cell,
.gradio-container #log-card .cell {
    background: #ffffff !important;
    color: #1b2d3d !important;
}

.gradio-container .gr-group .styler,
.gradio-container .gr-group .form {
    background-color: #ffffff !important;
}

.gradio-container #log-card th,
.gradio-container #log-card .header-cell {
    background: #edf4f6 !important;
    color: #24465b !important;
}

.gradio-container #log-card td,
.gradio-container #log-card .cell {
    border-color: #e4ebf0 !important;
}
"""


def build_log_rows(history: list[dict[str, object]]) -> list[list[object]]:
    """Turn saved pipeline results into rows for the triage table."""
    rows = []

    for number, entry in enumerate(history, start=1):
        compensation = entry["compensation"]
        if entry["should_escalate"]:
            route = "Manager review"
        else:
            route = "Customer email"

        rows.append(
            [
                number,
                entry["report"],
                entry["category"],
                compensation["shipment_value"],
                compensation["compensation_amount"],
                route,
            ]
        )

    return rows


def format_daily_summary(history: list[dict[str, object]]) -> str:
    """Create readable text for the daily summary panel."""
    session = TriageSession()

    for entry in history:
        session.add_exception(entry)

    summary = session.generate_daily_summary()
    category_totals = summary["category_totals"]

    lines = [
        "## Daily Triage Summary",
        f"- **Reports processed:** {summary['number_of_exceptions']}",
        f"- **Total compensation:** "
        f"${summary['total_compensation_paid']:.2f}",
        f"- **Escalated reports:** {summary['escalated_count']}",
        f"- **Escalation rate:** {summary['escalation_rate']:.1f}%",
        f"- **Costliest category:** "
        f"{summary['costliest_category'] or 'None'}",
        "- **Compensation by category:**",
    ]

    for category in category_totals:
        lines.append(
            f"  - {category}: ${category_totals[category]:.2f}"
        )

    return "\n".join(lines)


def submit_exception(
    report: str,
    shipment_value: float,
    customer_tier: str,
    days_delayed: int,
    damage_severity: str,
    history: list[dict[str, object]],
    classify_chain=None,
    escalate_chain=None,
    draft_email_chain=None,
):
    """Process one submitted report and update the log and session state."""
    if not report or not report.strip():
        raise gr.Error("Enter a shipment exception report.")
    if shipment_value is None or shipment_value < 0:
        raise gr.Error("Enter a shipment value of zero or more.")
    if days_delayed is None or days_delayed < 0:
        raise gr.Error("Days delayed must be zero or more.")
    if customer_tier not in ["standard", "premium"]:
        raise gr.Error("Choose standard or premium customer tier.")
    if damage_severity not in ["minor", "moderate", "severe"]:
        raise gr.Error("Choose a valid damage severity.")

    result = process_exception(
        exception_report=report.strip(),
        shipment_value=shipment_value,
        customer_tier=customer_tier,
        classify_chain=classify_chain,
        escalate_chain=escalate_chain,
        draft_email_chain=draft_email_chain,
        days_delayed=days_delayed,
        damage_severity=damage_severity,
    )

    saved_result = dict(result)
    saved_result["report"] = report.strip()
    updated_history = list(history or [])
    updated_history.append(saved_result)

    if result["should_escalate"]:
        route = "Escalated for manager review"
        response_label = "Internal manager note"
    else:
        route = "Resolved automatically"
        response_label = "Customer email draft"

    compensation = result["compensation"]
    outcome = (
        "## Processing Outcome\n"
        f"- **Category:** {result['category']}\n"
        f"- **Compensation:** "
        f"${compensation['compensation_amount']:.2f}\n"
        f"- **Route:** {route}\n"
        f"- **Steps:** report classified → compensation calculated → "
        f"{route.lower()}\n\n"
        f"### {response_label}\n"
        f"{result['response']}"
    )

    return outcome, build_log_rows(updated_history), updated_history


def clear_session():
    """Clear the visible outputs and per-browser-session triage history."""
    return "", [], [], ""


def create_demo():
    """Build the shipment exception desk interface."""
    with gr.Blocks(title="Northwind Shipment Exception Desk") as demo:
        gr.Markdown(
            "# Northwind Shipment Exception Desk\n\n"
            "A clear view of shipment exceptions, compensation, and review "
            "decisions.",
            elem_id="app-header",
        )

        session_history = gr.State([])

        with gr.Group(elem_id="report-card"):
            gr.Markdown("## New Exception Report")
            report_input = gr.Textbox(
                label="Shipment exception report",
                placeholder="Describe what happened to the shipment...",
                lines=4,
            )
            with gr.Row():
                shipment_value_input = gr.Number(
                    label="Declared shipment value ($)",
                    value=100,
                    minimum=0,
                    precision=2,
                )
                customer_tier_input = gr.Dropdown(
                    label="Customer tier",
                    choices=["standard", "premium"],
                    value="standard",
                )
            with gr.Row():
                days_delayed_input = gr.Number(
                    label="Days delayed (used for delay reports)",
                    value=1,
                    minimum=0,
                    precision=0,
                )
                damage_severity_input = gr.Dropdown(
                    label="Damage severity (used for damage reports)",
                    choices=["minor", "moderate", "severe"],
                    value="minor",
                )
            with gr.Row():
                submit_button = gr.Button(
                    "Process Report",
                    variant="primary",
                )
                clear_button = gr.Button("Start New Session")

        with gr.Group(elem_id="outcome-card"):
            gr.Markdown("## Processing Result")
            outcome_display = gr.Markdown(
                "Submit a report to see its category, compensation, and route."
            )

        with gr.Group(elem_id="log-card"):
            gr.Markdown("## Daily Triage Log")
            log_display = gr.Dataframe(
                headers=[
                    "#",
                    "Report",
                    "Category",
                    "Shipment value ($)",
                    "Compensation ($)",
                    "Route",
                ],
                datatype=["number", "str", "str", "number", "number", "str"],
                value=[],
                interactive=False,
                wrap=True,
            )

        with gr.Group(elem_id="summary-card"):
            gr.Markdown("## Daily Summary")
            summary_button = gr.Button("Generate Daily Summary")
            summary_display = gr.Markdown(
                "Process reports, then generate a summary."
            )

        submit_button.click(
            fn=submit_exception,
            inputs=[
                report_input,
                shipment_value_input,
                customer_tier_input,
                days_delayed_input,
                damage_severity_input,
                session_history,
            ],
            outputs=[outcome_display, log_display, session_history],
        )
        summary_button.click(
            fn=format_daily_summary,
            inputs=session_history,
            outputs=summary_display,
        )
        clear_button.click(
            fn=clear_session,
            inputs=[],
            outputs=[
                outcome_display,
                log_display,
                session_history,
                summary_display,
            ],
        )

    return demo


def main():
    demo = create_demo()
    demo.launch(
        theme=gr.themes.Base(
            primary_hue="teal",
            secondary_hue="cyan",
            neutral_hue="slate",
        ),
        css=APP_CSS,
    )


if __name__ == "__main__":
    main()
