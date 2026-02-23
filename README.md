# Smart Interview Prep Agent

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
├── Delete existing container if exists
├── Fetch ACR credentials automatically
└── Deploy fresh container with new image

Stage 4: 🔍 Health Verification
├── Wait for container to boot
├── Hit /health endpoint
└── Assert HTTP 200
```

---

## Project Structure

```
Smart-Interview-Prep-Agent/
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
├── images/                     # UI screenshots
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
| `/generate` | POST | Generate questions from JD + resume |
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
git clone https://github.com/your-username/Smart-Interview-Prep-Agent.git
cd Smart-Interview-Prep-Agent

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
docker build -t smart-interview-prep-agent .

docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  smart-interview-prep-agent
```

### Run Tests

```bash
uv run pytest tests/ -v
```

---

## Deploy to Azure

### Prerequisites
- Azure CLI installed and logged in
- Azure Container Registry created
- Azure Container Instance permissions

### Steps

```bash
# Login to your ACR
az acr login --name <your-acr-name>

# Build and push
docker build -t <your-acr-name>.azurecr.io/smart-interview-prep-agent:latest .
docker push <your-acr-name>.azurecr.io/smart-interview-prep-agent:latest

# Deploy to ACI
az container create \
  --resource-group <your-resource-group> \
  --name smart-interview-prep-agent \
  --image <your-acr-name>.azurecr.io/smart-interview-prep-agent:latest \
  --cpu 1 --memory 1.5 \
  --dns-name-label smart-interview-prep-agent \
  --ports 8000 \
  --os-type Linux \
  --environment-variables OPENAI_API_KEY=<your-key>
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key |

---

## Key Design Decisions

**Why ACI over Azure Web App?**
ACI gives a public URL instantly with no App Service Plan required. For a containerized LLM app, ACI is simpler and more cost-effective.

**Why LangGraph over a single LLM call?**
Question generation and answer evaluation are separate concerns with different prompts, context, and output schemas. LangGraph manages shared state cleanly across both agents.

**Why FastAPI serves the frontend?**
Single container, single port, zero infrastructure complexity. No separate frontend server needed.

---

## License

MIT