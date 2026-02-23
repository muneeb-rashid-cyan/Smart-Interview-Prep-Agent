from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain.chat_models import init_chat_model
from app.agents.state import InterviewState

load_dotenv()

llm = init_chat_model("gpt-4o-2024-08-06", temperature=0.3)


class Question(BaseModel):
    id: int
    type: str = Field(description="One of: technical, behavioural, situational, culture")
    question: str


class QuestionList(BaseModel):
    questions: list[Question] = Field(description="List of 5-7 interview questions")


structured_llm = llm.with_structured_output(QuestionList)


def generate_questions(state: InterviewState) -> dict:
    """
    LangGraph node: reads JD + resume, generates 5-7 structured interview questions.
    """
    result: QuestionList = structured_llm.invoke([
        {
            "role": "system",
            "content": """You are an expert technical interviewer. Given a job description and a candidate's resume:
1. Identify skill gaps between what the JD requires and what the resume shows.
2. Generate exactly 5-7 interview questions in this breakdown:
   - 2 Technical questions (based on JD tech requirements)
   - 2 Behavioural questions (targeting experience gaps)
   - 2 Situational questions (role-specific scenarios)
   - 1 Culture/motivation question
Return structured JSON only."""
        },
        {
            "role": "user",
            "content": f"JOB DESCRIPTION:\n{state['job_description']}\n\nRESUME:\n{state['resume']}"
        }
    ])

    return {"questions": [q.model_dump() for q in result.questions]}