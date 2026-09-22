```markdown
# SessionBook

A FastAPI backend for booking appointments, wired to an AI voice agent (AssemblyAI) so callers can check availability and book a session over a real phone call.

Built as a personal project to learn backend engineering patterns relevant to AI-integrated systems: async APIs, transaction-safe booking logic, and designing REST responses for an AI agent to consume rather than a UI.

## What it actually does

A caller talks to an AI voice agent. The agent doesn't know anything about scheduling itself, it calls this backend's REST endpoints as "tools" whenever it needs real data: today's date, open slots, or to book and confirm a session. The backend owns all the actual logic and data; the agent is a thin conversational layer on top of it.

## Architecture

```
Caller (phone) → AssemblyAI Voice Agent → FastAPI backend → PostgreSQL
```

The voice agent never touches the database directly. It only knows how to call a public HTTPS URL and read back JSON. The FastAPI service is fully independent and testable on its own with plain HTTP requests, no AI involved.

## Tech stack

- **Python 3.13**, **FastAPI**, **Uvicorn**
- **SQLAlchemy 2.0** (async) + **Alembic** for migrations
- **PostgreSQL** (via Docker locally)
- **Pydantic** / **pydantic-settings** for validation and config
- **AssemblyAI Voice Agent API** (HTTP tools mode)

## Project structure

```
sessionbook/
├── app/
│   ├── main.py                 # FastAPI app entrypoint
│   ├── config.py                # env-based settings
│   ├── database.py              # async engine + session
│   ├── models.py                 # SQLAlchemy ORM models
│   ├── schemas.py                # Pydantic request/response models
│   ├── services/
│   │   └── booking_service.py    # booking logic, incl. concurrency handling
│   └── routers/
│       └── tools.py               # endpoints the voice agent calls
├── scripts/
│   ├── seed.py                    # loads sample provider + slots
│   └── create_agent.py             # publishes agent.json to AssemblyAI
├── agent.json                      # voice agent configuration
├── alembic/                        # database migrations
├── docker-compose.yml               # local Postgres
└── requirements.txt
```

## Key design decisions

- **Every timestamp is stored timezone-aware, in UTC** (`DateTime(timezone=True)`), and only converted to the provider's local time at the point of formatting a spoken response. This avoids ambiguity about what a stored time actually means once deployed somewhere with a different server timezone.
- **Double-booking is prevented two ways at once**: a `SELECT ... FOR UPDATE` row lock during the booking transaction, backed by a database-level `UNIQUE` constraint on `bookings.slot_id` as an independent safety net.
- **API responses are written to be spoken, not just parsed.** Each relevant response includes a natural-language field (e.g. `spoken_label`, `spoken_confirmation`) alongside raw data, since the consumer of this API is a voice agent reading text aloud, not a UI rendering it.
- **Input validation stays loose on fields transcribed from speech** (like phone numbers), rather than strict pattern matching, since a strict schema rejection is invisible to the agent and can wrongly tell a caller the system is broken instead of just re-asking a question.

## Running it locally

```bash
# 1. Environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in your real ASSEMBLYAI_API_KEY

# 2. Database
docker compose up -d
alembic upgrade head
python -m scripts.seed

# 3. Run the API
uvicorn app.main:app --reload
```

Test it directly, no AI involved:

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/tools/check_availability \
  -H "Content-Type: application/json" -d '{"date": "2026-09-25"}'
```

## Wiring up the voice agent

```bash
# Expose the local server publicly
ngrok http 8000
# copy the https://... URL into .env as PUBLIC_API_BASE_URL

# Publish the agent config to AssemblyAI
python -m scripts.create_agent
```

## Environment variables

See `.env.example`. Requires `DATABASE_URL` (async, `postgresql+asyncpg://...`), `ASSEMBLYAI_API_KEY`, and `PUBLIC_API_BASE_URL` (your public tunnel URL).

## Possible extensions

- `/tools/cancel_booking` and `/tools/reschedule` endpoints
- SMS/email confirmation on booking
- API-key protection on the tool endpoints
```