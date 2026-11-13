"""Contrats d'entrée de l'API (validation Pydantic)."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class QuestionRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    level: str | None = Field(default=None, max_length=40)
    top_k: int = Field(default=5, ge=1, le=10)

    @field_validator("question")
    @classmethod
    def _strip_question(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("La question ne peut pas être vide.")
        return value


class FicheRequest(BaseModel):
    """Génération d'une fiche de préparation.

    `competence` accepte soit l'identifiant d'un extrait du corpus, soit une
    recherche libre (« masse volumique », « énergie mécanique »…).
    """

    competence: str = Field(min_length=2, max_length=300)
    level: str | None = Field(default=None, max_length=40)
    duration: str | None = Field(default=None, max_length=60)
    class_size: str | None = Field(default=None, max_length=60)
    context: str | None = Field(default=None, max_length=1000)

    @field_validator("competence")
    @classmethod
    def _strip_competence(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("La compétence ne peut pas être vide.")
        return value


class ExercicesRequest(BaseModel):
    competence: str = Field(min_length=2, max_length=300)
    level: str | None = Field(default=None, max_length=40)
    count: int = Field(default=5, ge=1, le=10)
    with_correction: bool = True
    difficulty: str | None = Field(default=None, max_length=40)
    context: str | None = Field(default=None, max_length=1000)

    @field_validator("competence")
    @classmethod
    def _strip_competence(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("La compétence ne peut pas être vide.")
        return value
