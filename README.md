# SessionBook

SessionBook exposes appointment availability and booking tools through FastAPI.

## Run locally

```bash
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The default database is `sessionbook.db` (SQLite), so the service starts without
an external database. Set `DATABASE_URL` in `.env` to use PostgreSQL, for example
`postgresql+asyncpg://user:password@localhost:5432/sessionbook`.

On startup the service creates the tables and, when the database is empty, seeds
09:00–13:00 slots for the next 14 days in the `Africa/Accra` timezone.

## API smoke test

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/tools/get_today
curl -X POST http://localhost:8000/tools/check_availability \
  -H "Content-Type: application/json" \
  -d '{"date":"2026-09-25"}'
curl -X POST http://localhost:8000/tools/book_slot \
  -H "Content-Type: application/json" \
  -d '{"slot_id":1,"caller_name":"Kwame","caller_phone":"0916 383 6950"}'
curl -X POST http://localhost:8000/tools/confirm_booking \
  -H "Content-Type: application/json" \
  -d '{"confirmation_code":"PASTE_THE_CODE_FROM_BOOKING"}'
```

## Runtime fixes

- Fixed package-relative ORM imports, which previously prevented `app.main`
  from importing.
- Replaced the malformed default database URL and added async SQLite for local
  startup.
- Added startup schema creation and seed data for a fresh database.
- Added connection health checks and clean engine disposal.
- Normalized spaced phone numbers accepted by the booking example.
- Added response schemas to prevent ORM serialization failures.
- Mapped missing slots to HTTP 404 and duplicate bookings to HTTP 409.
