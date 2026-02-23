from pydantic import BaseModel, Field
from langchain.chat_models import init_chat_model
from app.agents.state import InterviewState

llm = init_chat_model("gpt-4o-2024-08-06", temperature=0)


class Evaluation(BaseModel):
    question_id: int
    score: int = Field(ge=1, le=10, description="Score from 1 to 10")
    strengths: list[str] = Field(description="What the candidate did well")
    gaps: list[str] = Field(description="What was missing or could be improved")
    ideal_structure: str = Field(description="How an ideal answer would be structured")


structured_llm = llm.with_structured_output(Evaluation)


def evaluate_answer(question: dict, answer: str, job_description: str) -> dict:
    """
    Evaluates a single answer. Called per question from the FastAPI route.
    Not a LangGraph node — invoked directly since evaluation is per-answer.
    """
    result: Evaluation = structured_llm.invoke([
        {
            "role": "system",
            "content": """You are a strict but fair interview coach. Evaluate the candidate's answer to an interview question.
Consider the job description context when scoring.
Score from 1-10 where:
  1-3: Poor — missing key points, vague
  4-6: Average — some good points but incomplete
  7-8: Good — solid answer with minor gaps
  9-10: Excellent — comprehensive, structured, role-relevant

Return structured JSON only."""
        },
        {
            "role": "user",
            "content": f"""JOB DESCRIPTION CONTEXT:
{job_description}

QUESTION (type: {question['type']}):
{question['question']}

CANDIDATE'S ANSWER:
{answer}"""
        }
    ])

    return result.model_dump()


def compute_final_report(state: InterviewState) -> dict:
    """
    LangGraph node: computes overall score, grade, and top improvement areas from all evaluations.
    """
    evaluations = state["evaluations"]
    scores = [e["score"] for e in evaluations]
    overall = round((sum(scores) / (len(scores) * 10)) * 100, 1)

    if overall >= 85:
        grade = "A"
    elif overall >= 70:
        grade = "B"
    elif overall >= 55:
        grade = "C"
    else:
        grade = "D"

    # Collect all gaps and deduplicate top 3
    all_gaps = []
    for e in evaluations:
        all_gaps.extend(e["gaps"])

    # Ask LLM to summarize top 3 improvement areas
    summary_llm = llm
    response = summary_llm.invoke([
        {
            "role": "system",
            "content": "You are an interview coach. Given a list of feedback gaps from an interview, return the top 3 most important areas the candidate should improve. Be concise, one sentence each. Return as a plain numbered list."
        },
        {
            "role": "user",
            "content": "\n".join(f"- {g}" for g in all_gaps)
        }
    ])

    improvements = [
        line.strip().lstrip("123. ")
        for line in response.content.strip().split("\n")
        if line.strip()
    ][:3]

    return {
        "overall_score": overall,
        "grade": grade,
        "top_improvements": improvements
    }