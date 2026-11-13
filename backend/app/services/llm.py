"""Client LLM : API Anthropic côté serveur, avec repli explicite en mode démo."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..errors import LLMError


@dataclass
class LLMResponse:
    text: str
    model: str
    mode: str  # "live" | "mock"
    usage: dict[str, Any] = field(default_factory=dict)


class LLMService:
    """Encapsule l'appel à Anthropic.

    La clé ne quitte jamais le serveur. Le mode `mock` ne produit aucun appel
    réseau : les générateurs construisent alors une réponse de démonstration à
    partir des extraits récupérés.
    """

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        mode: str = "auto",
        max_tokens: int = 4096,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.requested_mode = (mode or "auto").lower()
        self.max_tokens = max_tokens
        self._client = None

    @property
    def mode(self) -> str:
        if self.requested_mode == "mock":
            return "mock"
        if self.requested_mode == "live":
            return "live"
        return "live" if self.api_key else "mock"

    @property
    def is_live(self) -> bool:
        return self.mode == "live"

    def _get_client(self):
        if self._client is not None:
            return self._client
        if not self.api_key:
            raise LLMError(
                "Aucune clé API Anthropic n'est configurée.",
                details={"hint": "Renseignez ANTHROPIC_API_KEY dans .env."},
            )
        try:
            import anthropic
        except ImportError as exc:  # pragma: no cover - dépendance installée
            raise LLMError("Le paquet `anthropic` n'est pas installé.") from exc

        self._client = anthropic.Anthropic(api_key=self.api_key)
        return self._client

    def complete(
        self,
        prompt: str,
        *,
        system: str | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        if not self.is_live:
            raise LLMError(
                "Le client LLM est en mode démonstration.",
                details={"mode": "mock"},
            )

        client = self._get_client()
        try:
            message = client.messages.create(
                model=self.model,
                max_tokens=max_tokens or self.max_tokens,
                system=system or "",
                messages=[{"role": "user", "content": prompt}],
            )
        except Exception as exc:  # l'SDK lève plusieurs types d'erreurs
            raise LLMError(
                "L'appel au service d'IA a échoué.",
                details={"type": type(exc).__name__, "message": str(exc)},
            ) from exc

        text = "".join(
            block.text for block in message.content if getattr(block, "type", "") == "text"
        )
        usage = {}
        if getattr(message, "usage", None):
            usage = {
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens,
            }

        return LLMResponse(
            text=text.strip(),
            model=self.model,
            mode="live",
            usage=usage,
        )
