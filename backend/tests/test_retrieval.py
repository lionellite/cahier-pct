from __future__ import annotations

from app.services.retrieval import BM25Index, normalize, tokenize


def test_normalize_removes_accents_and_case():
    assert normalize("Masse Volumique Éprouvette") == "masse volumique eprouvette"


def test_tokenize_filters_stopwords():
    tokens = tokenize("la masse et le volume d'un corps")
    assert "masse" in tokens
    assert "volume" in tokens
    assert "corps" in tokens
    assert "la" not in tokens
    assert "et" not in tokens


def test_bm25_ranks_relevant_document_first():
    index = BM25Index(
        {
            "a": "masse volumique mesurer balance éprouvette volume",
            "b": "énergie mécanique force travail puissance",
            "c": "cellule génétique reproduction",
        }
    )
    hits = index.search("comment calculer une masse volumique", top_k=2)
    assert hits
    assert hits[0].doc_id == "a"


def test_bm25_returns_empty_without_match():
    index = BM25Index({"a": "masse volumique"})
    assert index.search("philosophie médiévale") == []


def test_bm25_handles_empty_index():
    index = BM25Index({})
    assert index.search("masse") == []


def test_bm25_ignores_empty_query():
    index = BM25Index({"a": "masse volumique"})
    assert index.search("   ") == []
