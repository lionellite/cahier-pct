from __future__ import annotations


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "ok"


def test_meta_reports_corpus_and_mock_mode(client):
    response = client.get("/api/meta")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["llm"]["mode"] == "mock"
    assert payload["llm"]["live"] is False
    assert payload["corpus"]["extract_count"] >= 3


def test_list_corpus(client):
    response = client.get("/api/corpus")
    assert response.status_code == 200
    payload = response.get_json()
    assert len(payload["extracts"]) >= 3
    assert "completion" in payload["corpus"]


def test_get_extract(client):
    response = client.get("/api/corpus/3e-sa1-equilibre-solide")
    assert response.status_code == 200
    extract = response.get_json()["extract"]
    assert "EQUILIBRE" in extract["content"].upper()


def test_get_unknown_extract(client):
    response = client.get("/api/corpus/inconnu")
    assert response.status_code == 404
    assert response.get_json()["error"]["code"] == "extract_not_found"


def test_question_returns_citations_in_mock_mode(client):
    response = client.post(
        "/api/question",
        json={"question": "Comment calculer la masse volumique d'un corps ?"},
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["mode"] == "question"
    assert payload["llm_mode"] == "mock"
    assert payload["citations"]
    assert "démonstration" in payload["content"].lower()


def test_question_without_match_returns_safe_answer(client):
    response = client.post(
        "/api/question",
        json={"question": "Quelle est la recette du foutou ?"},
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["citations"] == []
    assert "ne contient pas" in payload["content"]


def test_question_validation_error(client):
    response = client.post("/api/question", json={"question": "a"})
    assert response.status_code == 422
    assert response.get_json()["error"]["code"] == "validation_error"


def test_question_requires_json(client):
    response = client.post("/api/question", data="pas du json")
    assert response.status_code == 400


def test_fiche(client):
    response = client.post(
        "/api/fiche",
        json={
            "competence": "masse volumique",
            "duration": "2 h",
            "class_size": "60",
        },
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["mode"] == "fiche"
    assert payload["citations"]


def test_fiche_unknown_competence(client):
    response = client.post("/api/fiche", json={"competence": "zzzz"})
    assert response.status_code == 404
    assert response.get_json()["error"]["code"] == "no_match"


def test_exercices(client):
    response = client.post(
        "/api/exercices",
        json={"competence": "masse volumique", "count": 3},
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["mode"] == "exercices"
    assert payload["citations"]


def test_exercices_count_validation(client):
    response = client.post(
        "/api/exercices",
        json={"competence": "masse volumique", "count": 50},
    )
    assert response.status_code == 422
