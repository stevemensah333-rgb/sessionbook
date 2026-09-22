import os
import time

import ngrok

from app.config import settings


def main() -> None:
    tunnel = ngrok.forward(
        settings.PORT,
        proto="http",
        authtoken=os.getenv("NGROK_AUTHTOKEN"),
    )
    print(f"Public URL: {tunnel.url()}", flush=True)
    print("Keep this process running while AssemblyAI calls the API.", flush=True)
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        ngrok.disconnect(tunnel.url())


if __name__ == "__main__":
    main()
