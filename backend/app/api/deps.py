"""Dépendances partagées par les routes."""

from __future__ import annotations

from flask import current_app

from ..services.corpus import CorpusSet, get_corpus
from ..services.llm import LLMService


def corpus() -> CorpusSet:
    return get_corpus(current_app.config["CORPUS_PATH"])


def llm() -> LLMService:
    return LLMService(
        api_key=current_app.config["ANTHROPIC_API_KEY"],
        model=current_app.config["ANTHROPIC_MODEL"],
        mode=current_app.config["LLM_MODE"],
        max_tokens=current_app.config["LLM_MAX_TOKENS"],
    )
