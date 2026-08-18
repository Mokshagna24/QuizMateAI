from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class AuthIn(BaseModel):
    name: Optional[str] = None
    email: str
    password: str


class TokenOut(BaseModel):
    token: str
    user: dict


class YouTubeRequest(BaseModel):
    url: str


class QuizRequest(BaseModel):
    source_text: Optional[str] = None
    source_name: Optional[str] = None
    topic: Optional[str] = None

    count: int = Field(
        default=10,
        ge=1,
        le=20,
    )

    question_type: Literal[
        "MCQ",
        "True / False",
        "Short Answer",
        "Mixed",
    ]

    difficulty: Literal[
        "Easy",
        "Medium",
        "Hard",
        "Mixed",
    ]


class QuizQuestion(BaseModel):
    type: Literal[
        "MCQ",
        "True / False",
        "Short Answer",
    ]

    question: str

    options: List[str] = Field(
        default_factory=list
    )

    answer: str

    explanation: str

    keywords: List[str] = Field(
        default_factory=list
    )

    @field_validator("type", mode="before")
    @classmethod
    def normalize_type(cls, value):
        if not isinstance(value, str):
            return value

        value = value.strip()

        normalized = value.lower().replace(" ", "")

        if normalized in {
            "true/false",
            "truefalse",
        }:
            return "True / False"

        if normalized == "mcq":
            return "MCQ"

        if normalized in {
            "shortanswer",
            "short-answer",
        }:
            return "Short Answer"

        return value


class QuizOut(BaseModel):
    questions: List[QuizQuestion]


class SubmitRequest(BaseModel):
    source_name: str
    difficulty: str
    questions: List[QuizQuestion]
    answers: dict


class SummaryRequest(BaseModel):
    text: str = Field(
        min_length=20
    )

    mode: Literal[
        "Quick Summary",
        "Detailed Summary",
        "Exam Revision Notes",
        "Explain Simply",
    ]
