"""Chargement et interrogation du corpus officiel structuré."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

from ..errors import CorpusError
from .retrieval import BM25Index, SearchHit

REQUIRED_FIELDS = ("id", "title", "type", "content", "source")


@dataclass(frozen=True)
class Extract:
    id: str
    title: str
    type: str
    content: str
    source: dict[str, Any]
    level: str = "3e"
    status: str = "draft"
    metadata: dict[str, Any] = field(default_factory=dict)
    version: int = 1

    def summary(self) -> dict[str, Any]:
        pages = self.source.get("pages") or []
        return {
            "id": self.id,
            "title": self.title,
            "type": self.type,
            "level": self.level,
            "status": self.status,
            "pages": pages,
            "reference": self.reference,
            "tags": self.metadata.get("tags", []),
        }

    def to_dict(self) -> dict[str, Any]:
        payload = self.summary()
        payload.update(
            {
                "content": self.content,
                "source": self.source,
                "metadata": self.metadata,
                "version": self.version,
            }
        )
        return payload

    @property
    def reference(self) -> str:
        document = self.source.get("document", "Programme officiel")
        pages = self.source.get("pages") or []
        if not pages:
            return document
        if len(pages) == 1:
            return f"{document}, p. {pages[0]}"
        return f"{document}, p. {pages[0]}-{pages[-1]}"

    @classmethod
    def from_dict(cls, data: dict[str, Any], *, fallback_level: str = "3e") -> Extract:
        missing = [name for name in REQUIRED_FIELDS if not data.get(name)]
        if missing:
            raise CorpusError(
                f"Extrait invalide : champs manquants {missing}.",
                details={"id": data.get("id")},
            )
        return cls(
            id=str(data["id"]),
            title=str(data["title"]),
            type=str(data["type"]),
            content=str(data["content"]).strip(),
            source=dict(data.get("source") or {}),
            level=str(data.get("level", fallback_level)),
            status=str(data.get("status", "draft")),
            metadata=dict(data.get("metadata") or {}),
            version=int(data.get("version", 1)),
        )


class Corpus:
    """Corpus en mémoire : manifeste + extraits + index BM25."""

    def __init__(self, path: Path, manifest: dict[str, Any], extracts: dict[str, Extract]):
        self.path = path
        self.manifest = manifest
        self.extracts = extracts
        documents = {
            extract.id: " ".join(
                [
                    extract.title,
                    extract.title,  # le titre pèse double dans l'index
                    extract.type,
                    extract.content,
                    " ".join(map(str, extract.metadata.get("tags", []))),
                    " ".join(map(str, extract.metadata.get("capacites", []))),
                ]
            )
            for extract in extracts.values()
        }
        self.index = BM25Index(documents)

    @classmethod
    def load(cls, path: Path) -> Corpus:
        path = Path(path)
        manifest_path = path / "manifest.json"
        if not manifest_path.exists():
            raise CorpusError(
                f"Manifeste introuvable : {manifest_path}.",
                details={"hint": "Voir docs/02-corpus.md pour la structure attendue."},
            )

        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise CorpusError(f"Manifeste illisible : {exc}") from exc

        fallback_level = str(manifest.get("level", "3e"))
        extracts: dict[str, Extract] = {}

        for entry in manifest.get("extracts", []):
            file_name = entry.get("file")
            if not file_name:
                raise CorpusError(
                    "Chaque entrée du manifeste doit référencer un fichier.",
                    details={"entry": entry},
                )
            extract_path = path / file_name
            if not extract_path.exists():
                raise CorpusError(
                    f"Fichier d'extrait introuvable : {extract_path}.",
                    details={"id": entry.get("id")},
                )
            try:
                data = json.loads(extract_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise CorpusError(f"Extrait illisible ({extract_path}) : {exc}") from exc

            extract = Extract.from_dict(data, fallback_level=fallback_level)
            if extract.id in extracts:
                raise CorpusError(f"Identifiant d'extrait en double : {extract.id}.")
            extracts[extract.id] = extract

        if not extracts:
            raise CorpusError("Le corpus ne contient aucun extrait.")

        return cls(path, manifest, extracts)

    # --- Lecture -----------------------------------------------------------

    def list_extracts(
        self, *, type_: str | None = None, status: str | None = None
    ) -> list[dict[str, Any]]:
        rows = [
            extract.summary()
            for extract in self.extracts.values()
            if (type_ is None or extract.type == type_)
            and (status is None or extract.status == status)
        ]
        return sorted(rows, key=lambda row: (row["type"], row["title"]))

    def get(self, extract_id: str) -> Extract | None:
        return self.extracts.get(extract_id)

    def search(self, query: str, top_k: int = 5) -> list[tuple[Extract, float]]:
        hits: list[SearchHit] = self.index.search(query, top_k=top_k)
        return [
            (self.extracts[hit.doc_id], hit.score)
            for hit in hits
            if hit.doc_id in self.extracts
        ]

    def resolve(self, value: str, *, top_k: int = 3) -> list[tuple[Extract, float]]:
        """Résout un identifiant exact ou une recherche libre."""
        if value in self.extracts:
            return [(self.extracts[value], 1.0)]
        return self.search(value, top_k=top_k)

    # --- Statistiques ------------------------------------------------------

    def stats(self) -> dict[str, Any]:
        by_type = Counter(extract.type for extract in self.extracts.values())
        by_status = Counter(extract.status for extract in self.extracts.values())
        expected = int(self.manifest.get("expected_extracts") or len(self.extracts))
        return {
            "id": self.manifest.get("id", self.path.name),
            "level": self.manifest.get("level"),
            "discipline": self.manifest.get("discipline"),
            "program": self.manifest.get("program", {}),
            "extract_count": len(self.extracts),
            "expected_extracts": expected,
            "completion": round(len(self.extracts) / expected, 3) if expected else None,
            "characters": sum(len(extract.content) for extract in self.extracts.values()),
            "by_type": dict(sorted(by_type.items())),
            "by_status": dict(sorted(by_status.items())),
            "validated": by_status.get("validated", 0),
        }


class CorpusSet:
    """Collection de corpus agrégés (un sous-dossier par programme/manif cultures).

    Expose la même interface qu'un Corpus unique `list/get/search/resolve/stats` :
    l'index BM25 est reconstruit sur l'ensemble des extraits, et les identifiants
    d'extraits doivent rester uniques (préfixe par niveau : `3e-`, `3e-prog-`, ...).
    """

    def __init__(self, path: Path, corpora: list[Corpus]):
        self.path = path
        self.corpora = corpora
        extracts: dict[str, Extract] = {}
        for corpus in corpora:
            for extract_id, extract in corpus.extracts.items():
                if extract_id in extracts:
                    raise CorpusError(
                        f"Identifiant d'extrait en double entre corpus : {extract_id}."
                    )
                extracts[extract_id] = extract
        self.extracts = extracts
        self.index = BM25Index(_documents(extracts))
        levels = {c.manifest.get("level") for c in self.corpora if c.manifest.get("level")}
        self.manifest = {
            "id": self.path.name,
            "discipline": next(iter(
                {c.manifest.get("discipline") for c in self.corpora if c.manifest.get("discipline")}
            ), None),
            "level": next(iter(levels), None) if len(levels) == 1 else None,
            "levels": sorted(levels),
        }

    # --- Lecture (même interface que Corpus) --------------------------------

    def list_extracts(
        self, *, type_: str | None = None, status: str | None = None
    ) -> list[dict[str, Any]]:
        rows = [
            extract.summary()
            for extract in self.extracts.values()
            if (type_ is None or extract.type == type_)
            and (status is None or extract.status == status)
        ]
        return sorted(rows, key=lambda row: (row["type"], row["title"]))

    def get(self, extract_id: str) -> Extract | None:
        return self.extracts.get(extract_id)

    def search(self, query: str, top_k: int = 5) -> list[tuple[Extract, float]]:
        hits: list[SearchHit] = self.index.search(query, top_k=top_k)
        return [
            (self.extracts[hit.doc_id], hit.score)
            for hit in hits
            if hit.doc_id in self.extracts
        ]

    def resolve(self, value: str, *, top_k: int = 3) -> list[tuple[Extract, float]]:
        """Résout un identifiant exact ou une recherche libre."""
        if value in self.extracts:
            return [(self.extracts[value], 1.0)]
        return self.search(value, top_k=top_k)

    def stats(self) -> dict[str, Any]:
        by_type = Counter(extract.type for extract in self.extracts.values())
        by_status = Counter(extract.status for extract in self.extracts.values())
        expected = sum(
            int(c.manifest.get("expected_extracts") or len(c.extracts))
            for c in self.corpora
        )
        levels = self.manifest.get("levels") or []
        return {
            "id": self.path.name,
            "level": levels[0] if len(levels) == 1 else None,
            "levels": levels,
            "extract_count": len(self.extracts),
            "expected_extracts": expected,
            "completion": round(len(self.extracts) / expected, 3) if expected else None,
            "characters": sum(len(extract.content) for extract in self.extracts.values()),
            "by_type": dict(sorted(by_type.items())),
            "by_status": dict(sorted(by_status.items())),
            "validated": by_status.get("validated", 0),
            "corpora": [
                {
                    "id": corpus.manifest.get("id", corpus.path.name),
                    "level": corpus.manifest.get("level"),
                    "extract_count": len(corpus.extracts),
                    "expected_extracts": int(
                        corpus.manifest.get("expected_extracts") or len(corpus.extracts)
                    ),
                    "completion": corpus.stats()["completion"],
                }
                for corpus in self.corpora
            ],
        }


def _documents(extracts: dict[str, Extract]) -> dict[str, str]:
    """Texte indexer par extrait : titre pondéré double, type, tags, capacités."""
    return {
        extract.id: " ".join(
            [
                extract.title,
                extract.title,  # le titre pèse double dans l'index
                extract.type,
                extract.content,
                " ".join(map(str, extract.metadata.get("tags", []))),
                " ".join(map(str, extract.metadata.get("capacites", []))),
            ]
        )
        for extract in extracts.values()
    }


@lru_cache(maxsize=8)
def _load_corpus(path: str) -> CorpusSet:
    root = Path(path)
    if (root / "manifest.json").exists():
        corpora = [Corpus.load(root)]
    else:
        corpora = [
            Corpus.load(subdir)
            for subdir in sorted(root.iterdir())
            if subdir.is_dir() and (subdir / "manifest.json").exists()
        ]
    if not corpora:
        raise CorpusError(
            f"Aucun manifeste de corpus trouvé sous : {root}.",
            details={"hint": "Voir docs/02-corpus.md pour la structure attendue."},
        )
    return CorpusSet(root, corpora)


def get_corpus(path: str | Path) -> CorpusSet:
    return _load_corpus(str(Path(path).resolve()))


def clear_corpus_cache() -> None:
    _load_corpus.cache_clear()
