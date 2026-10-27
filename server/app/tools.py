"""Agent tools: web search (Exa) and reading the page from the user's open tab."""

import httpx
from bs4 import BeautifulSoup
from exa_py import Exa
from langchain_core.tools import BaseTool, tool

from .config import settings
from .schemas import TabContext

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
)

UNREADABLE_TAGS = ("script", "style", "noscript", "svg", "iframe", "template", "form")


def fetch_page_text(url: str) -> str:
    """Fetch a URL and return its visible text, trimmed to the configured budget."""
    if not url.startswith(("http://", "https://")):
        return f"Cannot read {url!r}: only http and https URLs are supported."

    try:
        with httpx.Client(
            follow_redirects=True,
            timeout=settings.request_timeout,
            headers={"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"},
        ) as client:
            response = client.get(url)
            response.raise_for_status()
            html = response.text
    except httpx.HTTPStatusError as exc:
        return (
            f"Could not read {url}: the server returned HTTP {exc.response.status_code}. "
            "The page may be blocking automated requests or require a login."
        )
    except httpx.HTTPError as exc:
        return f"Could not read {url}: {type(exc).__name__}: {exc}"

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(UNREADABLE_TAGS):
        tag.decompose()

    lines = (line.strip() for line in soup.get_text(separator="\n").splitlines())
    text = "\n".join(line for line in lines if line)

    if not text:
        return f"Fetched {url} but found no readable text on the page."

    if len(text) > settings.max_page_chars:
        text = text[: settings.max_page_chars] + "\n\n[content truncated]"

    return f"Content of {url}:\n\n{text}"


@tool
def web_search(query: str) -> str:
    """Search the web for information that is not on the page the user has open.

    Use this for facts, definitions, news, documentation, or anything the current
    page does not cover. Returns the most relevant results with text snippets and
    their source URLs.
    """
    if not settings.exa_api_key:
        return "Web search is unavailable: EXA_API_KEY is not configured on the server."

    try:
        response = Exa(api_key=settings.exa_api_key).search(
            query,
            num_results=5,
            contents={"text": {"max_characters": 1500}, "highlights": True},
        )
    except Exception as exc:  # noqa: BLE001 - surface any provider failure to the model
        return f"Web search failed: {type(exc).__name__}: {exc}"

    results = getattr(response, "results", None) or []
    if not results:
        return f"No web results found for {query!r}."

    blocks = []
    for index, result in enumerate(results, start=1):
        snippet = (getattr(result, "text", None) or "").strip()
        if not snippet:
            highlights = getattr(result, "highlights", None) or []
            snippet = "\n".join(highlights).strip()
        if len(snippet) > 1200:
            snippet = snippet[:1200] + "..."

        blocks.append(
            f"[{index}] {getattr(result, 'title', None) or 'Untitled'}\n"
            f"URL: {getattr(result, 'url', '')}\n"
            f"{snippet}"
        )

    return "\n\n".join(blocks)


def build_tools(tab: TabContext | None) -> list[BaseTool]:
    """Build the tool list for one request, binding the user's active tab URL.

    The tab URL comes from `chrome.tabs.query` in the extension and is captured by
    the `read_current_tab` closure, so the agent never has to guess it.
    """
    tools: list[BaseTool] = [web_search]

    tab_url = (tab.url or "").strip() if tab else ""
    if not tab_url:
        return tools

    @tool
    def read_current_tab() -> str:
        """Read the full text of the web page the user currently has open in their tab.

        Use this whenever the question is about "this page", the article the user is
        reading, or anything shown in the current tab. Takes no arguments.
        """
        return fetch_page_text(tab_url)

    tools.append(read_current_tab)
    return tools
