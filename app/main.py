from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from app.agents.state import InterviewState
from app.agents.question_generator import generate_questions
from app.agents.answer_evaluator import evaluate_answer, compute_final_report

load_dotenv()

app = FastAPI(title="AI Interview Coach")

# ── In-memory session store (single user, demo-grade) ──────────────────────────
# For production: replace with Redis or DB
sessions: dict[str, InterviewState] = {}


# ── Request / Response schemas ─────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    session_id: str
    job_description: str
    resume: str


class AnswerRequest(BaseModel):
    session_id: str
    question_id: int
    answer: str


class ReportRequest(BaseModel):
    session_id: str


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "smart-interview-prep-agent", "version": "1.0.0"}


@app.post("/generate")
def generate(req: GenerateRequest):
    """Step 1: Generate interview questions from JD + Resume."""
    state: InterviewState = {
        "job_description": req.job_description,
        "resume": req.resume,
        "questions": [],
        "answers": [],
        "evaluations": [],
        "overall_score": None,
        "grade": None,
        "top_improvements": []
    }

    updated = generate_questions(state)
    state.update(updated)
    sessions[req.session_id] = state

    return {"questions": state["questions"]}


@app.post("/evaluate")
def evaluate(req: AnswerRequest):
    """Step 2: Evaluate a single answer. Call once per question."""
    state = sessions.get(req.session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found. Generate questions first.")

    question = next((q for q in state["questions"] if q["id"] == req.question_id), None)
    if not question:
        raise HTTPException(status_code=404, detail=f"Question ID {req.question_id} not found.")

    evaluation = evaluate_answer(question, req.answer, state["job_description"])

    state["answers"].append({"question_id": req.question_id, "answer": req.answer})
    state["evaluations"].append(evaluation)
    sessions[req.session_id] = state

    return evaluation


@app.post("/report")
def report(req: ReportRequest):
    """Step 3: Generate final report after all questions answered."""
    state = sessions.get(req.session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found.")

    if len(state["evaluations"]) == 0:
        raise HTTPException(status_code=400, detail="No evaluations found. Answer questions first.")

    updated = compute_final_report(state)
    state.update(updated)
    sessions[req.session_id] = state

    return {
        "overall_score": state["overall_score"],
        "grade": state["grade"],
        "top_improvements": state["top_improvements"],
        "questions": state["questions"],
        "evaluations": state["evaluations"]
    }


# ── Serve frontend ─────────────────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def root():
    return FileResponse("app/static/index.html")