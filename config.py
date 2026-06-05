"""Gradio server configuration sourced from environment variables."""
from __future__ import annotations

import os
from typing import ClassVar


class Config:
    """Gradio server settings with environment-variable overrides and safe defaults."""

    GRADIO_SERVER_NAME: ClassVar[str] = os.environ.get("GRADIO_SERVER_NAME", "0.0.0.0")
    GRADIO_SERVER_PORT: ClassVar[int] = int(os.environ.get("GRADIO_SERVER_PORT", "7860"))
    GRADIO_SHARE: ClassVar[bool] = False

    GRADIO_AUTH_MESSAGE: ClassVar[str] = "Welcome to my Alter Ego"
    GRADIO_ALLOWED_PATHS: ClassVar[tuple[str, ...]] = ("/",)
    GRADIO_ANALYTICS_ENABLED: ClassVar[bool] = False
