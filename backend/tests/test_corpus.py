from __future__ import annotations

from app.config import Config
from app.services.corpus import get_corpus


def test_corpus_loads():
    corpus = get_corpus(Config.CORPUS_PATH)
    assert len(corpus.extracts) >= 8
    levels = {c.manifest.get("level") for c in corpus.corpora}
    assert levels == {"3e", "6e", "2de", "1e", "tous"}


def test_corpus_search_finds_sa1():
    corpus = get_corpus(Config.CORPUS_PATH)
    hits = corpus.search("equilibre d'un solide", top_k=5)
    ids = [extract.id for extract, _score in hits]
    assert "3e-sa1-equilibre-solide" in ids


def test_corpus_resolve_by_id():
    corpus = get_corpus(Config.CORPUS_PATH)
    hits = corpus.resolve("3e-sa1-equilibre-solide")
    assert hits[0][0].id == "3e-sa1-equilibre-solide"


def test_corpus_stats_aggregates():
    corpus = get_corpus(Config.CORPUS_PATH)
    stats = corpus.stats()
    assert stats["extract_count"] == len(corpus.extracts)
    assert stats["expected_extracts"] >= stats["extract_count"]
    assert stats["characters"] > 0
    assert stats["completion"] is not None
    assert {c["id"] for c in stats["corpora"]} == {
        "pct-3e",
        "pct-3e-prog",
        "pct-6e",
        "pct-6e-prog",
        "pct-2de",
        "pct-2de-prog",
        "amenagement-sa-2de",
        "pct-1e",
        "pct-1e-prog",
        "igpm-epreuves",
        "pct-transversal",
    }
    assert stats["level"] is None  # niveaux multiples : niveau par corpus
