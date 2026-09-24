from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.agents.orchestrator import orchestrator
from app.config import settings

app = FastAPI(
    title="Multi-Agent Support Bot",
    description=(
        "A RAG + tool-calling multi-agent customer support bot, built with "
        "a swappable OpenAI/Gemini backend."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


class ChatResponseModel(BaseModel):
    reply: str
    route: str
    sources: list[str] = []


@app.get("/health")
def health():
    return {"status": "ok", "llm_provider": settings.llm_provider}


@app.post("/chat", response_model=ChatResponseModel)
def chat(payload: ChatRequest):
    result = orchestrator.handle(payload.message)
    return ChatResponseModel(reply=result.reply, route=result.route, sources=result.sources)


# Serve the demo chat widget at "/"
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
