"""Configuration de l'application, chargée depuis le `.env` racine."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# backend/app/config.py -> racine du dépôt
ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "backend"

load_dotenv(ROOT_DIR / ".env")
load_dotenv(BACKEND_DIR / ".env")


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _as_list(value: str | None, default: list[str] | None = None) -> list[str]:
    if not value:
        return default or []
    return [item.strip() for item in value.split(",") if item.strip()]


class Config:
    """Configuration par défaut. Surchargeable par variables d'environnement."""

    APP_NAME: str = "Cahier PCT"
    APP_VERSION: str = "0.1.0"

    # --- Modèle de langage --------------------------------------------------
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "").strip()
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
    LLM_MODE: str = os.getenv("LLM_MODE", "auto").strip().lower()
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "4096"))

    # --- Corpus -------------------------------------------------------------
    # Racine des corpus : chaque sous-dossier avec manifest.json est chargé
    CORPUS_PATH: Path = Path(
        os.getenv("CORPUS_PATH", str(ROOT_DIR / "corpus" / "processed"))
    )

    # --- Serveur ------------------------------------------------------------
    CORS_ORIGINS: list[str] = _as_list(
        os.getenv("CORS_ORIGINS"), ["http://localhost:5173"]
    )
    FLASK_DEBUG: bool = _as_bool(os.getenv("FLASK_DEBUG"), True)
    PORT: int = int(os.getenv("PORT", "5000"))

    # Dossier du build frontend, servi par Flask en production s'il existe.
    FRONTEND_DIST: Path = ROOT_DIR / "frontend" / "dist"

    JSON_AS_ASCII = False
    JSON_SORT_KEYS = False
