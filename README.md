# Codebase Reader API

## 1) Project Title
**Codebase Reader API**

## 2) Description
Codebase Reader API is a FastAPI server that:
- accepts a GitHub repository URL,
- clones and analyzes the repository,
- generates embeddings for code chunks,
- stores metadata/embeddings in Supabase,
- and provides RAG-based chat responses about the codebase via streaming.

## 3) Features
- User registration and profile bootstrap
- GitHub repository ingestion
- Repository tree fetch
- Repository quality score storage/retrieval
- Code chunk embedding generation (Hugging Face Inference)
- Vector search via Supabase RPC (`semantic`)
- Thread-based chat and message history
- SSE streaming responses for chatbot output
- CORS support for frontend integration

## 4) Tech Stack
- **Backend:** FastAPI, Uvicorn
- **LLM / RAG:** LangChain, LangGraph, Google Gemini (via `langchain-google-genai`),LangSmith
- **Embeddings:** Hugging Face Inference API (`BAAI/bge-small-en`)
- **Database:** Supabase (Postgres + vector/search RPC)
- **Repo handling:** GitPython + GitHub REST API
- **Language:** Python 3.13+

## 5) Installation Steps

### Option A: Using `uv` (recommended)
1. Clone this repository.
2. Create and sync environment:
	 - `uv venv`
	 - `uv sync`
3. Activate virtual environment:
	 - **Windows (PowerShell):** `.venv\Scripts\Activate.ps1`
	 - **macOS/Linux:** `source .venv/bin/activate`

### Option B: Using `pip`
1. Create virtual environment:
	 - `python -m venv .venv`
2. Activate virtual environment.
3. Install dependencies:
	 - `pip install -e .`

## 6) Environment Variables Setup (`.env` example)
Create a `.env` file in project root.

```env
# LLM
GOOGLE_API_KEY=your_google_api_key

# Embeddings
HUGGINGFACEHUB_ACCESS_TOKEN=your_huggingface_token

# GitHub API (for repo tree/details)
GITHUB_TOKEN=your_github_token

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_service_or_anon_key

# Frontend CORS origin
FRONTEND_URL=http://localhost:3000
```

> Note: `env_sample.txt` currently includes only a subset of required variables.

## 7) API Endpoints

Base URL (local): `http://127.0.0.1:8000`

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health/status message |
| POST | `/register` | Register a user profile if it does not exist |
| POST | `/embeddings` | Ingest a GitHub repo, compute score, create/store embeddings |
| GET | `/gettree` | Fetch repository tree from GitHub (`repo_owner`, `repo_name` query params) |
| GET | `/getscore/{repo_id}` | Get stored repository quality score |
| POST | `/newchat` | Create a new chat thread |
| POST | `/respond` | Stream chatbot response for a query (SSE) |
| GET | `/repositories/{user_id}` | List repositories added by a user |
| GET | `/threads/{repo_id}/{user_id}` | List chat threads for a repo + user |
| GET | `/messages/{thread_id}` | Get message history for a thread |

### Example request payloads

`POST /register`
```json
{
	"user": "<uuid>"
}
```

`POST /embeddings`
```json
{
	"repo_url": "https://github.com/owner/repo",
	"user_id": "<uuid>"
}
```

`POST /newchat`
```json
{
	"user_id": "<uuid>",
	"repo_id": 123,
	"title": "My first chat"
}
```

`POST /respond`
```json
{
	"query": "Explain the project architecture",
	"thread_id": 1,
	"user_id": "<uuid>",
	"repo_id": 123
}
```

## 8) Running the Server (Dev + Production)

### Development
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production (example)
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 9) Folder Structure

```text
codebase_reader/
├── main.py
├── utils.py
├── pyproject.toml
├── README.md
├── env_sample.txt
├── chatbot/
│   ├── chatbot.py
│   └── session.py
├── Database/
│   └── database.py
├── repo_qulaity/
│   ├── scanner.py
│   ├── metrics.py
│   └── score_cal.py
└── scripts/
		├── create_vectors.py
		├── create_vectors_api.py
		├── github_repo_loader.py
		├── loader.py
		├── spliiter.py
		└── clone_repo/
```

## 10) Future Improvements (Optional)
- Add authentication/authorization (JWT or Supabase Auth)
- Add rate limiting and request validation schemas
- Add background job queue for large repository ingestion
- Add retry/backoff for external API calls
- Add Docker + CI/CD pipeline
- Add test suite (unit/integration/e2e)
- Add structured logging and observability

## 11) License
This project is licensed under the **MIT License**.
