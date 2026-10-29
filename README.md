# Cahier PCT — atelier pédagogique RAG

Assistant web responsive destiné aux enseignants de PCT de 3e au Bénin. Il propose trois outils : question libre sur le programme, fiche de cours et exercices avec correction. Le serveur recherche les passages pertinents dans les 32 extraits du programme officiel certifié 2020 et renvoie les références utilisées.

## Test gratuit avec Gemini

Le fournisseur par défaut est **Gemini 3.8 Flash**, accessible depuis Google AI Studio avec un quota gratuit pour les projets éligibles. La clé API doit rester dans l’environnement serveur; elle n’est jamais envoyée au navigateur et ne doit jamais être committée. La disponibilité et les plafonds exacts dépendent du projet et sont visibles dans AI Studio.

1. Connectez-vous à [Google AI Studio](https://aistudio.google.com/apikey) et créez une clé API.
2. Dans le dépôt, créez votre fichier local `.env` à partir de `.env.example`, puis renseignez `GEMINI_API_KEY`.
3. Chargez ces variables dans le terminal ou dans la configuration secrète de l’hébergeur, puis redémarrez le serveur.

Installation et lancement local :

```bash
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
# Éditer .env et ajouter GEMINI_API_KEY, puis charger la variable dans le shell
set -a && . ./.env && set +a
python app.py
```

Ouvrez http://localhost:5000. En déploiement WSGI, utilisez `gunicorn app:app` et configurez `GEMINI_API_KEY` dans les secrets de l’hébergeur, pas dans un fichier versionné. Le modèle est modifiable avec `GEMINI_MODEL`. Si aucune clé Gemini n’est fournie, l’application accepte encore `ANTHROPIC_API_KEY` en solution de repli, mais Anthropic est payant à l’usage.

### Données et confidentialité

Le quota gratuit de Gemini peut permettre à Google d’utiliser les entrées et réponses pour améliorer ses produits, et des évaluateurs humains peuvent les examiner. N’envoyez pas de renseignements personnels, sensibles ou confidentiels. La clé API est transmise uniquement du serveur à Google via HTTPS. Une réponse générée reste à vérifier avant utilisation pédagogique.

## Fonctionnalités de l’interface

- Interface mobile et ordinateur, avec modes Question, Fiche de cours et Exercices.
- Suggestions de prompts, compte de caractères, options de durée, de nombre et de type d’exercices.
- Indicateur de configuration du service, affichage des sources, copie et impression de réponse.
- Endpoint `GET /api/health` sans divulgation de clé; `POST /api/generate` reçoit le mode, la demande et les options.

## Tests

```bash
python -m unittest discover -p 'tests_*.py' -v
```

La suite simule les fournisseurs pour vérifier le format et les réponses API sans clé et sans appel externe payant.
