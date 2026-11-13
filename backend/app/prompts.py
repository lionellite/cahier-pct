"""Chargement et rendu des consignes (prompts)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Iterable

from .services.corpus import Extract

PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"


@lru_cache(maxsize=16)
def load_prompt(name: str) -> str:
    path = PROMPTS_DIR / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Prompt introuvable : {path}")
    return path.read_text(encoding="utf-8")


def render(name: str, **values: object) -> str:
    """Remplace les jetons `<<CLE>>` par leur valeur."""
    text = load_prompt(name)
    for key, value in values.items():
        text = text.replace(f"<<{key}>>", str(value))
    return text


def system_prompt() -> str:
    return load_prompt("system")


def context_block(extracts: Iterable[Extract]) -> str:
    """Sérialise les extraits pour le modèle, avec leurs métadonnées."""
    blocks: list[str] = []
    for extract in extracts:
        blocks.append(
            "\n".join(
                [
                    f"### Extrait {extract.id}",
                    f"Titre : {extract.title}",
                    f"Type : {extract.type}",
                    f"Référence : {extract.reference}",
                    f"Statut de validation : {extract.status}",
                    "---",
                    extract.content.strip(),
                ]
            )
        )
    return "\n\n".join(blocks)
