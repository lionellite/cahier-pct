# Cahier PCT

Assistant numérique pour les enseignants de **Physique-Chimie-Technologie (PCT)** du Bénin.
Il répond aux questions, génère des fiches de préparation et des exercices **uniquement à
partir du programme officiel certifié**, en citant systématiquement la compétence, la
capacité ou la section concernée.

> État : socle technique en construction. Le corpus officiel n'est pas encore intégré.
> Les extraits présents dans `corpus/processed/pct-3e/` sont des **exemples de
> démonstration** destinés à faire tourner la chaîne de bout en bout.

## Sommaire

- [Ce que fait le produit](#ce-que-fait-le-produit)
- [Stack](#stack)
- [Structure du dépôt](#structure-du-dépôt)
- [Démarrage rapide](#démarrage-rapide)
- [Configuration](#configuration)
- [Base de connaissances](#base-de-connaissances)
- [Commandes utiles](#commandes-utiles)
- [Tests](#tests)
- [Documentation](#documentation)

## Ce que fait le produit

Trois modes, décrits dans le dossier de candidature NEXT IMPACT :

| Mode | Entrée | Sortie |
| --- | --- | --- |
| **Question** | Une question libre sur le programme | Une réponse sourcée, avec la compétence / capacité / section citée |
| **Fiche de cours** | Une compétence ou une capacité | Une fiche de préparation alignée sur les compétences et critères officiels |
| **Exercices** | Une compétence | Des exercices ou une évaluation avec grille de correction |

Principes non négociables :

1. **Fidélité** — aucune réponse hors programme non signalée.
2. **Traçabilité** — chaque affirmation renvoie à un extrait identifiable.
3. **Sobriété** — application web mobile, légère, pensée pour un usage à faible bande passante.

## Stack

- **Backend** : Python 3.12+, Flask 3, Pydantic 2, Anthropic SDK.
- **Frontend** : React 19, TypeScript, Vite 7, React Router, `react-markdown`.
- **Corpus** : fichiers JSON versionnés, un extrait = un fichier, manifeste de niveau.
- **Récupération** : BM25 implémenté en Python pur (aucun service externe, fonctionne hors ligne).
- **LLM** : API Anthropic, appelée **côté serveur uniquement**. Un mode `mock` permet de
  développement sans clé API.

## Structure du dépôt

```text
cahier-pct/
├─ backend/                  # API Flask
│  ├─ app/
│  │  ├─ api/                # routes HTTP (blueprint /api)
│  │  ├─ services/           # corpus, retrieval BM25, LLM, générateurs
│  │  ├─ prompts/            # consignes système et gabarits par mode
│  │  └─ schemas.py          # contrats d'entrée Pydantic
│  ├─ scripts/corpus.py      # extraction PDF, découpage, validation
│  └─ tests/
├─ frontend/                 # application React / Vite
│  └─ src/
│     ├─ pages/              # Accueil, Question, Fiche, Exercices, Corpus
│     ├─ components/
│     └─ lib/                # client API typé
├─ corpus/
│  ├─ raw/                   # documents bruts (PDF, DOCX…) — non versionnés
│  └─ processed/
│     └─ pct-3e/             # extraits structurés + manifeste + index
└─ docs/                     # architecture, corpus, API, feuille de route
```

## Démarrage rapide

Prérequis : Python 3.12+, Node 20.19+ (ou 22.12+), npm.

### 1. Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item ..\.env.example ..\.env      # puis renseigner la clé API (facultatif)
python run.py
```

L'API écoute sur `http://127.0.0.1:5000`. Sans clé API, elle démarre en **mode
démonstration** (`mock`) : la chaîne corpus → récupération → réponse fonctionne, mais
les réponses sont des extraits bruts clairement étiquetés.

### 2. Frontend

```powershell
cd frontend
npm install
npm run dev
```

L'interface est disponible sur `http://localhost:5173`. Vite proxifie `/api` vers le
backend.

### 3. Vérifier

- `GET http://127.0.0.1:5000/api/health`
- `GET http://127.0.0.1:5000/api/meta` — état du corpus et mode LLM
- Ouvrir `http://localhost:5173`

## Configuration

Toute la configuration vit dans un `.env` unique à la racine (chargé par le backend et
par Vite via `envDir`).

| Variable | Défaut | Rôle |
| --- | --- | --- |
| `ANTHROPIC_API_KEY` | vide | Clé API Anthropic. Vide ⇒ mode `mock`. |
| `ANTHROPIC_MODEL` | `claude-sonnet-4-6` | Modèle utilisé pour la génération. |
| `LLM_MODE` | `auto` | `auto` (live si clé présente), `live`, ou `mock`. |
| `CORPUS_PATH` | `corpus/processed/pct-3e` | Dossier du corpus actif. |
| `CORS_ORIGINS` | `http://localhost:5173` | Origines autorisées, séparées par des virgules. |
| `PORT` | `5000` | Port du serveur Flask. |
| `VITE_API_BASE` | `/api` | Base d'URL utilisée par le frontend. |

## Base de connaissances

Les documents fournis (programme officiel, manuels, anciens supports) se déposent dans
`corpus/raw/`. La chaîne est :

1. **Extraction** — PDF → texte à plat, avec repères de page.
2. **Découpage** — le texte est découpé par section via un fichier de repères
   (`headings.json`).
3. **Validation** — chaque extrait est relu et passé au statut `validated`.
4. **Indexation** — chargé automatiquement par l'API au démarrage.

Voir [docs/02-corpus.md](docs/02-corpus.md) pour le schéma exact et la procédure.

> Les fichiers de `corpus/raw/` ne sont pas versionnés (droits d'auteur, taille). Le
> corpus traité et validé, lui, est versionné.

## Commandes utiles

```powershell
# Backend
cd backend
python run.py                              # serveur de développement
pytest -q                                  # tests
python scripts/corpus.py validate          # valider le corpus actif
python scripts/corpus.py extract <pdf>     # PDF -> texte
python scripts/corpus.py build <config>    # texte -> extraits JSON

# Frontend
cd frontend
npm run dev                                # serveur de développement
npm run build                              # build de production
npm run typecheck                          # vérification TypeScript
```

## Tests

```powershell
cd backend
pytest -q
```

Les tests s'exécutent en mode `mock` : ils ne consomment aucun crédit API.

## Dépannage

### `npm install` échoue avec `EBUSY` sur `esbuild.exe` (Windows)

Un antivirus ou un processus Node peut verrouiller le binaire. Fermer les processus
Node, supprimer `node_modules`, puis relancer :

```powershell
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
Remove-Item -Recurse -Force node_modules
npm install
```

### Le backend répond mais le frontend affiche « Impossible de joindre le serveur »

Vérifier que Flask tourne sur le port 5000 et que Vite proxifie bien `/api`
(`frontend/vite.config.ts`). En production, servir le build via Flask.

## Documentation

- [Architecture](docs/01-architecture.md)
- [Base de connaissances](docs/02-corpus.md)
- [Contrat d'API](docs/03-api.md)
- [Feuille de route technique](docs/04-roadmap.md)
