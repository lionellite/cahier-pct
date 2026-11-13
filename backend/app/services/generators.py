"""Génération des trois modes : question, fiche de cours, exercices."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from collections.abc import Sequence

from ..errors import ApiError
from ..prompts import context_block, render, system_prompt
from .corpus import Corpus, Extract
from .llm import LLMService

MOCK_NOTICE = (
    "> **Mode démonstration.** Aucune clé API n'est configurée : le contenu ci-dessous "
    "est un extrait brut du corpus, pas une réponse générée. Renseignez "
    "`ANTHROPIC_API_KEY` dans `.env` pour activer la génération."
)


@dataclass
class GenerationResult:
    mode: str
    content: str
    citations: list[dict[str, Any]]
    retrieved: list[dict[str, Any]]
    model: str
    llm_mode: str
    usage: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "content": self.content,
            "citations": self.citations,
            "retrieved": self.retrieved,
            "model": self.model,
            "llm_mode": self.llm_mode,
            "usage": self.usage,
        }


def _page_range(pages: list[Any]) -> str:
    """Compresses a page list into ranges: [41..77] -> "41-77", [1,2,3,9] -> "1-3, 9"."""
    numbers = sorted({int(p) for p in pages if str(p).isdigit()})
    if not numbers:
        return "n/c"
    groups: list[list[int]] = [[numbers[0]]]
    for n in numbers[1:]:
        if n == groups[-1][-1] + 1:
            groups[-1].append(n)
        else:
            groups.append([n])
    parts: list[str] = []
    for group in groups:
        if len(group) == 1:
            parts.append(str(group[0]))
        elif len(group) == 2:
            parts.append(f"{group[0]}-{group[1]}")
        else:
            parts.append(f"{group[0]}-{group[-1]}")
    return ", ".join(parts)


def _citation(extract: Extract) -> dict[str, Any]:
    return {
        "extract_id": extract.id,
        "title": extract.title,
        "type": extract.type,
        "reference": extract.reference,
        "pages": extract.source.get("pages", []),
        "status": extract.status,
    }


def _retrieved(hits: list[tuple[Extract, float]]) -> list[dict[str, Any]]:
    return [
        {
            "extract_id": extract.id,
            "title": extract.title,
            "type": extract.type,
            "score": round(score, 4),
            "status": extract.status,
        }
        for extract, score in hits
    ]


def _citations(hits: list[tuple[Extract, float]]) -> list[dict[str, Any]]:
    return [_citation(extract) for extract, _score in hits]


def _level(
    corpus: Corpus, level: str | None, extracts: Sequence[Extract] | None = None
) -> str:
    """Niveau explicite > niveau du premier extrait récupéré > manifeste > 3e."""
    if level:
        return level
    if extracts:
        for extract in extracts:
            if extract.level and extract.level != "tous":
                return extract.level
    return str(corpus.manifest.get("level") or "3e")


def _excerpt(text: str, limit: int = 1600) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + " […]"


def _mock_extract_section(extract: Extract, *, limit: int = 1600) -> str:
    return "\n".join(
        [
            f"### {extract.title}",
            f"*{extract.type} — {extract.reference}*",
            "",
            _excerpt(extract.content, limit),
            "",
            f"[Réf : {extract.id} — {extract.title}, p. {_page_range(extract.source.get('pages', []))}]",
        ]
    )


def _require_hits(
    hits: list[tuple[Extract, float]], competence: str
) -> list[tuple[Extract, float]]:
    if not hits:
        raise ApiError(
            404,
            "Aucun extrait du programme ne correspond à cette compétence.",
            code="no_match",
            details={"competence": competence},
        )
    return hits


# --------------------------------------------------------------------------- #
# Mode Question
# --------------------------------------------------------------------------- #


def generate_question(
    corpus: Corpus,
    llm: LLMService,
    *,
    question: str,
    level: str | None = None,
    top_k: int = 5,
) -> GenerationResult:
    hits = corpus.search(question, top_k=top_k)
    if not hits:
        return GenerationResult(
            mode="question",
            content=(
                "Le programme fourni ne contient pas d'élément permettant de répondre "
                "à cette question.\n\n"
                "Reformulez la question avec les termes du programme (nom de la "
                "compétence, de la capacité ou du thème), ou consultez directement "
                "les extraits disponibles dans l'onglet **Corpus**."
            ),
            citations=[],
            retrieved=[],
            model=llm.model,
            llm_mode=llm.mode,
        )

    extracts = [extract for extract, _score in hits]

    if llm.is_live:
        prompt = render(
            "question",
            QUESTION=question,
            CONTEXT=context_block(extracts),
        )
        response = llm.complete(prompt, system=system_prompt())
        content = response.text
        usage = response.usage
    else:
        content = "\n\n".join(
            [
                MOCK_NOTICE,
                "## Extraits du programme correspondant à votre question",
                *(_mock_extract_section(extract) for extract in extracts),
            ]
        )
        usage = {}

    return GenerationResult(
        mode="question",
        content=content,
        citations=_citations(hits),
        retrieved=_retrieved(hits),
        model=llm.model,
        llm_mode=llm.mode,
        usage=usage,
    )


# --------------------------------------------------------------------------- #
# Mode Fiche de cours
# --------------------------------------------------------------------------- #


def generate_fiche(
    corpus: Corpus,
    llm: LLMService,
    *,
    competence: str,
    level: str | None = None,
    duration: str | None = None,
    class_size: str | None = None,
    context: str | None = None,
) -> GenerationResult:
    hits = _require_hits(corpus.resolve(competence, top_k=3), competence)
    extracts = [extract for extract, _score in hits]
    resolved_level = _level(corpus, level, extracts)

    if llm.is_live:
        prompt = render(
            "fiche",
            COMPETENCE=competence,
            LEVEL=resolved_level,
            DURATION=duration or "à préciser",
            CLASS_SIZE=class_size or "non précisé",
            CONTEXT_NOTE=context or "aucun",
            CONTEXT=context_block(extracts),
        )
        response = llm.complete(prompt, system=system_prompt())
        content = response.text
        usage = response.usage
    else:
        main = extracts[0]
        content = "\n\n".join(
            [
                MOCK_NOTICE,
                f"# Fiche de préparation — {main.title}",
                "## 1. Identification",
                f"- **Niveau** : {resolved_level}",
                f"- **Durée** : {duration or 'à préciser'}",
                f"- **Effectif** : {class_size or 'non précisé'}",
                f"- **Compétence / capacité** : {competence}",
                "",
                "## 2. Éléments du programme",
                *(_mock_extract_section(extract) for extract in extracts),
                "## 3. À compléter en mode live",
                "Les sections objectifs, déroulement, matériel et évaluation sont "
                "produites par le modèle à partir de ces extraits. Configurez "
                "`ANTHROPIC_API_KEY` pour générer la fiche complète.",
            ]
        )
        usage = {}

    return GenerationResult(
        mode="fiche",
        content=content,
        citations=_citations(hits),
        retrieved=_retrieved(hits),
        model=llm.model,
        llm_mode=llm.mode,
        usage=usage,
    )


# --------------------------------------------------------------------------- #
# Mode Exercices
# --------------------------------------------------------------------------- #


def generate_exercices(
    corpus: Corpus,
    llm: LLMService,
    *,
    competence: str,
    level: str | None = None,
    count: int = 5,
    with_correction: bool = True,
    difficulty: str | None = None,
    context: str | None = None,
) -> GenerationResult:
    hits = _require_hits(corpus.resolve(competence, top_k=3), competence)
    extracts = [extract for extract, _score in hits]
    resolved_level = _level(corpus, level, extracts)

    if llm.is_live:
        prompt = render(
            "exercices",
            COMPETENCE=competence,
            LEVEL=resolved_level,
            COUNT=count,
            DIFFICULTY=difficulty or "progressive",
            WITH_CORRECTION="oui" if with_correction else "non (sujet seul)",
            CONTEXT_NOTE=context or "aucun",
            CONTEXT=context_block(extracts),
        )
        response = llm.complete(prompt, system=system_prompt())
        content = response.text
        usage = response.usage
    else:
        main = extracts[0]
        content = "\n\n".join(
            [
                MOCK_NOTICE,
                f"# Évaluation — {main.title}",
                "## A. Cadre de l'évaluation",
                f"- **Niveau** : {resolved_level}",
                f"- **Nombre d'exercices demandés** : {count}",
                f"- **Difficulté** : {difficulty or 'progressive'}",
                f"- **Grille de correction** : {'oui' if with_correction else 'non'}",
                f"- **Compétence / capacité** : {competence}",
                "",
                "## B. Éléments du programme mobilisables",
                *(_mock_extract_section(extract) for extract in extracts),
                "## C. À compléter en mode live",
                "Les énoncés et la grille de correction sont produits par le modèle "
                "à partir de ces extraits. Configurez `ANTHROPIC_API_KEY` pour "
                "générer l'évaluation complète.",
            ]
        )
        usage = {}

    return GenerationResult(
        mode="exercices",
        content=content,
        citations=_citations(hits),
        retrieved=_retrieved(hits),
        model=llm.model,
        llm_mode=llm.mode,
        usage=usage,
    )
