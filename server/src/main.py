"""Sum-Go backend: the extension pushes the current page URL, the chat asks about it."""

import os
import threading
import time

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import llm

app = FastAPI(title="Sum-Go backend", version="1.0")

# The popup (chrome-extension://...) and the Vite dev server are different origins.
# No cookies or credentials are used, so a wildcard origin is safe for local dev.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_state_lock = threading.Lock()
_state: dict[str, object] = {"url": None, "updated_at": None}


class ContextRequest(BaseModel):
    url: str = Field(..., description="URL of the tab the extension was opened on")


class ChatRequest(BaseModel):
    message: str = Field(..., description="What the user asked about the page")
    url: str | None = Field(None, description="Optional override; defaults to the pushed URL")


@app.get("/api/health")
def health():
    with _state_lock:
        current = _state["url"]
    return {"status": "ok", "hasUrl": current is not None, "model": llm.MODEL_NAME}


@app.post("/api/context")
def set_context(payload: ContextRequest):
    """Called by the extension popup every time it opens."""
    try:
        url = llm.validate_url(payload.url)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    with _state_lock:
        _state["url"] = url
        _state["updated_at"] = time.time()

    print(f"[context] {url}", flush=True)
    return {"url": url}


@app.get("/api/context")
def get_context():
    with _state_lock:
        return {"url": _state["url"], "updatedAt": _state["updated_at"]}


@app.post("/api/chat")
def chat(payload: ChatRequest):
    """Fetch the page at the pushed URL and answer the user's message about it."""
    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    url = (payload.url or "").strip()
    if not url:
        with _state_lock:
            url = _state["url"] or ""

    if not url:
        raise HTTPException(
            status_code=409,
            detail="No page yet. Open the Sum-Go extension on the page you want summarized.",
        )

    try:
        reply = llm.answer(message, url)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except llm.PageFetchError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    except Exception as error:  # model/API/network failures
        raise HTTPException(
            status_code=502, detail=f"The model request failed: {error}"
        ) from error

    return {"reply": reply, "url": url}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=int(os.getenv("SUM_GO_PORT", "8000")),
    )
