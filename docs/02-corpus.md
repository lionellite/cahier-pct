# Base de connaissances

## Principe

Le corpus est la source de vérité. Aucune réponse ne doit être produite sans un extrait
identifiable. Le corpus est donc traité comme un livrable documentaire : versionné,
relu, validé, référencé.

## Arborescence

```text
corpus/
├─ raw/                          # documents fournis, non versionnés
│  ├─ programme-pct-3e.pdf
│  ├─ manuels/
│  └─ ancien-projet/
└─ processed/
   └─ pct-3e/
      ├─ manifest.json           # inventaire du niveau
      ├─ headings.json           # règles de découpage (à créer)
      └─ extraits/
         ├─ 01-....json
         └─ 02-....json
```

## Manifeste

`manifest.json` décrit le niveau et liste les extraits.

```json
{
  "id": "pct-3e",
  "level": "3e",
  "discipline": "PCT",
  "program": {
    "title": "Programme officiel de Physique-Chimie-Technologie — classe de 3e",
    "edition": "2020",
    "pages": 118,
    "source": "corpus/raw/programme-pct-3e.pdf"
  },
  "expected_extracts": 32,
  "status": "incomplete",
  "extracts": [
    {
      "id": "3e-orientations-generales",
      "title": "Orientations générales",
      "type": "orientations-generales",
      "file": "extraits/01-orientations-generales.json",
      "status": "validated"
    }
  ]
}
```

Champs utiles :

- `expected_extracts` : cible de couverture (32 pour la 3ᵉ), affichée dans l'interface.
- `status` : `incomplete`, `complete`, `deprecated`.
- Chaque entrée doit référencer un fichier existant.

## Extrait

Un fichier = un extrait.

```json
{
  "id": "3e-competence-disciplinaire-masse-volumique",
  "level": "3e",
  "type": "competence-disciplinaire",
  "title": "Compétence disciplinaire — masse et volume",
  "status": "validated",
  "version": 1,
  "source": {
    "document": "Programme officiel PCT 3e",
    "edition": "2020",
    "pages": [41, 43],
    "url": null
  },
  "metadata": {
    "tags": ["masse", "volume", "masse volumique"],
    "competences": ["…"],
    "capacites": ["…"],
    "criteres": ["…"]
  },
  "content": "Texte intégral de la section, à plat, sans mise en page."
}
```

### Types autorisés

| `type` | Contenu |
| --- | --- |
| `orientations-generales` | Finalités, démarche pédagogique. |
| `competence-transversale` | Compétences transversales. |
| `competence-transdisciplinaire` | Compétences transdisciplinaires. |
| `competence-disciplinaire` | Compétences et capacités de la discipline. |
| `situation-apprentissage` | Situations d'apprentissage. |
| `critere-evaluation` | Critères et indicateurs, si isolés. |
| `section` | Section générique, en attendant un classement plus fin. |

### Statuts

| Statut | Signification |
| --- | --- |
| `demo` | Extrait factice, sans valeur officielle. À supprimer ou remplacer. |
| `draft` | Extrait extrait automatiquement, non relu. |
| `validated` | Relu par un enseignant ou un responsable du corpus. |
| `deprecated` | Conservé pour historique, ne doit plus être cité. |

Règle : **aucun extrait `demo` ou `draft` ne doit partir en production**. L'API les
sert quand même en développement, mais l'interface les marque explicitement.

## Chaîne de production

### 1. Extraire le texte

```powershell
cd backend
python scripts/corpus.py extract ../corpus/raw/programme-pct-3e.pdf
```

Produit un `.txt` avec des repères `[[PAGE n]]`. L'extraction PDF est volontairement
« à plat » : les tableaux multi-pages sont mal reconstruits par les extracteurs de
tableaux, et le programme en contient.

### 2. Découper

Créer `corpus/processed/pct-3e/headings.json` à partir de
`headings.example.json`, puis :

```powershell
python scripts/corpus.py build ../corpus/raw/programme-pct-3e.pdf `
  --config ../corpus/processed/pct-3e/headings.json
```

Chaque section définie devient un fichier dans `extraits/`, avec ses pages calculées
automatiquement.

Format d'une section :

```json
{
  "id": "3e-competence-disciplinaire-masse-volumique",
  "title": "Masse et volume",
  "type": "competence-disciplinaire",
  "start": "MASSE\\s+ET\\s+VOLUME",
  "tags": ["masse", "volume", "masse volumique"]
}
```

`start` est une expression régulière, insensible à la casse. Le texte de la section va
du motif trouvé jusqu'au motif suivant.

### 3. Relire et enrichir

Pour chaque extrait :

1. vérifier le texte et les pages ;
2. renseigner `metadata.competences`, `capacites`, `criteres` ;
3. corriger le `title` et les `tags` (ils pèsent dans la recherche) ;
4. passer `status` à `validated` et incrémenter `version`.

### 4. Valider

```powershell
python scripts/corpus.py validate
python scripts/corpus.py stats
```

La validation vérifie les champs obligatoires, les identifiants uniques, les contenus
vides et les statuts inconnus.

### 5. Recharger

L'API met le corpus en cache. Après une modification, redémarrer Flask en
développement, ou vider le cache via un redémarrage du process.

## Ajouter un autre niveau

Créer `corpus/processed/pct-4e/` avec son manifeste, puis pointer
`CORPUS_PATH=corpus/processed/pct-4e`. À terme, l'API exposera un paramètre `level` et
chargera plusieurs corpus ; le contrat actuel ne gère qu'un corpus actif à la fois.

## Droits et données

- Les PDF de `raw/` ne sont pas versionnés (taille, droits).
- Les manuels scolaires ne peuvent être intégrés qu'avec l'autorisation des éditeurs.
  Cette vérification est un préalable, pas une étape optionnelle.
- Ne jamais inclure de données personnelles d'élèves ou d'enseignants dans le corpus.

## État actuel

Trois extraits de démonstration sont livrés pour faire fonctionner la chaîne. Ils sont
marqués `demo`, ne contiennent aucun texte officiel et doivent être remplacés par les
32 extraits validés du programme de 3ᵉ dès réception des documents.
