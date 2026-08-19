from fastapi import HTTPException

from ..schemas.models import QuizRequest
from .question_validation import generate_validated_questions
from .rag import (
    build_rag_index,
    build_retrieval_queries,
    format_retrieved_context,
    retrieve_context,
)
from .topics import get_topic_source


def question_type_instruction(
    question_type: str,
):
    return {
        "MCQ":
            "Generate ONLY Multiple Choice Questions.",

        "True / False":
            "Generate ONLY True / False questions.",

        "Short Answer":
            "Generate ONLY Short Answer questions.",

        "Mixed":
            (
                "Generate a balanced mixture of "
                "MCQ, True / False, and Short Answer questions."
            ),
    }[question_type]


def difficulty_instruction(
    difficulty: str,
):
    return {
        "Easy":
            "Test basic concepts, definitions and direct understanding.",

        "Medium":
            "Test conceptual understanding, comparisons, applications and important ideas.",

        "Hard":
            "Test deeper reasoning, relationships, applications, edge cases and detailed understanding.",

        "Mixed":
            "Use a mixture of easy, medium and hard questions.",
    }[difficulty]


def build_topic_prompt(
    req: QuizRequest,
    topic: str,
):
    if req.question_type == "MCQ":

        type_rules = """
Every question MUST be an MCQ.

The "type" MUST be exactly:
"MCQ"

The "options" field MUST contain exactly 4 unique options.

The "answer" MUST exactly match one of the options.

DO NOT generate True / False questions.

DO NOT generate Short Answer questions.
"""

    elif req.question_type == "True / False":

        type_rules = """
Every question MUST be a True / False question.

The "type" MUST be exactly:
"True / False"

The "options" field MUST be exactly:
["True", "False"]

The "answer" MUST be exactly:
"True"
or
"False"

DO NOT generate MCQ questions.

DO NOT generate Short Answer questions.
"""

    elif req.question_type == "Short Answer":

        type_rules = """
Every question MUST be a Short Answer question.

The "type" MUST be exactly:
"Short Answer"

The "options" field MUST be exactly:
[]

The "answer" MUST contain a concise,
correct and NON-EMPTY answer.

DO NOT generate MCQ questions.

DO NOT generate True / False questions.
"""

    else:

        type_rules = """
Generate a balanced mixture of:

- MCQ
- True / False
- Short Answer

MCQ:
- Exactly 4 unique options.
- Answer must match an option.

True / False:
- Options must be ["True", "False"].
- Answer must be exactly "True" or "False".

Short Answer:
- Options must be [].
- Answer must be non-empty.
"""

    return f"""
You are QuizMate AI.

Create EXACTLY {req.count} NEW educational quiz questions.

TOPIC:
{topic}

QUESTION TYPE:
{question_type_instruction(req.question_type)}

DIFFICULTY:
{difficulty_instruction(req.difficulty)}

============================================================
CRITICAL QUESTION TYPE RULE
============================================================

The selected question type is:

"{req.question_type}"

{type_rules}

============================================================
GENERAL RULES
============================================================

1. Questions must be specifically about the requested topic.

2. Do not repeat questions.

3. Make every question meaningfully different.

4. Generate EXACTLY {req.count} questions.

5. Every question MUST contain:

   type
   question
   options
   answer
   explanation
   keywords

6. Never omit any field.

7. Every answer MUST be non-empty.

8. Generate educationally accurate questions.

9. Do not use markdown.

10. Do not return ```json.

11. Return ONLY valid JSON.

12. Generate new questions every time.

============================================================
FINAL VALIDATION BEFORE RESPONSE
============================================================

Before returning the JSON, verify:

- Exactly {req.count} questions exist.
- Every question uses the selected type.
- No question uses a different type.
- Every answer is non-empty.
- All required fields exist.

============================================================
OUTPUT FORMAT
============================================================

Return:

{{
  "questions": [
    {{
      "type": "{req.question_type}",
      "question": "Question text",
      "options": [],
      "answer": "Correct answer",
      "explanation": "Brief explanation.",
      "keywords": []
    }}
  ]
}}
"""


# ============================================================
# QUIZ GENERATION
# ============================================================

