"""Generic pre-event infrastructure. No competition feature is implemented here."""

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI(title="Hackathon infrastructure template", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok", "scope": "infrastructure-only"}


@app.get("/api/readiness")
def readiness():
    # Presence is deliberately not described as authenticated or connected.
    return {
        "template_only": True,
        "competition_feature_implemented": False,
        "model_access_verified": False,
        "deployment_verified": False,
        "account_configuration_present": bool(os.getenv("GOOGLE_CLOUD_PROJECT")),
        "model_id_present": bool(os.getenv("GEMINI_MODEL")),
    }


@app.get("/")
def index():
    return FileResponse(Path(__file__).with_name("index.html"))


if __name__ == "__main__":
    import uvicorn

    # Avoid Windows Proactor accept failures seen during the real HTTP check.
    uvicorn.run(app, host="127.0.0.1", port=int(os.getenv("PORT", "8080")), loop="asyncio:SelectorEventLoop")
