import json

from tools import check_star_structure, detect_filler_words, score_relevance, tools


TOOL_FUNCTIONS = {
    "detect_filler_words": detect_filler_words,
    "check_star_structure": check_star_structure,
    "score_relevance": score_relevance,
}


class EvaluatorAgent:
    def __init__(self, client):
        self.client = client
        self.history = []

    def get_session_summary(self) -> dict[str, object]:
        """Calculate progress from every answer evaluated in this session."""
        return self._summarize_entries(self.history)

    def evaluate_interview(
        self,
        question: str,
        answer: str,
        expected_keywords: list[str] | None = None,
    ) -> dict[str, object]:
        """Evaluate one answer, save it in session history, and provide feedback."""
        keyword_guidance = ""
        if expected_keywords:
            keyword_guidance = (
                " For score_relevance, use these expected question-related "
                f"keywords or concepts: {json.dumps(expected_keywords)}."
            )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an encouraging interview evaluator. Evaluate the "
                    "candidate answer for filler words, STAR structure, and "
                    "relevance to the interview question. Call each of the three "
                    "available tools exactly once. For score_relevance, choose "
                    "important expected keywords or concepts based on the question."
                    + keyword_guidance
                    + " After receiving the tool results, give the candidate "
                    "concise feedback in at most two short sentences and no more "
                    "than 25 words. Mention one strength and one practical improvement."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Interview question: {question}\n"
                    f"Candidate answer: {answer}"
                ),
            },
        ]

        tool_results = {}

        for _ in range(len(TOOL_FUNCTIONS)):
            remaining_tools = [
                tool_name
                for tool_name in TOOL_FUNCTIONS
                if tool_name not in tool_results
            ]
            if not remaining_tools:
                break

            messages.append(
                {
                    "role": "system",
                    "content": (
                        "Call each of these tools that has not been called yet: "
                        + ", ".join(remaining_tools)
                    ),
                }
            )
            response = self.client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=messages,
                tools=tools,
                tool_choice="required",
            )
            message = response.choices[0].message

            if not message.tool_calls:
                raise RuntimeError("The model did not return the required tool call.")

            messages.append(message)

            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                if tool_name not in TOOL_FUNCTIONS:
                    raise RuntimeError(f"Unknown tool requested: {tool_name}")
                if tool_name in tool_results:
                    raise RuntimeError(f"The model called {tool_name} more than once.")

                arguments = json.loads(tool_call.function.arguments)
                if tool_name == "score_relevance" and expected_keywords is not None:
                    arguments["expected_keywords"] = expected_keywords

                print(f"Tool called: {tool_name}({arguments})")
                tool_result = TOOL_FUNCTIONS[tool_name](**arguments)
                print(f"Tool result: {tool_result}")
                tool_results[tool_name] = tool_result

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_result),
                    }
                )

        if len(tool_results) != len(TOOL_FUNCTIONS):
            missing_tools = [
                tool_name
                for tool_name in TOOL_FUNCTIONS
                if tool_name not in tool_results
            ]
            raise RuntimeError(
                f"The model did not call all evaluation tools. Missing: {missing_tools}"
            )

        entry = {
            "question": question,
            "answer": answer,
            "tool_results": tool_results,
            "feedback": None,
        }
        session_so_far = self.history + [entry]
        self.history.append(entry)
        messages.append(
            {
                "role": "system",
                "content": (
                    "Give brief, encouraging feedback in at most two short "
                    "sentences and no more than 25 words. Mention one strength "
                    "and one practical improvement. Do not add a long summary. "
                    "Current session summary: "
                    + json.dumps(self._summarize_entries(session_so_far))
                ),
            }
        )
        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
        )
        entry["feedback"] = response.choices[0].message.content

        return entry

    def _summarize_entries(self, entries: list[dict[str, object]]) -> dict[str, object]:
        """Calculate score statistics for the supplied session entries."""
        if not entries:
            return {
                "answers_evaluated": 0,
                "average_relevance_score": None,
                "weakest_question": None,
                "weakest_relevance_score": None,
            }

        total_score = 0
        weakest_entry = entries[0]

        for entry in entries:
            score = entry["tool_results"]["score_relevance"]["score"]
            total_score += score
            if score < weakest_entry["tool_results"]["score_relevance"]["score"]:
                weakest_entry = entry

        weakest_score = weakest_entry["tool_results"]["score_relevance"]["score"]
        return {
            "answers_evaluated": len(entries),
            "average_relevance_score": round(total_score / len(entries), 1),
            "weakest_question": weakest_entry["question"],
            "weakest_relevance_score": weakest_score,
        }

    def ask_agent(self, question: str) -> str:
        """Answer a progress question using the complete interview session history."""
        if not self.history:
            return (
                "There are no evaluated answers yet. "
                "Answer an interview question first."
            )

        summary = self.get_session_summary()
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an encouraging interview coach. Answer the candidate's "
                    "progress question using only the complete interview history and "
                    "the calculated session summary provided. The average relevance "
                    "and weakest question are calculated from all answers so far; "
                    "state them accurately when relevant. Give concise, practical advice."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Complete interview history:\n"
                    + json.dumps(self.history)
                    + "\nCalculated session summary:\n"
                    + json.dumps(summary)
                    + "\nCandidate's progress question:\n"
                    + question
                ),
            },
        ]
        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
        )
        return response.choices[0].message.content

    def generate_final_report(self) -> str:
        """Create a report using aggregated results from the full interview session."""
        if not self.history:
            return "No answers have been evaluated yet, so there is no report to show."

        summary = self.get_session_summary()
        star_totals = {
            "Situation": 0,
            "Task": 0,
            "Action": 0,
            "Result": 0,
        }
        filler_total = 0

        for entry in self.history:
            results = entry["tool_results"]
            for component in star_totals:
                if results["check_star_structure"]["components"][component]:
                    star_totals[component] += 1
            for count in results["detect_filler_words"]["counts"].values():
                filler_total += count

        weakest_star_component = min(star_totals, key=star_totals.get)
        average_score = summary["average_relevance_score"]
        average_score_display = f"{average_score:g}"
        if average_score >= 80:
            relevance_observation = "Your answers were generally relevant to the questions."
        elif average_score >= 50:
            relevance_observation = "Your answers were partly relevant; adding more question-specific details could improve them."
        else:
            relevance_observation = "Your answers need stronger connections to the questions asked."

        if filler_total:
            filler_observation = (
                f"The evaluator detected {filler_total} filler word"
                f"{'s' if filler_total != 1 else ''} across your answers."
            )
        else:
            filler_observation = "The evaluator did not detect filler words in your answers."

        return (
            "## Interview Performance Report\n\n"
            f"- **Answers evaluated:** {summary['answers_evaluated']}\n"
            f"- **Average relevance score:** {average_score_display}/100\n"
            f"- **Weakest area:** {summary['weakest_question']} "
            f"(relevance: {summary['weakest_relevance_score']}/100)\n\n"
            "### Overall observations\n"
            f"- {relevance_observation}\n"
            f"- STAR components found across answers: "
            + ", ".join(
                f"{component} ({count}/{summary['answers_evaluated']})"
                for component, count in star_totals.items()
            )
            + f". Consider strengthening **{weakest_star_component}** in future examples.\n"
            f"- {filler_observation}\n\n"
            "Keep practicing, especially on the weakest question, and build on the parts of your answers that are already working."
        )
