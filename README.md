# SessionBook

SessionBook exposes appointment availability and booking tools through FastAPI.

## Run locally

```bash
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Use the project virtualenv explicitly if `uvicorn` is not on your shell PATH:

```bash
venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The default database is `sessionbook.db` (SQLite), so the service starts without
an external database. In development, a localhost PostgreSQL URL is also
automatically mapped to SQLite so an unstarted local PostgreSQL container does
not prevent the API from booting. Set `ENV=production` to require PostgreSQL,
or set `DATABASE_URL` in `.env` to use a remote PostgreSQL instance.

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
- Added a development-only localhost PostgreSQL fallback so a stopped local
  database does not disconnect the API during startup.
- Added startup schema creation and seed data for a fresh database.
- Added connection health checks and clean engine disposal.
- Normalized spaced phone numbers accepted by the booking example.
- Added response schemas to prevent ORM serialization failures.
- Mapped missing slots to HTTP 404 and duplicate bookings to HTTP 409.

## Expose the API with ngrok

The `ngrok` entry in `requirements.txt` is the Python SDK; it does not install
the separate `ngrok` command-line executable. On macOS, install and
authenticate the CLI with Homebrew:

```bash
brew install ngrok
ngrok config add-authtoken YOUR_NGROK_AUTHTOKEN
ngrok http 8000
```

If Homebrew is not installed, install the ngrok macOS agent from
https://ngrok.com/download, then reopen the terminal so `ngrok` is on `PATH`.

Keep Uvicorn running in another terminal and set the HTTPS forwarding URL in
`.env`:

```dotenv
PUBLIC_API_BASE_URL=https://YOUR_SUBDOMAIN.ngrok-free.app
```

If the CLI is not installed, the repository includes an SDK-based alternative:

```bash
export NGROK_AUTHTOKEN=YOUR_NGROK_AUTHTOKEN
venv/bin/python -m scripts.start_tunnel
```

Run `create_agent.py` from the project root after setting that public URL:

```bash
venv/bin/python scripts/create_agent.py
```

The publisher uses AssemblyAI's Voice Agent API at
`https://agents.assemblyai.com/v1/agents`. A `404` from
`https://api.assemblyai.com/v1/agents` means the old API hostname was used;
the agent API is hosted on the `agents.assemblyai.com` subdomain.

### TLS errors when testing the tunnel

Use the exact HTTPS URL printed by ngrok. Do **not** copy
`your-actual-subdomain.ngrok-free.app`; that string is only a placeholder and
will not reach your tunnel. If curl reports error 60 (`unable to get local issuer
certificate`) while opening an ngrok URL, the request is being blocked before it
reaches this application. A proxy, VPN, or Fortinet HTTPS inspection
certificate is usually being presented instead of the public ngrok chain.

Confirm the tunnel separately with:

```bash
curl -v -X POST https://PASTE_THE_EXACT_URL_FROM_NGROK/tools/get_today
```

Do not disable certificate verification for normal use. `curl -k` may be used
once for diagnosis only; the durable fix is to install the network
administrator's trusted root CA or switch to a network without HTTPS
interception, then retry without `-k`.
