"""Cahier PCT — assistant RAG pour le programme officiel béninois de 3e."""
import json
import os
import re
import unicodedata
from pathlib import Path

import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
CORPUS_PATH = Path(__file__).parent / "data" / "corpus.json"
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"

with CORPUS_PATH.open(encoding="utf-8") as corpus_file:
    CORPUS = json.load(corpus_file)

STOP_WORDS = set("a au aux avec ce ces dans de des du elle en et eux il ils je la le les leur lui ma mais me même mes moi mon ne nos notre nous on ou par pas pour qu que quelle quelles quel quels qui sa se ses son sur ta te tes toi ton tu un une vos votre vous y est sont".split())
VALID_MODES = {"question", "fiche", "exercices"}
EXERCISE_TYPES = {"questions à réponse courte", "exercices avec situation-problème", "QCM"}


def active_provider():
    """Free Gemini is the default when configured; Anthropic remains a fallback."""
    if os.environ.get("GEMINI_API_KEY"):
        return {"id": "gemini", "name": "Gemini 3.8 Flash", "model": GEMINI_MODEL, "configured": True}
    if os.environ.get("ANTHROPIC_API_KEY"):
        return {"id": "anthropic", "name": "Claude", "model": ANTHROPIC_MODEL, "configured": True}
    return {"id": "gemini", "name": "Gemini 3.8 Flash", "model": GEMINI_MODEL, "configured": False}


def normalize(text):
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.findall(r"[a-z0-9]+", text)


def retrieve(query, limit=5):
    query_terms = {term for term in normalize(query) if term not in STOP_WORDS and len(term) > 1}
    if not query_terms:
        return []
    scored = []
    for chunk in CORPUS:
        section = f"{chunk.get('section', '')} {chunk.get('subsection', '')}"
        section_terms = normalize(section)
        terms = normalize(section + " " + chunk.get("text", ""))
        counts = {}
        for term in terms:
            counts[term] = counts.get(term, 0) + 1
        score = sum(min(counts.get(term, 0), 5) * (2 if term in section_terms else 1) for term in query_terms)
        if score:
            scored.append((score, chunk))
    scored.sort(key=lambda item: (-item[0], item[1].get("id", "")))
    return [chunk for _, chunk in scored[:limit]]


def build_prompt(mode, query, options, sources):
    refs = "\n\n".join(
        f"[SOURCE {i} — {item.get('section')} — {item.get('subsection')}]\n{item.get('text', '')[:7000]}"
        for i, item in enumerate(sources, 1)
    )
    system = (
        "Tu es un assistant pédagogique pour les enseignants de PCT (Physique-Chimie-Technologie) "
        "au Bénin, classe de 3ème. Réponds en français. Utilise exclusivement les extraits fournis; "
        "n'invente aucun contenu officiel. Si les extraits ne permettent pas de répondre, indique-le "
        "clairement. Cite les sources avec leur section et sous-section. Distingue toute suggestion "
        "pédagogique de ce qui est prescrit par le programme."
    )
    if mode == "fiche":
        task = (f"Prépare une fiche de séance de {options['duree']}. Organise-la en compétence/capacité "
                "visée (uniquement si indiquée), objectifs, prérequis si sourcés, matériel, déroulement "
                "par étapes, évaluation et critères officiels. Signale comme proposition les éléments non prescrits.")
    elif mode == "exercices":
        task = (f"Crée {options['nombre']} {options['type']} aligné(s) sur les extraits. Fournis les consignes, "
                "une grille de correction avec barème, et rattache chaque exercice à un élément sourcé. "
                "Ne requiers pas de savoir absent des extraits.")
    else:
        task = "Réponds précisément à la question de l'enseignant et cite la section pertinente."
    user = f"EXTRAITS DU PROGRAMME OFFICIEL:\n{refs}\n\nDEMANDE:\n{query}\n\nTÂCHE:\n{task}"
    return system, user


def call_gemini(system, user):
    key = os.environ["GEMINI_API_KEY"]
    response = requests.post(
        GEMINI_URL,
        headers={"x-goog-api-key": key, "content-type": "application/json"},
        json={
            "system_instruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {"maxOutputTokens": 3000},
        },
        timeout=(10, 45),
    )
    response.raise_for_status()
    payload = response.json()
    candidates = payload.get("candidates", [])
    if not candidates:
        raise ValueError("Gemini n'a retourné aucune réponse (contenu possiblement filtré).")
    return "\n".join(part.get("text", "") for part in candidates[0].get("content", {}).get("parts", []) if part.get("text")).strip()


