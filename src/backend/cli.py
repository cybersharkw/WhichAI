"""Entry point for `uv run whichai`."""

import uvicorn

from backend.config import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run("backend.main:app", host=settings.host, port=settings.port)
