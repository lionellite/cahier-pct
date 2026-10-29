# Cahier PCT — assistant RAG enseignant

Application web mobile pour les enseignants de Physique-Chimie-Technologie (PCT) de 3e au Bénin. Le corpus contient 32 extraits du programme officiel certifié 2020. Les modes Question, Fiche de cours et Exercices récupèrent des extraits pertinents côté serveur et demandent une réponse Claude ancrée dans ces sources.

## Lancer en local

```bash
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY="votre-cle"  # ne jamais committer cette clé
python app.py
```

Ouvrir http://localhost:5000. Le serveur écoute le port défini par `PORT` (5000 par défaut). Le modèle est `claude-sonnet-4-6`, ajustable via `ANTHROPIC_MODEL`. L’application ne fonctionne pas en génération sans clé API Anthropic configurée côté serveur; les fonctions `/` et `/api/health` restent utilisables. L’endpoint de santé n’expose pas la clé.

Pour un déploiement WSGI: `gunicorn app:app`. Ajouter `ANTHROPIC_API_KEY` comme secret d’environnement chez l’hébergeur. Ne jamais placer de clé dans le frontend ou dans Git.

## API

- `GET /api/health` — état minimal et nombre d’extraits.
- `POST /api/generate` — JSON `{ "mode": "question|fiche|exercices", "query": "...", "options": {} }`. Les options sont `duree` (55/110 minutes) pour une fiche, et `nombre` (1–10), `type` pour des exercices. Les sources retenues sont renvoyées avec la réponse.

Le corpus est versionné dans `data/corpus.json`; la sélection lexicale est volontairement légère pour le prototype et ne remplace pas une validation pédagogique. Les sections « Situations d’apprentissage » restent celles de l’extraction existante et comportent les limites décrites dans le cahier des charges.

## Tests

```bash
python -m unittest discover -p 'tests_*.py' -v
```

Les tests couvrent le chargement du corpus, la récupération, la validation et une réponse API simulée; aucun appel payant à Anthropic n’est effectué.
