from typing_extensions import TypedDict


class InterviewState(TypedDict):
    # Inputs
    job_description: str
    resume: str

    # Generated questions: list of dicts {id, type, question}
    questions: list[dict]

    # User answers: list of dicts {question_id, answer}
    answers: list[dict]

    # Evaluations: list of dicts {question_id, score, strengths, gaps, ideal_structure}
    evaluations: list[dict]

    # Derived
    overall_score: float | None
    grade: str | None
    top_improvements: list[str]