def call_anthropic(system, user):
    response = requests.post(
        ANTHROPIC_URL,
        headers={"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01", "content-type": "application/json"},
        json={"model": ANTHROPIC_MODEL, "max_tokens": 3000, "system": system, "messages": [{"role": "user", "content": user}]},
        timeout=(10, 45),
    )
    response.raise_for_status()
    payload = response.json()
    return "\n".join(block["text"] for block in payload.get("content", []) if block.get("type") == "text").strip()


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/health")
def health():
    provider = active_provider()
    return jsonify({"status": "ok", "corpus_chunks": len(CORPUS), "provider": provider["id"], "provider_name": provider["name"], "model": provider["model"], "api_configured": provider["configured"]})


@app.post("/api/generate")
def generate():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Corps JSON invalide."), 400
    mode, query = data.get("mode"), data.get("query")
    options = data.get("options") or {}
    if mode not in VALID_MODES:
        return jsonify(error="Mode invalide."), 400
    if not isinstance(query, str) or not query.strip():
        return jsonify(error="La question ou le thème est obligatoire."), 400
    query = query.strip()
    if len(query) > 1200:
        return jsonify(error="La demande ne peut pas dépasser 1 200 caractères."), 400
    if not isinstance(options, dict):
        return jsonify(error="Options invalides."), 400
    if mode == "fiche":
        duree = options.get("duree", "55 minutes")
        if duree not in {"55 minutes", "110 minutes"}:
            return jsonify(error="Durée de séance invalide."), 400
        options = {"duree": duree}
    elif mode == "exercices":
        try:
            nombre = int(options.get("nombre", 4))
        except (TypeError, ValueError):
            return jsonify(error="Le nombre d'exercices doit être un entier."), 400
        exercise_type = options.get("type", "questions à réponse courte")
        if not 1 <= nombre <= 10 or exercise_type not in EXERCISE_TYPES:
            return jsonify(error="Options d'exercices invalides."), 400
        options = {"nombre": nombre, "type": exercise_type}
    sources = retrieve(query)
    if not sources:
        return jsonify(error="Aucun extrait suffisamment pertinent trouvé. Reformule avec un thème ou une compétence du programme."), 422
    provider = active_provider()
    if not provider["configured"]:
        return jsonify(error="Aucune clé IA configurée. Crée gratuitement une clé Gemini AI Studio puis ajoute GEMINI_API_KEY dans l'environnement du serveur."), 503
    system, user = build_prompt(mode, query, options, sources)
    try:
        answer = call_gemini(system, user) if provider["id"] == "gemini" else call_anthropic(system, user)
    except requests.Timeout:
        app.logger.warning("AI provider request timed out (%s)", provider["id"])
        return jsonify(error="Le service IA met trop de temps à répondre. Réessaie."), 504
    except requests.HTTPError as exc:
        status = getattr(getattr(exc, "response", None), "status_code", None)
        app.logger.warning("AI provider request failed (provider=%s, status=%s)", provider["id"], status)
        if status == 429:
            message = "Le quota gratuit est temporairement atteint. Attends quelques instants ou réessaie plus tard."
            return jsonify(error=message), 429
        if status in {401, 403}:
            return jsonify(error="La clé API n'est pas acceptée. Vérifie la variable GEMINI_API_KEY côté serveur."), 502
        return jsonify(error="Le service IA a refusé la demande. Vérifie le modèle et réessaie."), 502
    except requests.RequestException:
        app.logger.exception("AI provider network failure (%s)", provider["id"])
        return jsonify(error="Le service IA est temporairement indisponible. Réessaie plus tard."), 502
    except (ValueError, KeyError, TypeError):
        app.logger.exception("Invalid AI response (%s)", provider["id"])
        return jsonify(error="Réponse invalide reçue du service IA."), 502
    if not answer:
        return jsonify(error="Aucune réponse textuelle reçue du service IA."), 502
    cited_sources = [{"section": s.get("section"), "subsection": s.get("subsection"), "id": s.get("id")} for s in sources]
    return jsonify(answer=answer, sources=cited_sources, provider=provider["name"])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