def generate_questions(
    req: QuizRequest,
):

    # ========================================================
    # TOPIC-ONLY MODE
    #
    # IMPORTANT:
    # Direct topic mode does NOT search data/topics/*.txt.
    #
    # Example:
    # topic = "iot"
    #
    # It directly sends "iot" to Gemini.
    # ========================================================

    if req.topic and not req.source_text:

        topic = req.topic.strip()

        if len(topic) < 2:
            raise HTTPException(
                status_code=400,
                detail="Please enter a valid topic.",
            )

        prompt = build_topic_prompt(
            req,
            topic,
        )

        return generate_validated_questions(
            prompt=prompt,
            requested_count=req.count,
            selected_type=req.question_type,
            mode="TOPIC",
            max_attempts=3,
        )

    # ========================================================
    # DOCUMENT / RAG MODE
    # ========================================================

    if req.source_text:

        source_text = (
            req.source_text.strip()
        )

        source_name = (
            req.source_name
            or "Uploaded Document"
        )

    elif req.topic:

        # This is kept for EXISTING topic-file functionality.
        # Direct topic mode above returns before reaching here.
        source_name, source_text = (
            get_topic_source(
                req.topic
            )
        )

    else:

        raise HTTPException(
            status_code=400,
            detail=(
                "Please upload a document "
                "or select a topic."
            ),
        )

    if len(source_text) < 100:

        raise HTTPException(
            status_code=400,
            detail=(
                "The selected document/topic "
                "does not contain enough study material."
            ),
        )

    index = build_rag_index(
        source_text,
        source_name,
    )

    retrieval_queries = (
        build_retrieval_queries(req)
    )

    top_k = min(
        max(
            8,
            req.count // 2 + 5,
        ),
        15,
        len(index["chunks"]),
    )

    retrieved = retrieve_context(
        index,
        retrieval_queries,
        top_k=top_k,
    )

    if not retrieved:

        raise HTTPException(
            status_code=502,
            detail=(
                "RAG could not retrieve "
                "relevant content."
            ),
        )

    context = format_retrieved_context(
        retrieved
    )

    # ========================================================
    # DOCUMENT TYPE RULES
    # ========================================================

    if req.question_type == "MCQ":

        document_type_rules = """
Generate ONLY MCQ questions.

Every "type" MUST be exactly "MCQ".

Each question MUST contain exactly 4 unique options.

The answer MUST exactly match one option.

Do NOT generate True / False.

Do NOT generate Short Answer.
"""

    elif req.question_type == "True / False":

        document_type_rules = """
Generate ONLY True / False questions.

Every "type" MUST be exactly "True / False".

Every question MUST have:

"options": ["True", "False"]

The answer MUST be exactly "True" or "False".

Do NOT generate MCQ.

Do NOT generate Short Answer.
"""

    elif req.question_type == "Short Answer":

        document_type_rules = """
Generate ONLY Short Answer questions.

Every "type" MUST be exactly "Short Answer".

Every question MUST have:

"options": []

Every answer MUST contain a concise,
correct and non-empty answer.

Do NOT generate MCQ.

Do NOT generate True / False.
"""

    else:

        document_type_rules = """
Generate a balanced mixture of:

- MCQ
- True / False
- Short Answer

MCQ:
- Exactly 4 unique options.
- Answer must match one option.

True / False:
- Options must be ["True", "False"].
- Answer must be exactly "True" or "False".

Short Answer:
- Options must be [].
- Answer must be non-empty.
"""

    prompt = f"""
You are QuizMate AI.

Generate EXACTLY {req.count} NEW quiz questions.

Use ONLY the retrieved study context.

QUESTION TYPE:
{question_type_instruction(req.question_type)}

DIFFICULTY:
{difficulty_instruction(req.difficulty)}

============================================================
STRICT QUESTION TYPE RULES
============================================================

{document_type_rules}

============================================================
DOCUMENT RULES
============================================================

1. Use ONLY information explicitly supported by the context.

2. Do NOT use outside knowledge.

3. Do NOT invent facts.

4. Do NOT repeat questions.

5. Make every question meaningfully different.

6. Every answer must be supported by the context.

7. Every question MUST contain:

   type
   question
   options
   answer
   explanation
   keywords

8. Never omit any field.

9. Every answer MUST be non-empty.

10. Return ONLY valid JSON.

11. Do not return markdown.

12. Do not return ```json.

============================================================
FINAL VALIDATION
============================================================

Before returning the JSON, verify:

- Exactly {req.count} questions exist.
- Every question uses the selected type.
- No question has a different type.
- Every answer is non-empty.
- All required fields exist.

============================================================
OUTPUT
============================================================

Return:

{{
  "questions": [
    {{
      "type": "{req.question_type}",
      "question": "Question",
      "options": [],
      "answer": "Correct answer",
      "explanation": "Explanation from context.",
      "keywords": []
    }}
  ]
}}

============================================================
RETRIEVED STUDY CONTEXT
============================================================

<RETRIEVED_CONTEXT>
{context}
</RETRIEVED_CONTEXT>
"""

    return generate_validated_questions(
        prompt=prompt,
        requested_count=req.count,
        selected_type=req.question_type,
        mode="DOCUMENT",
        max_attempts=3,
    )
