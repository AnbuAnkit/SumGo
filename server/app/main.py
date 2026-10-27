"""FastAPI entrypoint for the Chrome extension chat agent."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.exceptions import LangChainException

from .agent import run_agent
from .config import settings
from .schemas import ChatRequest, ChatResponse

app = FastAPI(title="Chrome Chat Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "model": settings.model,
        "missing_keys": settings.missing_keys(),
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    missing = settings.missing_keys()
    if missing:
        raise HTTPException(
            status_code=500,
            detail=f"Server is missing credentials: {', '.join(missing)}. Add them to server/.env.",
        )

    try:
        reply, tool_calls = run_agent(request)
    except LangChainException as exc:
        raise HTTPException(status_code=502, detail=f"Model call failed: {exc}") from exc
    except Exception as exc:  # noqa: BLE001 - report any agent failure to the client
        raise HTTPException(
            status_code=500, detail=f"Agent run failed: {type(exc).__name__}: {exc}"
        ) from exc

    return ChatResponse(
        reply=reply,
        tool_calls=tool_calls,
        tab_url=request.tab.url if request.tab else None,
    )
