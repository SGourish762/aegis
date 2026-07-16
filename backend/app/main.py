from fastapi import FastAPI

from app.detection.engine import screen
from app.schemas import ScreenRequest, ScreenResponse

app = FastAPI(
    title="Aegis",
    description="AI-agent guardrail layer: prompt-injection screening and action policy enforcement.",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/screen", response_model=ScreenResponse)
def screen_text(req: ScreenRequest) -> ScreenResponse:
    return screen(req.text)
