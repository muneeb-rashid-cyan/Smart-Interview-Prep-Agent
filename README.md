# AI Interview Coach — LLMOps

An AI-powered interview preparation tool built with LangGraph and GPT-4o. Paste your resume and a job description — the agent generates role-specific interview questions, evaluates your answers, and returns scored feedback with improvement suggestions.

---

## What It Does

```
User pastes Resume + Job Description
        ↓
Question Generator Agent
├── Identifies skill gaps between resume and JD
├── Generates 5-7 targeted questions
│   ├── Technical (based on JD requirements)
│   ├── Behavioural (based on experience gaps)
│   ├── Situational (based on the role)
│   └── Motivation
        ↓
User answers each question
        ↓
Answer Evaluator Agent
├── Scores each answer (1-10)
├── Identifies strengths
├── Identifies what was missing
└── Suggests ideal answer structure
        ↓
Final Report
├── Overall score + grade (A/B/C/D)
├── Per-question breakdown
└── Top 3 areas to improve
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Agent Framework** | LangGraph (StateGraph) |
| **LLM** | OpenAI GPT-4o via `init_chat_model` |
| **API Framework** | FastAPI + Pydantic v2 |
| **Frontend** | HTML + Vanilla JS (served by FastAPI) |
| **Dependency Management** | uv |
| **Containerization** | Docker |
| **Container Registry** | Azure Container Registry (ACR) |
| **Deployment** | Azure Container Instance (ACI) |
| **CI/CD** | Azure DevOps Pipelines (4-stage) |

---

## CI/CD Pipeline

4-stage pipeline triggered on every push to `master`:

```
Stage 1: 🧪 Quality Gate
├── Install dependencies via uv
├── Ruff lint check
└── Pytest

Stage 2: 🐳 Build & Push to ACR
├── Login to Azure Container Registry
├── Docker build
└── Push :latest + :buildId to ACR

Stage 3: 🚀 Deploy to ACI
├── Delete existing container (if exists)
├── Fetch ACR credentials automatically
└── Create fresh ACI container with new image

Stage 4: 🔍 Health Verification
├── Wait for container to boot
├── Hit /health endpoint
└── Assert HTTP 200 — print live URL
```

---

## Project Structure

```
ai-interview-coach-llmops/
├── agents/
│   ├── question_generator.py   # generates interview questions
│   └── answer_evaluator.py     # scores answers + feedback
├── graph/
│   ├── state.py                # shared InterviewState TypedDict
│   └── pipeline.py             # LangGraph StateGraph wiring
├── api/
│   └── main.py                 # FastAPI endpoints
├── static/
│   ├── index.html              # input page
│   ├── interview.html          # question/answer page
│   └── report.html             # final score report
├── models/
│   └── schemas.py              # Pydantic request/response models
├── tests/
│   └── test_api.py
├── Dockerfile
├── azure-pipelines.yml
├── pyproject.toml
└── README.md
```

---

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Serves the web UI |
| `/health` | GET | Health check |
| `/generate` | POST | Generate interview questions from JD + resume |
| `/evaluate` | POST | Score and give feedback on an answer |
| `/report` | POST | Generate final report from all answers |

---

## Local Setup

### Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) installed
- OpenAI API key

### Run Locally

```bash
git clone https://github.com/your-username/ai-interview-coach-llmops.git
cd ai-interview-coach-llmops

uv venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\Activate.ps1

uv sync

cp .env.example .env
# Add your OPENAI_API_KEY to .env

uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000` in your browser.

### Run with Docker

```bash
docker build -t ai-interview-coach .

docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  ai-interview-coach
```

### Run Tests

```bash
uv run pytest tests/ -v
```

---

## Deploy to Azure (Manual)

```bash
# Login to ACR
az acr login --name costforecastingmlopsacr

# Build and push
docker build -t costforecastingmlopsacr.azurecr.io/interview-coach-app:latest .
docker push costforecastingmlopsacr.azurecr.io/interview-coach-app:latest

# Deploy to ACI
az container create \
  --resource-group mirlin-ml-dev \
  --name interview-coach-app \
  --image costforecastingmlopsacr.azurecr.io/interview-coach-app:latest \
  --cpu 1 --memory 1.5 \
  --dns-name-label interview-coach-app \
  --ports 8000 \
  --os-type Linux \
  --location canadacentral
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key |

---

## Key Design Decisions

**Why ACI over Azure Web App?**
ACI gives a public URL instantly with no App Service Plan required. For a containerized LLM app with variable load, ACI is simpler and more cost-effective for a portfolio project.

**Why LangGraph over a single LLM call?**
The interview flow has distinct steps — question generation and answer evaluation are separate concerns with different prompts, different context requirements, and different output schemas. LangGraph manages the shared state cleanly across both agents.

**Why FastAPI serves the frontend?**
Single container, single port, zero infrastructure complexity. FastAPI serves HTML files directly via `StaticFiles` — no separate frontend server needed.

---

## License

MIT