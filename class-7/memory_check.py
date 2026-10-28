import json

from agent import EvaluatorAgent


STRONG_QUESTION = "Describe a time you improved a team process."
STRONG_ANSWER = (
    "I organized the team, improved our process, and the result was faster service."
)
WEAK_QUESTION = "How do you analyze quarterly financial forecasts?"
WEAK_ANSWER = "I enjoy working with people and learning new things."
FOLLOW_UP_QUESTION = "Tell me about collaborating with a team."
FOLLOW_UP_ANSWER = "I collaborated with the team to complete our project goals."


class FakeToolCall:
    def __init__(self, tool_name: str, arguments: dict[str, object]):
        self.id = f"call_{tool_name}"
        self.function = type(
            "Function",
            (),
            {
                "name": tool_name,
                "arguments": json.dumps(arguments),
            },
        )()


class FakeMessage:
    def __init__(self, tool_calls=None, content=None):
        self.tool_calls = tool_calls
        self.content = content


class FakeResponse:
    def __init__(self, message: FakeMessage):
        self.choices = [type("Choice", (), {"message": message})()]


class FakeCompletions:
    def create(self, **request):
        if "tools" not in request:
            prompt = request["messages"][-1]["content"]
            if "Complete interview history:" in prompt:
                marker = "\nCalculated session summary:\n"
                summary_start = prompt.index(marker) + len(marker)
                summary_end = prompt.index("\nCandidate's progress question:\n")
                summary = json.loads(prompt[summary_start:summary_end])
                response = (
                    f"Your weakest area is: {summary['weakest_question']} "
                    f"(relevance score: {summary['weakest_relevance_score']})."
                )
            else:
                response = "Good effort. Keep practicing."
            return FakeResponse(FakeMessage(content=response))

        messages = request["messages"]
        user_prompt = next(
            message["content"]
            for message in messages
            if isinstance(message, dict) and message.get("role") == "user"
        )
        question = user_prompt.split("Interview question: ", 1)[1].split(
            "\nCandidate answer:", 1
        )[0]
        answer = user_prompt.split("\nCandidate answer:", 1)[1]
        remaining_tools = messages[-1]["content"].split(": ", 1)[1].split(", ")
        tool_name = remaining_tools[0]

        if tool_name in ["detect_filler_words", "check_star_structure"]:
            arguments = {"answer": answer}
        else:
            expected_keywords = {
                STRONG_QUESTION: ["team", "process", "result"],
                WEAK_QUESTION: ["financial", "forecast", "analysis"],
                FOLLOW_UP_QUESTION: ["collaborated", "team"],
            }[question]
            arguments = {
                "answer": answer,
                "expected_keywords": expected_keywords,
            }

        return FakeResponse(
            FakeMessage([FakeToolCall(tool_name, arguments)])
        )


class FakeClient:
    def __init__(self):
        self.chat = type(
            "Chat",
            (),
            {"completions": FakeCompletions()},
        )()


def main():
    agent = EvaluatorAgent(FakeClient())

    print("1. Evaluating a strong answer...")
    agent.evaluate_interview(STRONG_QUESTION, STRONG_ANSWER)

    print("\n2. Evaluating a deliberately weak answer...")
    agent.evaluate_interview(WEAK_QUESTION, WEAK_ANSWER)

    print("\n3. Evaluating a strong follow-up to ensure the latest answer is not weakest...")
    agent.evaluate_interview(FOLLOW_UP_QUESTION, FOLLOW_UP_ANSWER)

    print("\n4. Asking the agent about session performance...")
    meta_answer = agent.ask_agent("What's my weakest area?")
    print(meta_answer)

    summary = agent.get_session_summary()
    print(f"\nSession summary: {summary}")

    assert summary["answers_evaluated"] == 3, summary
    assert summary["weakest_question"] == WEAK_QUESTION, summary
    assert summary["weakest_relevance_score"] == 0, summary
    assert FOLLOW_UP_QUESTION != summary["weakest_question"]
    assert WEAK_QUESTION in meta_answer, (
        "The agent did not identify the deliberately weak question as the weakest area."
    )

    print("\nPASS: The agent identified the lowest-scoring question from session history.")


if __name__ == "__main__":
    main()
