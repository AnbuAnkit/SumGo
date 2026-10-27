from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class TabContext(BaseModel):
    """The tab the user has open, captured in the popup via chrome.tabs.query."""

    url: str | None = None
    title: str | None = None


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1)
    tab: TabContext | None = None


class ToolCallRecord(BaseModel):
    """A tool invocation the agent made, surfaced so the UI can show its work."""

    tool: str
    args: dict = Field(default_factory=dict)


class ChatResponse(BaseModel):
    reply: str
    tool_calls: list[ToolCallRecord] = Field(default_factory=list)
    tab_url: str | None = None
