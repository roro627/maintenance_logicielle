# Documentation technique

## Architecture
- `borne_arcade/`: menu principal, scripts de lancement, jeux.
- `borne_arcade/projet/<jeu>/`: code, `description.txt`, `bouton.txt`, `highscore`.
- `MG2D/`: bibliotheque graphique (lecture seule).
- `scripts/`: installation, deploiement, docs, lint, tests.

## Principes
- DRY: fonctions shell mutualisees dans `scripts/lib/outils_communs.sh`.
- KISS: scripts explicites et idempotents.
- Configuration centralisee: `borne_arcade/config/borne.env`.
- Pas de nombres magiques dans le nouveau code.

## Integrite MG2D
Aucun fichier sous `MG2D/MG2D` et `MG2D/doc_MG2D` ne doit etre modifie par les scripts de maintenance.
