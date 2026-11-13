# Corpus Cahier PCT

Ce dossier contient la base de connaissances du produit.

```text
corpus/
├─ raw/                       # documents bruts fournis (non versionnés)
└─ processed/
   └─ pct-3e/                 # corpus actif, versionné
      ├─ manifest.json        # inventaire du niveau
      ├─ headings.example.json# modèle de découpage
      └─ extraits/            # un fichier JSON par extrait
```

## Déposer les documents

Placez ici, dans `raw/`, **tous** les documents sources :

- programme officiel PCT de la 3ᵉ (version certifiée, PDF) ;
- manuels scolaires numériques ;
- anciens supports, fiches, évaluations ;
- éventuel ancien prototype (code ou documents).

Les PDF de `raw/` ne sont pas versionnés par Git (taille et droits d'auteur).

## Construire le corpus

La procédure complète est décrite dans
[docs/02-corpus.md](../docs/02-corpus.md) :

```powershell
cd backend
python scripts/corpus.py extract ../corpus/raw/programme-pct-3e.pdf --out ../corpus/raw/programme-pct-3e.txt
python scripts/corpus.py build ../corpus/raw/programme-pct-3e.txt --config ../corpus/processed/pct-3e/headings.json
python scripts/corpus.py validate
```

## Statut actuel

Le corpus livré ici est un **jeu de démonstration** : trois extraits étiquetés
`status: "demo"`, destinés à valider la chaîne technique. Ils ne contiennent aucun
texte officiel et doivent être remplacés dès réception des documents.
