from typing import List

from fastapi import HTTPException

from ..schemas.models import QuizQuestion
from .json_utils import parse_ai_json
from .gemini import call_ai


def normalize_question_item(
    item: dict,
):
    """
    Normalize common Gemini mistakes before Pydantic validation.
    """

    if not isinstance(item, dict):
        raise ValueError(
            "Question is not a JSON object."
        )

    item = dict(item)

    # -------------------------
    # Normalize type
    # -------------------------

    raw_type = item.get(
        "type",
        "",
    )

    if isinstance(raw_type, str):
        normalized_type = (
            raw_type
            .strip()
            .lower()
            .replace(" ", "")
        )

        if normalized_type in {
            "true/false",
            "truefalse",
        }:
            item["type"] = "True / False"

        elif normalized_type == "mcq":
            item["type"] = "MCQ"

        elif normalized_type in {
            "shortanswer",
            "short-answer",
        }:
            item["type"] = "Short Answer"

    # -------------------------
    # Options
    # -------------------------

    options = item.get(
        "options",
        None,
    )

    if not isinstance(options, list):
        options = []

    item["options"] = [
        str(option).strip()
        for option in options
    ]

    # True/False always gets options
    if item.get("type") == "True / False":
        item["options"] = [
            "True",
            "False",
        ]

    # Short Answer always gets empty options
    if item.get("type") == "Short Answer":
        item["options"] = []

    # -------------------------
    # Keywords
    # -------------------------

    keywords = item.get(
        "keywords",
        [],
    )

    if not isinstance(keywords, list):
        keywords = []

    item["keywords"] = [
        str(k).strip()
        for k in keywords
        if str(k).strip()
    ]

    # -------------------------
    # Required strings
    # -------------------------

    item["question"] = str(
        item.get(
            "question",
            "",
        )
    ).strip()

    item["answer"] = str(
        item.get(
            "answer",
            "",
        )
    ).strip()

    item["explanation"] = str(
        item.get(
            "explanation",
            "",
        )
    ).strip()

    return item


# ============================================================
# QUESTION VALIDATION
# ============================================================

def validate_questions(
    items,
    requested_count: int,
    selected_type: str,
):
    if not isinstance(items, list):
        raise ValueError(
            "AI did not return a questions list."
        )

    validated = []
    seen = set()

    for raw_item in items:

        try:
            normalized = normalize_question_item(
                raw_item
            )

            # =================================================
            # MIXED MODE
            # =================================================

            if selected_type == "Mixed":

                if normalized.get("type") not in {
                    "MCQ",
                    "True / False",
                    "Short Answer",
                }:
                    print(
                        "Skipping unsupported "
                        "question type:",
                        normalized.get("type"),
                    )
                    continue

            # =================================================
            # STRICT SINGLE TYPE MODE
            # =================================================

            else:

                if normalized.get("type") != selected_type:
                    print(
                        "QUESTION TYPE SKIPPED:",
                        normalized.get("type"),
                        "| EXPECTED:",
                        selected_type,
                    )
                    continue

            question = QuizQuestion(
                **normalized
            )

        except Exception as e:
            print(
                "QUESTION VALIDATION SKIPPED:",
                repr(e),
            )
            continue

        question_key = " ".join(
            question.question
            .lower()
            .split()
        )

        if not question_key:
            continue

        if question_key in seen:
            print(
                "Skipping duplicate question."
            )
            continue

        # ====================================================
        # MCQ
        # ====================================================

        if question.type == "MCQ":

            if len(question.options) != 4:
                print(
                    "Skipping MCQ: "
                    "must have exactly 4 options."
                )
                continue

            normalized_options = [
                option.strip().lower()
                for option in question.options
            ]

            if len(
                set(normalized_options)
            ) != 4:
                print(
                    "Skipping MCQ: "
                    "duplicate options."
                )
                continue

            if not question.answer.strip():
                print(
                    "Skipping MCQ: "
                    "answer is empty."
                )
                continue

            # Gemini may return the correct MCQ answer as either:
            # 1) the option text, or
            # 2) a 1-based option number such as "1", "2", "3", "4".
            # Normalize both forms to the actual option text so the
            # existing scoring/frontend contract remains unchanged.

            answer_value = question.answer.strip()

            if answer_value in {"1", "2", "3", "4"}:
                answer_index = int(answer_value) - 1
                question.answer = question.options[answer_index]

                print(
                    f"Normalized MCQ numeric answer {answer_value} "
                    f"to option {answer_index + 1}."
                )

            elif answer_value.lower() in normalized_options:
                # Preserve the existing answer text, normalized only by
                # matching it to the canonical option spelling.

                answer_index = normalized_options.index(
                    answer_value.lower()
                )

                question.answer = question.options[answer_index]

            else:
                print(
                    "Skipping MCQ: "
                    "answer is not one of options."
                )
                continue

        # ====================================================
        # TRUE / FALSE
        # ====================================================

        elif question.type == "True / False":

            if (
                question.answer
                .strip()
                .lower()
                not in {
                    "true",
                    "false",
                }
            ):
                print(
                    "Skipping True/False: "
                    "answer must be True or False."
                )
                continue

            question.options = [
                "True",
                "False",
            ]

        # ====================================================
        # SHORT ANSWER
        # ====================================================

        elif question.type == "Short Answer":

            if not question.answer.strip():
                print(
                    "Skipping Short Answer: "
                    "answer is empty."
                )
                continue

            question.options = []

        # ====================================================
        # UNKNOWN TYPE
        # ====================================================

        else:

            print(
                "Skipping unsupported question type:",
                question.type,
            )

            continue

        seen.add(question_key)

        validated.append(question)

        if len(validated) >= requested_count:
            break

    return validated


