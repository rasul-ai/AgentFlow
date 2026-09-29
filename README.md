# Code 19 HR Leave Assistant

A RAG-grounded, multi-agent leave request pipeline built with **LangGraph**, backed by an **Ollama Cloud** LLM,
for the leave rules defined in `Code 19 Leave Policy 2022.pdf`. Employees interact through a chat interface —
asking policy questions, getting holiday-aware leave-date suggestions, and having the assistant collect and
submit a leave application for them — rather than filling out a static form.

```
Employee chats with the HR Assistant (React)
        │
        ▼
FastAPI  ──▶  Chat agent graph (per message, multi-turn state persisted in SQLite)
              1. Policy Retrieval — embeds the message, searches a Chroma vector store
                                     built from the leave policy (RAG)
              2. Converse Agent  — answers policy/balance questions, gives leave-date
                                    suggestions grounded in real festival-holiday dates
                                    and the Friday/Saturday weekly off (never fabricates
                                    a moon-sighting/government-declared date), and
                                    incrementally fills a leave-request draft across
                                    turns. Only proposes submitting once the employee
                                    has explicitly confirmed a complete draft.
        │  (once the employee confirms and all required fields are known)
        ▼
        Leave Request pipeline (same LangGraph pipeline used by the direct API)
              3. Eligibility Agent — a deterministic rules engine (balances, notice
                                      periods, consecutive-day caps, gender rules, etc.
                                      distilled from the policy) makes the eligible/
                                      not-eligible call; the LLM only writes the
                                      employee-facing explanation, grounded in the
                                      retrieved policy clauses, and never overrides
                                      the verdict
              4a. Application Filler Agent (if eligible) — LLM drafts a formal leave
                  application and the request is queued for the manager/HR
              4b. Reject (if not eligible) — request is closed with the cited reasons
        │
        ▼
HR Dashboard (React) — approve/reject queued applications
```

**Why the eligibility verdict is deterministic, not LLM-decided:** leave balances, notice
periods and day caps are hard numeric rules from the policy — the kind of thing an LLM can
misread or hallucinate. The rules engine (`backend/app/policy_rules.py`) is the single source
of truth for the eligible/not-eligible boolean; the LLM's job is explanation and drafting,
always grounded in the chunks retrieved from the policy document. This keeps the system
auditable while still being a genuine RAG + multi-agent pipeline.

## Prerequisites

