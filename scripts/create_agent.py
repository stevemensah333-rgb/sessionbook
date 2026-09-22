import json
import sys
from pathlib import Path

import httpx

from app.config import settings

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AGENT_JSON_PATH = PROJECT_ROOT / "voice_agent" / "agent.json"
ASSEMBLYAI_AGENTS_URL = "https://agents.assemblyai.com/v1/agents"


def load_agent_config() -> dict:
    if not settings.PUBLIC_API_BASE_URL:
        raise RuntimeError(
            "PUBLIC_API_BASE_URL is required. Start ngrok and set it in .env."
        )
    if not AGENT_JSON_PATH.is_file():
        raise FileNotFoundError(f"Agent configuration not found: {AGENT_JSON_PATH}")

    raw = AGENT_JSON_PATH.read_text()
    return json.loads(raw.replace("{{BASE_URL}}", settings.PUBLIC_API_BASE_URL.rstrip("/")))


def main() -> None:
    if not settings.ASSEMBLYAI_API_KEY:
        raise RuntimeError("ASSEMBLYAI_API_KEY is required in .env.")

    update_id = sys.argv[2] if len(sys.argv) >= 3 and sys.argv[1] == "--update" else None
    endpoint = (
        f"{ASSEMBLYAI_AGENTS_URL}/{update_id}"
        if update_id
        else ASSEMBLYAI_AGENTS_URL
    )
    with httpx.Client(timeout=30) as client:
        response = client.request(
            "PATCH" if update_id else "POST",
            endpoint,
            headers={
                "Authorization": settings.ASSEMBLYAI_API_KEY,
                "Content-Type": "application/json",
            },
            json=load_agent_config(),
        )
    if response.is_error:
        raise RuntimeError(
            f"AssemblyAI agent request failed ({response.status_code}): "
            f"{response.text}"
        )

    data = response.json()
    agent_id = data.get("id") or data.get("agent_id")
    if not agent_id:
        raise RuntimeError(f"AssemblyAI response did not include an agent id: {data}")

    print(f"Agent published. agent_id = {agent_id}")
    (PROJECT_ROOT / "agent_id.txt").write_text(agent_id)


if __name__ == "__main__":
    main()
