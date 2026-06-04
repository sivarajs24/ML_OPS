from __future__ import annotations

import os
from pathlib import Path


class Config:
    """Application configuration."""

    PLATFORM_ROOT = Path(__file__).resolve().parents[2]
    CLIENT_DIR = PLATFORM_ROOT / "client"
    SERVER_DIR = PLATFORM_ROOT / "server"

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-smartnest-change-in-production")
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))

    # Load ML artifacts at startup (set false to lazy-load on first request).
    EAGER_LOAD_ARTIFACTS = os.getenv("EAGER_LOAD_ARTIFACTS", "1") == "1"
