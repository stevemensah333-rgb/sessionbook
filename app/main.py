from fastapi import FastAPI

app = FastAPI(name="SessionBook", description="A backend service that manages appointment/session bookings")

@app.get("/health")
def health():
    return {"status": "ok"}
