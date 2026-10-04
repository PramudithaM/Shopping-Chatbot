import logging  # to write errors into the terminal log
from contextlib import asynccontextmanager  # for startup / shutdown code
from typing import Literal  # limits a value to a fixed set of options

from fastapi import FastAPI, HTTPException, Request  # web framework
from fastapi.middleware.cors import CORSMiddleware  # lets the React app call this API
from pydantic import BaseModel, Field  # request / response data validation

from app.config import AVAILABLE_PROVIDERS, FRONTEND_ORIGINS, LLM_PROVIDER  # settings (config.py)
from app.rag import answer, build_agent  # our RAG agent (rag.py)

log = logging.getLogger("shopassist")  # logger for this app


def default_provider() -> str | None:  # provider used when the UI does not choose one
    if LLM_PROVIDER in AVAILABLE_PROVIDERS:  # the one set in .env
        return LLM_PROVIDER
    return AVAILABLE_PROVIDERS[0] if AVAILABLE_PROVIDERS else None  # or the first one with a key


def get_agent(app: FastAPI, provider: str):  # one agent per provider, built the first time it is needed
    if provider not in app.state.agents:
        app.state.agents[provider] = build_agent(provider)
    return app.state.agents[provider]


@asynccontextmanager
async def lifespan(app: FastAPI):  # runs once when the server starts
    app.state.agents = {}  # cache: provider name -> agent
    yield  # the server runs here


app = FastAPI(title="ShopAssist AI", lifespan=lifespan)  # create the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,  # only our React app may call the API
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):  # one message in the history
    role: Literal["user", "assistant"]  # who wrote it
    content: str  # the text


class ChatRequest(BaseModel):  # what the frontend sends us
    message: str = Field(min_length=1, max_length=1000)  # the new question
    history: list[ChatMessage] = []  # previous messages (optional)
    provider: Literal["openai", "gemini"] | None = None  # LLM chosen in the UI (optional)


class Source(BaseModel):  # one source chunk shown under the answer
    collection: str  # "support" or "reviews"
    snippet: str  # first 200 characters of the chunk


class ChatResponse(BaseModel):  # what we send back
    answer: str  # the chatbot answer
    sources: list[Source]  # chunks the answer is based on


@app.get("/health")  # simple check: is the server alive?
async def health():
    return {"status": "ok"}


@app.get("/providers")  # which LLMs can the UI offer?
async def providers():
    return {"available": AVAILABLE_PROVIDERS, "default": default_provider()}


@app.post("/chat", response_model=ChatResponse)  # main endpoint
async def chat(req: ChatRequest, request: Request):
    provider = req.provider or default_provider()  # UI choice, or the default
    if provider not in AVAILABLE_PROVIDERS:  # no key for it in .env
        raise HTTPException(status_code=400, detail=f"Provider '{provider}' is not configured.")

    history = [m.model_dump() for m in req.history]  # pydantic objects -> plain dicts
    try:
        agent = get_agent(request.app, provider)  # agent for this provider
        text, sources = await answer(agent, req.message, history)  # run the agent
    except Exception:  # LLM error, rate limit, etc.
        log.exception("chat failed")  # full error goes to the terminal
        raise HTTPException(status_code=500, detail="Something went wrong. Please try again.")
    return ChatResponse(answer=text, sources=sources)  # send the answer back