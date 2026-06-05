# AI Alter Ego

A production-ready personal website chatbot that acts as an AI stand-in. Visitors ask it about career, skills, and experience; it answers using live CV and bio data, captures leads via email, and self-heals poor responses through a second LLM judge.

---

## How It Works

```
User → Gradio UI
           ↓
      ChatAgent (GPT-4o-mini)
           ↓ if tool_calls
      ToolExecutor → Notifier → SMTP Email
           ↓ reply
      Evaluator (Gemini 2.5 Flash) ← LLM-as-Judge
           ↓ fail
      ChatAgent retries with rejection feedback
           ↓ pass
      Reply returned to UI
```

---


### 1. Dual-LLM Architecture
Two different LLMs play different roles:
- **GPT-4o-mini** (OpenAI) handles the conversational persona — low latency, cost-effective for chat.
- **Gemini 2.5 Flash** (Google, via OpenAI-compatible endpoint) acts as a quality judge — a separate model evaluating the first one reduces bias compared to self-evaluation.

### 2. LLM-as-Judge Evaluator with Self-Healing
Every reply from the agent passes through a structured evaluator before being shown to the user. If the reply fails quality control, the agent is given the rejection reason and retries once with a corrected prompt. This pattern:
- Catches off-topic, low-effort, or out-of-character replies automatically
- Requires no manual threshold tuning — the judge LLM reasons about quality
- Uses **Pydantic structured outputs** (`response_format=Evaluation`) to guarantee a parseable `{is_acceptable, feedback}` schema

### 3. Structured Outputs via Pydantic + OpenAI `.parse()`
```python
class Evaluation(BaseModel):
    is_acceptable: bool
    feedback: str

response = gemini.beta.chat.completions.parse(..., response_format=Evaluation)
```
The evaluator uses `beta.chat.completions.parse()` instead of `.create()`, which enforces the Pydantic schema at the SDK level and eliminates fragile JSON parsing.

### 4. OpenAI Function Calling for Lead Capture
The agent is equipped with two tools:
- `record_user_details` — captures visitor name, email, and notes
- `record_unknown_question` — logs questions the agent couldn't answer

When the LLM decides a tool is needed, `ToolExecutor` dispatches the call to `Notifier`, which fires a real-time email alert. This gives the site owner instant visibility into visitor intent without a database.

### 5. PDF CV Ingestion
The owner's CV is parsed at startup using `pypdf` and injected into the system prompt:
```python
cv_text = "".join(page.extract_text() or "" for page in PdfReader(cv_path).pages)
```
No embeddings, no vector store — for a single-document context, direct injection into the prompt is simpler and more reliable.

### 6. Immutable Context via Frozen Dataclass
`ChatContext` is a `@dataclass(frozen=True)` — once loaded, the agent's identity and context cannot be accidentally mutated. Both the agent and evaluator system prompts are generated from the same context object, keeping them in sync.

### 7. Google Gemini via OpenAI-Compatible API
Gemini is accessed through its OpenAI-compatible endpoint, meaning only one SDK (`openai`) is needed:
```python
gemini = OpenAI(
    api_key=os.environ["GOOGLE_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
```
This is a practical multi-provider pattern — swap models without changing code structure.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **UI** | [Gradio](https://gradio.app/) — `gr.ChatInterface` with custom `gr.Chatbot` |
| **Primary LLM** | GPT-4o-mini via [OpenAI Python SDK](https://github.com/openai/openai-python) |
| **Judge LLM** | Gemini 2.5 Flash via Google's OpenAI-compatible endpoint |
| **Structured outputs** | [Pydantic v2](https://docs.pydantic.dev/) + `beta.chat.completions.parse()` |
| **Document parsing** | [pypdf](https://pypdf.readthedocs.io/) — CV extraction from PDF |
| **Email** | `smtplib.SMTP_SSL` — lead capture and unknown question alerts |
| **Config** | `python-dotenv` — env-based config with `Config` class defaults |
| **Linting / formatting** | [Ruff](https://docs.astral.sh/ruff/) |
| **Package manager** | [uv](https://github.com/astral-sh/uv) |
| **Python** | 3.12+ |

---

## Project Structure

```
ai-alter-ego/
├── chat_agent.py       # ChatAgent: orchestrates conversation + evaluation loop
├── chat_context.py     # ChatContext: frozen dataclass, builds all system prompts
├── evaluation.py       # Evaluator: LLM-as-judge quality gate with Pydantic schema
├── tool_executor.py    # ToolExecutor: dispatches LLM tool-call requests
├── tool_specs.py       # OpenAI function-call JSON schemas
├── notifier.py         # Notifier: SMTP email alerts for leads and unknown questions
├── config.py           # Config: Gradio server settings from environment
├── me/
│   ├── summary.txt     # Owner bio (injected into system prompt)
│   └── CV_*.pdf        # CV parsed at startup via pypdf
└── pyproject.toml
```

---

## Setup

**Prerequisites:** Python 3.12+, `uv`

```bash
uv sync
cp .env.example .env   # fill in your API keys
uv run python chat_agent.py
```

Open `http://127.0.0.1:7860/alter-ego`

### Required Environment Variables

| Variable | Purpose |
|---|---|
| `OPENAI_API_KEY` | GPT-4o-mini (primary agent) |
| `GOOGLE_API_KEY` | Gemini 2.5 Flash (evaluator judge) |
| `ALERT_FROM_EMAIL` | SMTP sender address |
| `EMAIL_PASSWORD` | SMTP password |
| `ALERT_TO_EMAIL` | Where lead-capture emails are sent |
| `GRADIO_SERVER_NAME` | Override bind address (default `0.0.0.0`) |
| `GRADIO_SERVER_PORT` | Override port (default `7860`) |
| `SMTP_HOST` | Override SMTP server (default `smtp.mail.ovh.net`) |
| `SMTP_PORT` | Override SMTP port (default `465`) |
