"""Fetch a web page's readable text and hand it to Gemma 4 through LangChain."""

import os
import re
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# .env lives at the repo root, two levels above server/src/
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

MODEL_NAME = os.getenv("SUM_GO_MODEL", "gemma-4-26b-a4b-it")
MAX_PAGE_CHARS = 12_000
FETCH_TIMEOUT_SECONDS = 15.0
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36 Sum-Go/1.0"
)

SYSTEM_PROMPT = (
    "You are Sum, a browser-extension assistant that summarizes the web page the "
    "user is currently reading. You are given the page's URL and its extracted text. "
    "Answer the user's request using only that page content. Be concise: lead with "
    "the answer, then at most three short supporting points. Quote sparingly. If the "
    "page text does not contain the answer, say so plainly instead of guessing."
)

# Tags that never carry readable prose.
NOISE_TAGS = (
    "script",
    "style",
    "noscript",
    "iframe",
    "svg",
    "form",
    "nav",
    "footer",
    "aside",
    "header",
)


class PageFetchError(Exception):
    """The page could not be fetched or contained no readable text."""


def validate_url(url: str) -> str:
    """Return a cleaned http(s) URL, or raise ValueError."""
    cleaned = url.strip()
    parsed = urlparse(cleaned)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only http:// and https:// URLs can be summarized")
    if not parsed.netloc:
        raise ValueError("That URL is missing a host")
    return cleaned


def fetch_page_text(url: str) -> str:
    """Download the page and return its collapsed readable text."""
    validate_url(url)

    try:
        with httpx.Client(
            timeout=FETCH_TIMEOUT_SECONDS,
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT, "Accept-Language": "en"},
        ) as client:
            response = client.get(url)
    except httpx.HTTPError as error:
        raise PageFetchError(f"Could not load that page: {error}") from error

    if response.status_code >= 400:
        raise PageFetchError(
            f"That page returned HTTP {response.status_code}, so there is nothing to summarize."
        )

    content_type = response.headers.get("content-type", "")
    if "html" not in content_type and "text" not in content_type:
        raise PageFetchError(f"Unsupported content type: {content_type or 'unknown'}")

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(NOISE_TAGS):
        tag.decompose()

    # Prefer the main article content when the page marks it up.
    main = soup.find("main") or soup.find("article") or soup.body or soup
    text = main.get_text(separator=" ", strip=True)
    text = re.sub(r"\s+", " ", text).strip()

    if len(text) < 100:
        raise PageFetchError("That page had almost no readable text to summarize.")

    return text[:MAX_PAGE_CHARS]


@lru_cache(maxsize=1)
def get_model() -> ChatGoogleGenerativeAI:
    """Gemma 4 through LangChain's Google integration (Gemini API)."""
    return ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=0.3,
        max_retries=1,
        timeout=60,
    )


def build_messages(url: str, page_text: str, user_message: str):
    return [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"Page URL: {url}\n\n"
                f"Page text:\n{page_text}\n\n"
                f"User request: {user_message}"
            )
        ),
    ]


def answer(message: str, url: str) -> str:
    """Fetch the page at `url` and answer `message` about it."""
    page_text = fetch_page_text(url)
    response = get_model().invoke(build_messages(url, page_text, message))
    content = response.content
    if isinstance(content, list):
        content = " ".join(
            part.get("text", "") if isinstance(part, dict) else str(part) for part in content
        )
    reply = str(content).strip()
    return reply or "The model returned an empty response."
