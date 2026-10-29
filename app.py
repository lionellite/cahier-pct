"""Cahier PCT: assistant RAG pour le programme officiel béninois de 3e."""
import json
import os
import re
import unicodedata
from pathlib import Path

import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
API_URL = "https://api.anthropic.com/v1/messages"
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")
CORPUS_PATH = Path(__file__).parent / "data" / "corpus.json"

with CORPUS_PATH.open(encoding="utf-8") as corpus_file:
    CORPUS = json.load(corpus_file)

STOP_WORDS = set("a au aux avec ce ces dans de des du elle en et eux il ils je la le les leur lui ma mais me même mes moi mon ne nos notre nous on ou par pas pour qu que quelle quelles quel quels qui sa se ses son sur ta te tes toi ton tu un une vos votre vous y est sont".split())
VALID_MODES = {"question", "fiche", "exercices"}
EXERCISE_TYPES = {"questions à réponse courte", "exercices avec situation-problème", "QCM"}


def normalize(text):
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.findall(r"[a-z0-9]+", text)


def retrieve(query, limit=5):
    """Lexical retrieval with phrase/number bonuses, no external dependencies."""
    query_terms = {term for term in normalize(query) if term not in STOP_WORDS and len(term) > 1}
    if not query_terms:
        return []
    scored = []
    for chunk in CORPUS:
        section = f"{chunk.get('section', '')} {chunk.get('subsection', '')}"
        terms = normalize(section + " " + chunk.get("text", ""))
        counts = {}
        for term in terms:
            counts[term] = counts.get(term, 0) + 1
        score = sum(min(counts.get(term, 0), 5) * (2 if term in normalize(section) else 1) for term in query_terms)
        if score:
            scored.append((score, chunk))
    scored.sort(key=lambda item: (-item[0], item[1].get("id", "")))
    return [chunk for _, chunk in scored[:limit]]


def build_prompt(mode, query, options, sources):
    refs = "\n\n".join(
        f"[SOURCE {i} — {item.get('section')} — {item.get('subsection')}]\n{item.get('text', '')}"
        for i, item in enumerate(sources, 1)
    )
    base = (
        "Tu es un assistant pédagogique pour les enseignants de PCT (Physique-Chimie-Technologie) "
        "au Bénin, classe de 3ème. Réponds en français. Utilise exclusivement les extraits fournis; "
        "n'invente aucun contenu officiel. Si les extraits ne permettent pas de répondre, indique-le "
        "clairement. Cite les sources avec leur section et sous-section. Distingue explicitement toute "
        "suggestion pédagogique de ce qui est prescrit par le programme."
    )
    if mode == "fiche":
        task = (f"Prépare une fiche de séance de {options['duree']}. Structure-la en: compétence/capacité "
                "visée (seulement si indiquée dans les extraits), objectifs, prérequis si sourcés, matériel, "
                "déroulement par étapes, évaluation et critères officiels. Signale comme proposition les éléments non explicitement prescrits.")
    elif mode == "exercices":
        task = (f"Crée {options['nombre']} {options['type']} aligné(s) sur les extraits. Fournis les consignes, "
                "puis une grille de correction/barème et rattache chaque exercice à la capacité ou au critère sourcé. "
                "Ne requiers pas de savoir absent des extraits.")
    else:
        task = "Réponds précisément à la question de l'enseignant et cite la section pertinente."
    user = f"EXTRAITS DU PROGRAMME OFFICIEL:\n{refs}\n\nDEMANDE:\n{query}\n\nTÂCHE:\n{task}"
    return base, user


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "corpus_chunks": len(CORPUS), "api_configured": bool(os.environ.get("ANTHROPIC_API_KEY"))})


@app.post("/api/generate")
def generate():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Corps JSON invalide."), 400
    mode = data.get("mode")
    query = data.get("query")
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
        return jsonify(error="Aucun extrait suffisamment pertinent trouvé dans le corpus. Reformule avec un thème ou une compétence du programme."), 422
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return jsonify(error="Le service IA n'est pas configuré. Ajoutez ANTHROPIC_API_KEY dans les variables d'environnement du serveur."), 503
    system, user = build_prompt(mode, query, options, sources)
    try:
        response = requests.post(
            API_URL,
            headers={"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": MODEL, "max_tokens": 3000, "system": system, "messages": [{"role": "user", "content": user}]},
            timeout=(10, 90),
        )
        response.raise_for_status()
        payload = response.json()
    except requests.Timeout:
        app.logger.warning("Anthropic request timed out")
        return jsonify(error="Le service IA met trop de temps à répondre. Réessaie."), 504
    except requests.RequestException as exc:
        status = getattr(getattr(exc, "response", None), "status_code", None)
        app.logger.warning("Anthropic API request failed (status=%s)", status)
        return jsonify(error="Le service IA est temporairement indisponible. Réessaie plus tard."), 502
    except (ValueError, KeyError, TypeError):
        app.logger.exception("Invalid Anthropic response")
        return jsonify(error="Réponse invalide reçue du service IA."), 502
    answer = "\n".join(block["text"] for block in payload.get("content", []) if block.get("type") == "text").strip()
    if not answer:
        return jsonify(error="Aucune réponse textuelle reçue du service IA."), 502
    cited_sources = [{"section": s.get("section"), "subsection": s.get("subsection"), "id": s.get("id")} for s in sources]
    return jsonify(answer=answer, sources=cited_sources)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
