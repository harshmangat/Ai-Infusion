def detect_filler_words(answer: str) -> dict[str, object]:
    """Detect common filler words in a candidate's answer and return structured results."""
    filler_words = ["um", "uh", "like", "basically"]
    matches = []
    word_count = {}
    current_word = ""

    for character in answer + " ":
        if character.isalnum():
            current_word += character.lower()
        else:
            if current_word in filler_words:
                matches.append(current_word)

                if current_word in word_count:
                    word_count[current_word] += 1
                else:
                    word_count[current_word] = 1

            current_word = ""

    return {
        "has_fillers": len(matches) > 0,
        "filler_words": matches,
        "counts": word_count,
    }


def check_star_structure(answer: str) -> dict[str, object]:
    """Check for simple keyword clues for each part of a STAR answer."""
    words = []
    current_word = ""

    for character in answer.lower() + " ":
        if character.isalnum():
            current_word += character
        else:
            if current_word:
                words.append(current_word)
            current_word = ""

    clues = {
        "Situation": ["situation", "context", "when", "during"],
        "Task": ["task", "goal", "responsible", "needed"],
        "Action": ["action", "created", "built", "led", "implemented"],
        "Result": ["result", "achieved", "improved", "increased", "reduced"],
    }
    components = {}
    present = []
    missing = []

    for component in clues:
        components[component] = False

        for clue in clues[component]:
            if clue in words:
                components[component] = True
                break

        if components[component]:
            present.append(component)
        else:
            missing.append(component)

    return {
        "components": components,
        "present": present,
        "missing": missing,
    }


def score_relevance(
    answer: str, expected_keywords: list[str]
) -> dict[str, object]:
    """Score an answer by counting expected question-related keywords it contains."""
    answer_words = []
    current_word = ""

    for character in answer.lower() + " ":
        if character.isalnum():
            current_word += character
        else:
            if current_word:
                answer_words.append(current_word)
            current_word = ""

    matched_words = []
    missing_words = []

    for keyword in expected_keywords:
        keyword_words = []
        current_word = ""

        for character in keyword.lower() + " ":
            if character.isalnum():
                current_word += character
            else:
                if current_word:
                    keyword_words.append(current_word)
                current_word = ""

        found = False
        start = 0
        while start <= len(answer_words) - len(keyword_words):
            position = 0
            while (
                position < len(keyword_words)
                and answer_words[start + position] == keyword_words[position]
            ):
                position += 1

            if position == len(keyword_words) and len(keyword_words) > 0:
                found = True
                break

            start += 1

        if found:
            matched_words.append(keyword)
        else:
            missing_words.append(keyword)

    if len(expected_keywords) == 0:
        score = 0
    else:
        score = int(len(matched_words) / len(expected_keywords) * 100)

    return {
        "score": score,
        "matched_words": matched_words,
        "missing_words": missing_words,
    }


tools = [
    {
        "type": "function",
        "function": {
            "name": "detect_filler_words",
            "description": (
                "Detect and flag common filler words such as 'um', 'like', "
                "and 'basically' in a candidate's interview answer. Return "
                "the matching words and their counts."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "answer": {
                        "type": "string",
                        "description": "The candidate's interview answer to analyze.",
                    }
                },
                "required": ["answer"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_star_structure",
            "description": (
                "Check whether a behavioral interview answer includes "
                "Situation, Task, Action, and Result. Return which components "
                "appear present or are missing."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "answer": {
                        "type": "string",
                        "description": "The candidate's behavioral interview answer.",
                    }
                },
                "required": ["answer"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "score_relevance",
            "description": (
                "Score a candidate's answer from 0 to 100 by identifying "
                "expected keywords or concepts relevant to the interview "
                "question and checking which are present in the answer. "
                "Provide the question-related expected keywords as a list."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "answer": {
                        "type": "string",
                        "description": "The candidate's answer to the question.",
                    },
                    "expected_keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "Important keywords or concepts expected in an "
                            "answer to the interview question."
                        ),
                    },
                },
                "required": ["answer", "expected_keywords"],
            },
        },
    },
]