- Python 3.11+
- Node.js 20+
- An [Ollama Cloud](https://ollama.com) account and API key (create one at
  https://ollama.com/settings/keys) — used for the **chat** model.
- A local [Ollama](https://ollama.com/download) install with `ollama serve` running —
  used for the **embedding** model. Ollama Cloud hosts large chat models but does not serve
  the `/api/embed` endpoint, so embeddings have to run locally regardless of how the chat
  model is configured. Also note: Ollama Cloud's hosted models don't honor the `format`
  (grammar-constrained JSON) parameter the way local models do — the backend works around
  this with prompt-engineered JSON + defensive parsing (see `app/llm/client.py`), so this is
  handled for you, but it's why responses are parsed rather than schema-enforced server-side.

## Backend setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Import the bundled embedding model into your local Ollama daemon (one-time):
cd models/embeddinggemma-300m && ollama create embeddinggemma:300m -f Modelfile && cd ../..

cp .env.example .env
# edit .env and set OLLAMA_CHAT_API_KEY to your real Ollama Cloud key
uvicorn app.main:app --reload --port 8016
```

On first startup the backend will:
- create `data/app.db` (SQLite) and seed 4 demo employees with varied join dates,
  confirmation status and gender (so you can exercise CL/SL pro-ration, EL notice-period
  rejection, PL/ML gender rules, etc.)
- embed the 12 lettered sections of `data/policy_source.md` (a clean transcription of the
  source PDF, kept alongside it in `data/leave_policy.pdf` for provenance) into a local
  Chroma collection at `data/chroma/`

If `OLLAMA_CHAT_API_KEY` is missing/invalid, or the local embedding model hasn't been imported
yet, the server still starts (employee/balance endpoints work), but chat and leave submission
will fail until both are fixed and the server is restarted — check the terminal for a warning
at startup.

API docs: http://localhost:8000/docs

## Frontend setup

```bash
cd frontend
npm install
cp .env.example .env   # defaults to http://localhost:8000, edit if needed
npm run dev
```

Open http://localhost:5173 — a company landing page with two logins:

- **Employee Login** (`/login/employee`) → the Employee Portal: profile, leave balances, request
  history, and a floating "HR Assistant" chat button (bottom-right) for policy questions,
  leave-date suggestions, and filling/submitting requests conversationally.
- **HR / Manager Login** (`/login/hr`) → the HR Dashboard: pending-approval queue, full request
  history, approve/reject.

Both logins use JWTs (`PyJWT`, demo secret in `app/config.py` — override `JWT_SECRET` in `.env`
for anything beyond a local demo) and bcrypt-hashed passwords. An employee can only ever read/act
on their own data; the backend enforces this server-side, not just in the UI.

**Demo accounts** (seeded in `app/seed.py`, all fake data):

| Employees (password: `password123`) | HR / Managers (password: `hrpass123`) |
|---|---|
| `ayesha` · `tanvir` · `nusrat` · `rakib` · `farzana` | `farhana` · `imtiaz` |

`nusrat` is a newer, unconfirmed employee with an empty history; the other four have seeded
historical leave requests (approved, agent-rejected, and manager-rejected examples) so balances
and both dashboards look lived-in immediately, with no need to submit anything first.

Conversation history and in-progress drafts are persisted server-side per employee (`ChatMessage` /
`ChatDraft` tables), so refreshing the page or logging back in doesn't lose the thread. Use
"Start over" in the chat header to discard the current in-progress draft without clearing the conversation.

## Policy rules encoded (Code 19 Leave Policy, Edition 1.1, 15 Jan 2022)

| Leave type | Annual entitlement | Key rules enforced |
|---|---|---|
| Casual (CL) | 10 days | max 2 consecutive days, half-day ≤4h, pro-rata from joining, resets yearly |
| Sick (SL) | 14 days | medical certificate required if >1 day, pro-rata from joining, resets yearly |
| Earned (EL) | 20 days | ≥10 working days' notice, pro-rata from confirmation, resets yearly, >5 consecutive days flagged for senior approval |
| Paternal (PL) | 7 days | male employees only, ≥4 weeks' notice, must fall within 6 weeks of birth, max 2 children |
| Maternity (ML) | 120 days | female employees only, ≥10 weeks' notice, medical certificate required, max 2 children |
| Without Pay (LWP) | as required | always routed to HR for discretionary approval |

## Project layout

```
backend/
  app/
    agents/       LangGraph state/nodes/graph for both the leave pipeline and the chat agent
    llm/          Ollama Cloud client wrapper (chat, structured JSON, multi-turn, embeddings)
    rag/          Policy chunking, Chroma ingestion + retrieval
    routers/      FastAPI endpoints (auth, employees, leave, hr, policy, chat)
    auth.py           Password hashing, JWT issue/verify, FastAPI auth dependencies
    policy_rules.py   Deterministic entitlement/eligibility rules distilled from the PDF
    balances.py       Leave balance computation (entitlement - used - pending)
    holidays.py       Festival-holiday + weekly-off calendar context for leave suggestions
    labels.py         Shared leave-type display labels
    seed.py           5 demo employees + 2 HR users w/ credentials + historical leave records
  data/           Source PDF, transcribed policy markdown, SQLite db, Chroma store
  models/         Local embedding model (EmbeddingGemma GGUF + Modelfile)
frontend/
  src/
    api/          Typed axios client (Bearer-token auth on every authenticated call)
    context/      AuthContext — employee & HR session state, localStorage persistence
    components/   ProtectedRoute, PortalNav, FloatingChat, ChatWindow, balance cards, badges
    pages/        LandingPage, EmployeeLogin, HRLogin, EmployeePortal, HRDashboard
```