# ============================================================
# ROBUST AI QUESTION GENERATION
# ============================================================

def generate_validated_questions(
    prompt: str,
    requested_count: int,
    selected_type: str,
    mode: str,
    max_attempts: int = 3,
):
    """
    Ask Gemini for a quiz and retry when the model returns
    malformed, incomplete, duplicate, or wrong-type questions.

    This keeps the existing validation rules but avoids failing
    immediately when Gemini produces only a few valid questions.
    """

    last_valid_count = 0
    last_error = ""

    for attempt in range(1, max_attempts + 1):
        retry_instruction = ""

        if attempt > 1:
            retry_instruction = f"""

IMPORTANT RETRY:
This is retry {attempt} of {max_attempts}.
The previous response did not contain enough valid questions.
Generate a COMPLETE replacement set of exactly {requested_count}
questions.

Do not copy invalid questions from the previous attempt.
Be extremely strict about the requested question type.
For MCQ, use exactly 4 unique options and make the answer exactly
match one option.
For True / False, use only True or False and options exactly
["True", "False"].
For Short Answer, use an empty options array and a non-empty answer.
Return ONLY the JSON object.
"""

        try:
            raw = call_ai(prompt + retry_instruction)
            parsed = parse_ai_json(raw)

            items = (
                parsed.get("questions", [])
                if isinstance(parsed, dict)
                else parsed
            )

            validated = validate_questions(
                items,
                requested_count,
                selected_type,
            )

            last_valid_count = len(validated)

            if len(validated) >= requested_count:
                print(
                    f"{mode} QUIZ SUCCESS: "
                    f"{len(validated)} valid questions "
                    f"on attempt {attempt}."
                )
                return validated[:requested_count]

            last_error = (
                f"Gemini returned {len(validated)} valid "
                f"questions out of {requested_count}."
            )

            print(
                f"{mode} QUIZ RETRY {attempt}: "
                f"{last_error}"
            )

        except HTTPException:
            raise

        except Exception as exc:
            last_error = str(exc)

            print(
                f"{mode} QUIZ RETRY {attempt}: "
                f"AI response could not be parsed: {exc!r}"
            )

    raise HTTPException(
        status_code=502,
        detail=(
            f"Gemini generated only {last_valid_count} valid "
            f"{selected_type} questions out of {requested_count} "
            f"after {max_attempts} attempts. "
            "Please try again."
        ),
    )