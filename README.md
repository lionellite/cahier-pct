# Cahier PCT — version autonome

Application web pour aider les enseignants de PCT (3ème, Bénin) à préparer des cours,
fiches et exercices à partir du programme officiel certifié 2020.

## Structure

```
server_app/
  app.py              -> serveur Flask (garde la clé API en sécurité)
  templates/index.html -> l'interface (déjà générée, contient le programme officiel)
  requirements.txt
  .env.example
```

## 1. Installer et lancer en local (sur ton PC)

```bash
cd server_app
python3 -m venv venv
source venv/bin/activate      # sur Windows : venv\Scripts\activate
pip install -r requirements.txt

# Copie .env.example en .env et colle ta vraie clé API dedans
cp .env.example .env
# puis édite .env avec ta clé

# Charge la variable d'environnement et lance le serveur
export $(cat .env | xargs)    # sur Windows, utilise plutôt : set ANTHROPIC_API_KEY=...
python3 app.py
```

Ouvre ensuite `http://localhost:5000` dans ton navigateur — l'app doit fonctionner
complètement, y compris les 3 modes (Question / Fiche / Exercices).

**Ne mets jamais ta vraie clé API dans un fichier que tu partages ou publies sur GitHub.**
Le fichier `.env` doit rester uniquement sur ta machine ou dans les "variables
d'environnement" secrètes de ton hébergeur (voir plus bas).

## 2. Déployer gratuitement pour que d'autres enseignants puissent l'utiliser

Plusieurs hébergeurs ont un plan gratuit suffisant pour ce prototype :

- **Render.com** (recommandé pour débuter) : crée un compte, "New Web Service",
  connecte ton dépôt GitHub, indique `gunicorn app:app` comme commande de démarrage,
  et ajoute `ANTHROPIC_API_KEY` dans la section "Environment" — jamais dans le code.
- **Railway.app** : fonctionnement similaire.
- **PythonAnywhere** : plan gratuit, bon si Render ne convient pas.

Dans tous les cas, la clé API se configure comme **variable d'environnement secrète**
sur la plateforme d'hébergement — jamais écrite en dur dans `app.py` ou `index.html`.

## 3. Ce qui reste à surveiller

- **Coût** : chaque question envoyée à Claude a un coût (facturation à l'usage sur
  console.anthropic.com). Pour un usage par quelques enseignants en test, ça reste
  minime, mais à surveiller si l'usage grandit.
- **Limite de réponse** : les réponses sont actuellement limitées à 1500 tokens
  (~1000-1200 mots) — suffisant pour une fiche standard, à ajuster dans `app.py`
  (`max_tokens`) si besoin de réponses plus longues.
- **Un seul niveau couvert** : seul le programme PCT 3ème est chargé pour l'instant.
