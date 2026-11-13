# Architecture

## Vue d'ensemble

```text
Téléphone / navigateur
        │  HTTPS
        ▼
┌───────────────────────┐
│  Frontend React/Vite  │  3 modes + navigation du corpus
└───────────┬───────────┘
            │ JSON /api/*
            ▼
┌───────────────────────┐
│   API Flask           │  validation, CORS, erreurs, fichiers statiques
│   routes              │
└───────────┬───────────┘
            │
   ┌────────┼─────────────────────┐
   ▼        ▼                     ▼
┌───────┐ ┌──────────────┐  ┌──────────────┐
│Corpus │ │ Récupération │  │  LLM (Claude)│
│JSON   │ │ BM25 français│  │  clé serveur │
└───────┘ └──────────────┘  └──────────────┘
```

Le serveur est le seul à connaître la clé API et le corpus complet. Le navigateur ne
reçoit que la réponse finale, ses citations et les métadonnées publiques des extraits.

## Composants

### Frontend (`frontend/`)

- **React 19 + TypeScript + Vite 7**, React Router.
- Cinq écrans : accueil, question, fiche, exercices, corpus.
- Client API typé (`src/lib/api.ts`) : une seule porte de sortie réseau, erreurs
  normalisées.
- Contexte `meta` : état du corpus et mode LLM, affiché dans l'en-tête.
- Rendu Markdown via `react-markdown` + `remark-gfm`, indispensable pour les fiches et
  les tableaux de barème.
- CSS unique, mobile d'abord, sans framework : le build reste petit et le rendu rapide
  sur un téléphone à faible bande passante.

### API (`backend/app/`)

- **Flask 3**, fabrique d'application (`create_app`) pour faciliter les tests.
- Blueprint unique `/api`, routes minces qui délèguent aux services.
- Validation des entrées par **Pydantic 2** ; les erreurs sont renvoyées dans un format
  unique (`{"error": {"code", "message", "details"}}`).
- Sert le build React en production si `frontend/dist` existe.

### Services

| Module | Rôle |
| --- | --- |
| `services/corpus.py` | Chargement du manifeste et des extraits, cache mémoire, statistiques, résolution d'une compétence. |
| `services/retrieval.py` | BM25 en Python pur, normalisation française (minuscules, accents, ponctuation, mots vides). |
| `services/llm.py` | Appel Anthropic, gestion du mode `live` / `mock`, remontée d'erreurs explicite. |
| `services/generators.py` | Composition des trois modes : récupération → consigne → génération → citations. |
| `prompts.py` + `prompts/*.md` | Consignes système et gabarits par mode, versionnés comme du code. |

### Corpus (`corpus/`)

Le corpus est un ensemble de fichiers JSON versionnés. Un extrait = un fichier, avec
son texte, sa source, ses pages et son statut de validation. Le manifeste décrit le
niveau, le programme et l'inventaire des extraits.

Voir [02-corpus.md](02-corpus.md).

## Flux d'une requête

Exemple : mode Question.

1. `POST /api/question` avec `{ "question": "…" }`.
2. Pydantic valide la requête.
3. `Corpus.search()` tokenise la question et classe les extraits par BM25.
4. Si aucun extrait ne ressort, l'API renvoie une réponse de prudence : « le programme
   fourni ne contient pas cette information ».
5. Sinon, les extraits sont sérialisés dans un bloc `<extraits>` et injectés dans la
   consigne du mode.
6. En mode `live`, le serveur appelle Anthropic avec la consigne système ;
   en mode `mock`, il construit une réponse de démonstration à partir des extraits.
7. La réponse contient le Markdown, la liste des citations et les extraits récupérés
   avec leur score.

## Décisions techniques

| Décision | Raison |
| --- | --- |
| BM25 plutôt que recherche vectorielle | 32 extraits, pas de coût d'embeddings, fonctionnement hors ligne, résultats explicables. Une couche vectorielle pourra s'ajouter sans changer le contrat d'API. |
| Un fichier JSON par extrait | Revue et validation indépendantes, diffs Git lisibles, correction d'un extrait sans toucher au reste. |
| Prompts dans des fichiers Markdown | Les consignes sont un actif produit : elles doivent être relues, versionnées et testées comme du code. |
| Mode `mock` intégré | Développer l'interface et les tests sans clé ni crédit API ; rendre visible l'absence de génération. |
| Clé API uniquement côté serveur | Exigence de sécurité du dossier de candidature. Le navigateur ne voit jamais la clé. |
| React plutôt que HTML vanilla | Le dossier initial prévoyait du HTML/JS simple ; le choix React/Vite a été retenu pour absorber la croissance (comptes, historique, tableau de bord pilote). |

## Sécurité

- Clé API lue depuis `.env`, jamais exposée ni journalisée.
- CORS restreint aux origines configurées.
- Validation stricte des entrées (longueurs, bornes de `top_k`, `count`).
- Aucune donnée personnelle collectée pour l'instant.
- À ajouter avant le pilote public : authentification des enseignants, quotas par
  compte, limitation de débit, journalisation des usages sans contenu sensible,
  sauvegarde du corpus.

## Déploiement

### Développement

Deux process : Flask (`:5000`) et Vite (`:5173`, proxy `/api`).

### Production

```powershell
cd frontend
npm run build

cd ../backend
pip install -r requirements.txt
# Linux : gunicorn -w 2 -b 0.0.0.0:8000 run:app
# Windows : waitress-serve --port=8000 run:app
```

Flask sert alors `frontend/dist` et l'API sur le même domaine. Prévoir un reverse proxy
HTTPS (Caddy, Nginx) et un disque persistant pour le corpus.

## Limites connues

- Pas encore d'authentification ni de comptes.
- Pas de persistance des conversations ou des fiches générées.
- Le mode `mock` ne produit pas de vraie fiche ni de vrais exercices.
- La couverture du corpus dépend entièrement des documents fournis.
- Le BM25 lexical peut manquer des synonymes ; le corpus doit employer les termes du
  programme, ce qui est précisément le cas visé.
