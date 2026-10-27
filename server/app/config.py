import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Environment-driven configuration for the agent backend."""

    def __init__(self) -> None:
        self.google_api_key = os.getenv("GOOGLE_API_KEY", "").strip()
        self.exa_api_key = os.getenv("EXA_API_KEY", "").strip()
        self.model = os.getenv("MODEL", "google_genai:gemini-3.8-flash").strip()
        self.max_page_chars = int(os.getenv("MAX_PAGE_CHARS", "12000"))
        self.request_timeout = float(os.getenv("REQUEST_TIMEOUT", "20"))
        self.cors_origins = [
            origin.strip()
            for origin in os.getenv("CORS_ORIGINS", "*").split(",")
            if origin.strip()
        ]

    def missing_keys(self) -> list[str]:
        """Names of required env vars that are not set."""
        missing = []
        if not self.google_api_key:
            missing.append("GOOGLE_API_KEY")
        if not self.exa_api_key:
            missing.append("EXA_API_KEY")
        return missing


settings = Settings()
