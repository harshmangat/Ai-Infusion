"""Launch the InterviewIQ interview interface."""

import os
import sys
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

CLASS_SEVEN_PATH = Path(__file__).parent / "class-7"
sys.path.insert(0, str(CLASS_SEVEN_PATH))

from agent import EvaluatorAgent
from interview_bank import INTERVIEW_BANK


APP_CSS = """
:root {
    color-scheme: light;
}

html,
body,
.gradio-container {
    background-color: #ecf7f8 !important;
}

.gradio-container {
    color: #19363a;
}
"""

SCORECARD_HEADERS = [
    "#",
    "Question",
    "Relevance",
    "STAR components found",
    "Filler words",
]


def build_scorecard(history):
    rows = []

    for number, entry in enumerate(history, start=1):
        results = entry["tool_results"]
        star_components = results["check_star_structure"]["present"]
        filler_counts = results["detect_filler_words"]["counts"]
        filler_summary = ", ".join(
            f"{word} ({count})" for word, count in filler_counts.items()
        )
        rows.append(
            [
                number,
                entry["question"],
                results["score_relevance"]["score"],
                ", ".join(star_components) if star_components else "None",
                filler_summary if filler_summary else "None",
            ]
        )

    return rows


def create_demo(client):
    def submit_answer(question_index, answer, history):
        if question_index >= len(INTERVIEW_BANK):
            raise gr.Error("You have completed all interview questions.")

        answer = answer.strip()
        if not answer:
            raise gr.Error("Enter your answer before submitting.")

        question_data = INTERVIEW_BANK[question_index]
        evaluator = EvaluatorAgent(client)
        evaluator.history = list(history or [])
        evaluation = evaluator.evaluate_interview(
            question_data["question"],
            answer,
            question_data["expected_keywords"],
        )
        updated_history = evaluator.history
        next_index = question_index + 1

        if next_index < len(INTERVIEW_BANK):
            question_display = INTERVIEW_BANK[next_index]["question"]
            progress = f"Question {next_index + 1} of {len(INTERVIEW_BANK)}"
            submit_update = gr.update(
                value="Submit Answer",
                interactive=True,
            )
        else:
            question_display = "You have completed all interview questions."
            progress = f"Completed all {len(INTERVIEW_BANK)} questions."
            submit_update = gr.update(
                value="Interview Complete",
                interactive=False,
            )

        return (
            evaluation["feedback"],
            build_scorecard(updated_history),
            updated_history,
            next_index,
            question_display,
            progress,
            "",
            submit_update,
        )

    def ask_coach(question, history):
        question = question.strip()
        if not question:
            raise gr.Error("Enter a question for the interview coach.")

        evaluator = EvaluatorAgent(client)
        evaluator.history = list(history or [])
        return evaluator.ask_agent(question)

    def show_final_report(history):
        evaluator = EvaluatorAgent(client)
        evaluator.history = list(history or [])
        return evaluator.generate_final_report()

    def start_new_session():
        return (
            INTERVIEW_BANK[0]["question"],
            "Question 1 of {}".format(len(INTERVIEW_BANK)),
            "",
            [],
            0,
            "",
            [],
            gr.update(value="Submit Answer", interactive=True),
            "",
        )

    with gr.Blocks(title="InterviewIQ Interview Coach") as demo:
        gr.Markdown(
            "# InterviewIQ Interview Coach\n"
            "Answer every question, get immediate coaching, and track your "
            "progress across the interview."
        )

        history_state = gr.State([])
        question_index_state = gr.State(0)

        with gr.Group():
            gr.Markdown("## Current Question")
            question_display = gr.Textbox(
                label="Interview question",
                value=INTERVIEW_BANK[0]["question"],
                interactive=False,
                lines=2,
            )
            progress_display = gr.Markdown(
                f"Question 1 of {len(INTERVIEW_BANK)}"
            )
            answer_box = gr.Textbox(
                label="Your Answer",
                placeholder="Type your interview answer here...",
                lines=6,
            )
            with gr.Row():
                submit_button = gr.Button("Submit Answer", variant="primary")
                new_session_button = gr.Button("Start New Session")

        with gr.Group():
            gr.Markdown("## Feedback")
            feedback_panel = gr.Markdown(
                "Submit an answer to receive concise feedback."
            )

        with gr.Group():
            gr.Markdown("## Live Scorecard")
            scorecard = gr.Dataframe(
                headers=SCORECARD_HEADERS,
                datatype=["number", "str", "number", "str", "str"],
                value=[],
                interactive=False,
                wrap=True,
            )

        with gr.Group():
            gr.Markdown("## Interview Coach")
            with gr.Row():
                coach_question = gr.Textbox(
                    label="Ask about your progress",
                    placeholder="How am I doing so far? What should I improve?",
                    lines=2,
                    scale=4,
                )
                coach_button = gr.Button("Ask Coach", variant="secondary", scale=1)
            coach_response = gr.Markdown()

        with gr.Group():
            gr.Markdown("## Final Interview Report")
            final_report_button = gr.Button("Generate Final Report")
            final_report = gr.Markdown()

        submit_button.click(
            fn=submit_answer,
            inputs=[question_index_state, answer_box, history_state],
            outputs=[
                feedback_panel,
                scorecard,
                history_state,
                question_index_state,
                question_display,
                progress_display,
                answer_box,
                submit_button,
            ],
        )
        coach_button.click(
            fn=ask_coach,
            inputs=[coach_question, history_state],
            outputs=coach_response,
        )
        coach_question.submit(
            fn=ask_coach,
            inputs=[coach_question, history_state],
            outputs=coach_response,
        )
        final_report_button.click(
            fn=show_final_report,
            inputs=history_state,
            outputs=final_report,
        )
        new_session_button.click(
            fn=start_new_session,
            inputs=[],
            outputs=[
                question_display,
                progress_display,
                answer_box,
                scorecard,
                question_index_state,
                feedback_panel,
                history_state,
                submit_button,
                final_report,
            ],
        )

    return demo


def main():
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing from your .env file")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
    )
    demo = create_demo(client)
    demo.launch(
        inbrowser=True,
        theme=gr.themes.Soft(primary_hue="teal", secondary_hue="cyan"),
        css=APP_CSS,
    )


if __name__ == "__main__":
    main()
