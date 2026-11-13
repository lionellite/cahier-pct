"""Erreurs applicatives et gestion uniforme des réponses d'erreur."""

from __future__ import annotations

from typing import Any


class ApiError(Exception):
    """Erreur destinée à être renvoyée telle quelle au client."""

    def __init__(
        self,
        status: int,
        message: str,
        *,
        code: str = "api_error",
        details: Any = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.message = message
        self.code = code
        self.details = details

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"error": {"code": self.code, "message": self.message}}
        if self.details is not None:
            payload["error"]["details"] = self.details
        return payload


class CorpusError(ApiError):
    def __init__(self, message: str, *, details: Any = None) -> None:
        super().__init__(500, message, code="corpus_error", details=details)


class LLMError(ApiError):
    def __init__(self, message: str, *, details: Any = None) -> None:
        super().__init__(502, message, code="llm_error", details=details)
