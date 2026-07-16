from fastapi import FastAPI

from app.agent.demo_agent import propose_actions
from app.detection.engine import screen
from app.policy.engine import evaluate_all
from app.schemas import AgentRunRequest, AgentRunResponse, ScreenRequest, ScreenResponse

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


@app.post("/agent/run", response_model=AgentRunResponse)
def agent_run(req: AgentRunRequest) -> AgentRunResponse:
    actions = propose_actions(req.task)
    results = evaluate_all(actions)
    return AgentRunResponse(task=req.task, proposed_actions=actions, results=results)
