# Documentation technique

## Architecture
- `borne_arcade/`: menu principal, scripts de lancement, jeux.
- `borne_arcade/projet/<jeu>/`: code, `description.txt`, `bouton.txt`, `highscore`.
- `MG2D/`: bibliotheque graphique (lecture seule).
- `scripts/`: installation, deploiement, docs, lint, tests.

## Principes
- DRY: fonctions shell mutualisees dans `scripts/lib/outils_communs.sh`.
- KISS: scripts explicites et idempotents.
- Configuration centralisee: `borne_arcade/config/borne.env` (`JEU_REFERENCE_TEST`, resolution, clavier, etc.).
- Versions minimales centralisees: `config/versions_minimales.env`.
- Perimetre lint Python centralise: `config/pylint_repertoires.txt`.
- Pas de nombres magiques dans le nouveau code.

## Integrite MG2D
Le dossier `MG2D/` est un miroir de `https://github.com/synave/MG2D`.
Aucun fichier sous `MG2D/` ne doit etre modifie par les scripts de maintenance.
