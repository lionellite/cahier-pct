# Feuille de route technique

La feuille de route du dossier de candidature est organisée en trois phases sur six
mois, avec deux jalons de validation. Ce document la traduit en travail technique.

Principe : **on n'étend le contenu qu'après validation du pilote, et on ne lance
l'offre payante qu'après validation du corpus étendu.**

## Phase 0 — Socle (fait)

- [x] Monorepo backend Flask + frontend React/Vite.
- [x] Trois modes exposés par l'API et l'interface.
- [x] Corpus JSON versionné, manifeste, statistiques, statut de validation.
- [x] Recherche BM25 française, sans dépendance externe.
- [x] Consignes système et gabarits par mode.
- [x] Mode démonstration sans clé API.
- [x] Outil d'extraction, de découpage et de validation du corpus.
- [x] Documentation architecture, corpus, API.
- [ ] Corpus officiel de 3ᵉ intégré et validé (dépend des documents).
- [ ] Clé API configurée et test en conditions réelles.

## Phase 1 — Pilote (mois 1 à 2)

Objectif : passer d'un prototype local à un service utilisé par de vrais enseignants.

### Technique

- [ ] Intégrer les 32 extraits du programme officiel de 3ᵉ, statut `validated`.
- [ ] Corriger l'extraction de la section « Situations d'apprentissage » (tableaux
  multi-pages), avec validation manuelle.
- [ ] Déployer l'API et le frontend sur un serveur public, HTTPS, nom de domaine.
- [ ] Authentification simple des enseignants (compte + mot de passe ou lien magique).
- [ ] Quotas et limitation de débit par compte.
- [ ] Journalisation des usages sans contenu sensible : nombre de requêtes, mode,
  extraits cités, coût API estimé.
- [ ] Sauvegarde quotidienne du corpus et de la base de comptes.
- [ ] Mesurer le coût API réel par enseignant.

### Terrain

- [ ] Recruter 30 enseignants pilotes.
- [ ] Formation courte (1 h) et guide d'utilisation.
- [ ] Collecte des retours : formulaire intégré ou entretiens hebdomadaires.
- [ ] Questionnaire avant/après sur le temps de préparation.

### Jalon 1 — Validation du pilote

Critères proposés :

- 30 enseignants actifs, au moins une utilisation par semaine ;
- satisfaction ≥ 4/5 ;
- temps de préparation perçu en baisse ;
- aucune réponse non fidèle signalée sans correction possible ;
- coût API par enseignant mesuré et compatible avec un prix acceptable.

Décision : poursuivre, corriger, ou réorienter.

## Phase 2 — Extension (mois 3 à 4)

Objectif : élargir le corpus sans dégrader la fidélité.

### Technique

- [ ] Intégrer les manuels scolaires numériques (après autorisation des éditeurs).
- [ ] Ajouter les autres niveaux (6ᵉ à Terminale) : un dossier de corpus par niveau,
  chargement multi-niveaux dans l'API.
- [ ] Faire évoluer le manifeste pour gérer plusieurs corpus actifs.
- [ ] Interface de sélection du niveau.
- [ ] Validation des nouveaux extraits par des enseignants experts.
- [ ] Améliorer la recherche : synonymes du programme, réordonnancement des résultats,
  éventuellement une couche vectorielle en complément du BM25.
- [ ] Historique local des fiches et exercices générés (stockage navigateur ou compte).

### Jalon 2 — Validation du corpus étendu

Critères proposés :

- corpus de plusieurs niveaux intégré, chaque extrait `validated` ;
- taux de réponses sourcées élevé sur un jeu de questions de référence ;
- revue par des enseignants experts ;
- performance et coût maîtrisés.

## Phase 3 — Lancement commercial (mois 5 à 6)

Objectif : transformer le pilote validé en service payant.

### Technique

- [ ] Abonnement enseignant via Mobile Money (intégration opérateur ou passerelle).
- [ ] Licence établissement / réseau d'écoles (comptes multiples, facturation unique).
- [ ] Tableau de bord d'usage pour l'établissement.
- [ ] Tarification pilotée par le coût réel mesuré en phase 1.
- [ ] Étude du canal WhatsApp : file d'attente, webhook, réponses courtes.
- [ ] Cadre juridique : conditions d'utilisation, politique de confidentialité, droits
  sur les corpus.
- [ ] Supervision : alertes sur erreurs, coûts, disponibilité.

## Backlog priorisé

### P0 — avant toute mise en public

1. Corpus officiel validé.
2. Clé API et test de bout en bout.
3. Déploiement HTTPS + sauvegardes.
4. Authentification et quotas.
5. Journalisation des coûts.

### P1 — pendant le pilote

1. Retours intégrés dans l'interface.
2. Statistiques d'usage.
3. Historique des fiches.
4. Amélioration des consignes à partir des cas réels.
5. Tests de non-régression sur un jeu de questions de référence.

### P2 — après validation

1. Manuels et autres niveaux.
2. Canal WhatsApp.
3. Paiement Mobile Money.
4. Licences établissement.
5. Couche de recherche sémantique.

## Risques et parades

| Risque | Parade |
| --- | --- |
| Coût API si l'usage se généralise | Mesurer par enseignant, plafonner les requêtes, tarifer en conséquence. |
| Réponse erronée ou non fidèle | Consigne restrictive, citation obligatoire, relecture enseignante, corrections issues du pilote. |
| Couverture limitée à la 3ᵉ | Extension progressive, niveau par niveau, avec validation. |
| Extraction imparfaite des situations | Retraitement ciblé et validation manuelle. |
| Faible adoption | Pilote réel, formation courte, interface mobile simple, itérations rapides. |
| Internet limité et coût des données | Build léger, pas de police externe, réponses compactes, WhatsApp étudié à terme. |
| Droits sur les manuels | Autorisation des éditeurs avant toute intégration. |
| Dépendance à un fournisseur d'IA | Le serveur relaie les appels : changement de modèle sans impact sur le frontend. |
