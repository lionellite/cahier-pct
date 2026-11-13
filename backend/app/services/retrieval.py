"""Recherche lexicale BM25, en Python pur.

Aucun service externe, aucune dépendance : le corpus tient en quelques dizaines
d'extraits et doit rester interrogeable hors ligne et à faible coût.
"""

from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass

_WORD_RE = re.compile(r"[a-z0-9]+")

# Mots vides français. Liste volontairement courte : mieux vaut un rappel un peu
# large qu'un mot-clé utile supprimé par erreur.
STOPWORDS: frozenset[str] = frozenset(
    """
    a au aux avec ce ces cet cette dans de des du elle en et eux il ils je la le
    les leur lui ma mais me meme mes moi mon ne nos notre nous on ou par pas pour
    qu que qui sa se ses son sur ta te tes toi ton tu un une vos votre vous y
    quel quelle quelles quels quoi
    est sont etre avoir a ai as avons avez ont fait faire plus moins tres tout
    tous toute toutes comme aussi donc alors si non oui
    """.split()
)


def normalize(text: str) -> str:
    """Minuscules, sans accents, ponctuation remplacée par des espaces."""
    decomposed = unicodedata.normalize("NFD", text)
    stripped = "".join(c for c in decomposed if unicodedata.category(c) != "Mn")
    return stripped.lower()


def tokenize(text: str) -> list[str]:
    return [
        token
        for token in _WORD_RE.findall(normalize(text))
        if len(token) > 1 and token not in STOPWORDS
    ]


@dataclass(frozen=True)
class SearchHit:
    doc_id: str
    score: float


class BM25Index:
    """Implémentation classique de BM25 (k1=1.5, b=0.75)."""

    def __init__(self, documents: dict[str, str], *, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_ids: list[str] = list(documents.keys())
        self.doc_tokens: dict[str, list[str]] = {
            doc_id: tokenize(text) for doc_id, text in documents.items()
        }
        self.doc_freqs: Counter[str] = Counter()
        self.term_freqs: dict[str, Counter[str]] = {}
        self.doc_lengths: dict[str, int] = {}

        for doc_id, tokens in self.doc_tokens.items():
            frequencies = Counter(tokens)
            self.term_freqs[doc_id] = frequencies
            self.doc_lengths[doc_id] = len(tokens)
            for term in frequencies:
                self.doc_freqs[term] += 1

        total = sum(self.doc_lengths.values())
        self.avg_length = total / len(self.doc_ids) if self.doc_ids else 0.0
        self._size = len(self.doc_ids)

    def _idf(self, term: str) -> float:
        df = self.doc_freqs.get(term, 0)
        if df == 0:
            return 0.0
        return math.log(1 + (self._size - df + 0.5) / (df + 0.5))

    def search(self, query: str, top_k: int = 5) -> list[SearchHit]:
        terms = tokenize(query)
        if not terms or not self.doc_ids:
            return []

        scores: dict[str, float] = {}
        for doc_id in self.doc_ids:
            frequencies = self.term_freqs[doc_id]
            length = self.doc_lengths[doc_id] or 1
            score = 0.0
            for term in terms:
                tf = frequencies.get(term, 0)
                if not tf:
                    continue
                denominator = tf + self.k1 * (
                    1 - self.b + self.b * (length / (self.avg_length or 1))
                )
                score += self._idf(term) * (tf * (self.k1 + 1)) / denominator
            if score > 0:
                scores[doc_id] = score

        ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        return [SearchHit(doc_id, score) for doc_id, score in ranked[:top_k]]
