# Contrat d'API

Base : `http://127.0.0.1:5000/api` en développement (Vite proxifie `/api`).
Toutes les réponses sont en JSON, encodées en UTF-8.

## Erreurs

```json
{
  "error": {
    "code": "validation_error",
    "message": "Les données envoyées sont invalides.",
    "details": {
      "errors": [
        {
          "type": "string_too_short",
          "loc": ["question"],
          "msg": "String should have at least 3 characters"
        }
      ]
    }
  }
}
```

| Code | HTTP | Cause |
| --- | --- | --- |
| `invalid_body` | 400 | Corps JSON absent. |
| `validation_error` | 422 | Champ manquant, trop long ou hors bornes. |
| `no_match` | 404 | Aucun extrait ne correspond à la compétence. |
| `extract_not_found` | 404 | Identifiant d'extrait inconnu. |
| `llm_error` | 502 | Échec de l'appel au service d'IA. |
| `corpus_error` | 500 | Corpus absent, illisible ou invalide. |
| `internal_error` | 500 | Erreur inattendue. |

## `GET /health`

```json
{ "status": "ok", "service": "Cahier PCT", "version": "0.1.0" }
```

## `GET /meta`

État du corpus et du service de génération. Utilisé par le frontend pour afficher le
badge « IA active » ou « Mode démo ».

```json
{
  "name": "Cahier PCT",
  "version": "0.1.0",
  "llm": { "mode": "mock", "model": "claude-sonnet-4-6", "live": false },
  "corpus": {
    "id": "pct-3e",
    "level": "3e",
    "discipline": "PCT",
    "extract_count": 3,
    "expected_extracts": 32,
    "completion": 0.094,
    "characters": 1834,
    "by_type": { "competence-disciplinaire": 1, "orientations-generales": 1 },
    "by_status": { "demo": 3 },
    "validated": 0
  }
}
```

## `GET /corpus`

Paramètres facultatifs : `type`, `status`.

```json
{
  "corpus": { "...": "voir /meta" },
  "extracts": [
    {
      "id": "3e-competence-disciplinaire-masse-volumique-demo",
      "title": "Compétence disciplinaire — masse et volume (démonstration)",
      "type": "competence-disciplinaire",
      "level": "3e",
      "status": "demo",
      "pages": [41, 43],
      "reference": "Programme officiel PCT 3e (démonstration), p. 41-43",
      "tags": ["masse", "volume", "masse volumique"]
    }
  ]
}
```

Les extraits listés ne contiennent **pas** leur texte complet.

## `GET /corpus/{extract_id}`

```json
{
  "extract": {
    "id": "…",
    "title": "…",
    "type": "…",
    "level": "3e",
    "status": "demo",
    "pages": [41, 43],
    "reference": "…",
    "content": "Texte intégral…",
    "source": { "document": "…", "edition": "2020", "pages": [41, 43], "url": null },
    "metadata": { "tags": [], "competences": [], "capacites": [], "criteres": [] },
    "version": 1
  }
}
```

## `POST /question`

Requête :

```json
{
  "question": "Comment calculer la masse volumique d'un corps ?",
  "level": "3e",
  "top_k": 5
}
```

| Champ | Type | Contraintes |
| --- | --- | --- |
| `question` | string | 3 à 2000 caractères |
| `level` | string | facultatif, 40 caractères max |
| `top_k` | int | 1 à 10, défaut 5 |

Réponse :

```json
{
  "mode": "question",
  "content": "Markdown de la réponse…",
  "citations": [
    {
      "extract_id": "3e-competence-disciplinaire-masse-volumique-demo",
      "title": "Compétence disciplinaire — masse et volume (démonstration)",
      "type": "competence-disciplinaire",
      "reference": "Programme officiel PCT 3e (démonstration), p. 41-43",
      "pages": [41, 43],
      "status": "demo"
    }
  ],
  "retrieved": [
    {
      "extract_id": "3e-competence-disciplinaire-masse-volumique-demo",
      "title": "…",
      "type": "competence-disciplinaire",
      "score": 8.4213,
      "status": "demo"
    }
  ],
  "model": "claude-sonnet-4-6",
  "llm_mode": "mock",
  "usage": {}
}
```

Si aucun extrait n'est trouvé, `citations` et `retrieved` sont vides et `content`
explique que le programme fourni ne contient pas l'information. Le statut HTTP reste
200 : c'est une réponse produit, pas une erreur technique.

## `POST /fiche`

Requête :

```json
{
  "competence": "masse volumique",
  "level": "3e",
  "duration": "2 h",
  "class_size": "60 élèves",
  "context": "matériel expérimental limité"
}
```

`competence` accepte un identifiant d'extrait ou une recherche libre.
Réponse : même structure que `/question`, avec `mode: "fiche"`.
Si aucun extrait ne correspond : `404 no_match`.

## `POST /exercices`

Requête :

```json
{
  "competence": "masse volumique",
  "level": "3e",
  "count": 5,
  "with_correction": true,
  "difficulty": "progressive",
  "context": "évaluation de fin de trimestre"
}
```

| Champ | Type | Contraintes |
| --- | --- | --- |
| `count` | int | 1 à 10, défaut 5 |
| `with_correction` | bool | défaut `true` |
| `difficulty` | string | facultatif |

Réponse : même structure, avec `mode: "exercices"`.

## Notes d'intégration

- Toujours envoyer `Content-Type: application/json`.
- Les champs `level` sont facultatifs : le niveau du corpus actif sert de valeur par
  défaut.
- Le frontend ne doit jamais recevoir la clé API : aucun endpoint ne l'expose.
- Les citations sont la garantie de traçabilité : les afficher systématiquement, même
  en mode démonstration.
