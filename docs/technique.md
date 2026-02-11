# Documentation technique

## Architecture
- `borne_arcade/`: menu principal, scripts de lancement, jeux.
- `borne_arcade/projet/<jeu>/`: code, `description.txt`, `bouton.txt`, `highscore`.
- `MG2D/`: bibliotheque graphique (lecture seule).
- `scripts/`: installation, deploiement, docs, lint, tests.
- `.github/workflows/`: pipeline CI qualite.
- `config/`: versions minimales et regles statiques.
- `archives/`: anciennes versions centralisees.
- `build/`: artefacts de compilation Java.
- `.cache/`: cache technique (ex: classes MG2D fallback).
- `logs/`: journaux pipeline post-pull.

## Principes
- DRY: fonctions shell mutualisees dans `scripts/lib/outils_communs.sh`.
- KISS: scripts explicites et idempotents.
- Configuration centralisee: `borne_arcade/config/borne.env` (`JEU_REFERENCE_TEST`, resolution, clavier, etc.).
- Versions minimales centralisees: `config/versions_minimales.env`.
- Perimetre lint Python centralise: `config/pylint_repertoires.txt`.
- Pas de nombres magiques dans le nouveau code.
- Pipeline post-pull verrouille (fichier `.post_pull.lock`) pour eviter les executions concurrentes.
- Journalisation technique centralisee dans `logs/` pour faciliter le diagnostic.
- Verification CI versionnee via `.github/workflows/qualite.yml`.
- Architecture cible documentee dans `ARCHITECTURE.md`.

## Chaine qualite automatisee

1. Installation: `scripts/install/installer_borne.sh`
2. Compilation globale: `borne_arcade/compilation.sh`
3. Lint: `scripts/lint/lancer_lint.sh`
4. Tests: `scripts/tests/lancer_suite.sh`
5. Documentation: `scripts/docs/generer_documentation.sh`
6. Deploiement post-pull: `scripts/deploiement/post_pull_update.sh`

## Isolation des artefacts

- Les classes Java compilees sont stockees dans `build/classes/`.
- Les classes MG2D fallback restent dans `.cache/mg2d_classes/`.
- Les dossiers sources ne doivent plus contenir de `.class` actifs.
- Le test `scripts/tests/test_architecture.sh` controle ces regles.

## Integrite MG2D
Le dossier `MG2D/` est un miroir de `https://github.com/synave/MG2D`.
Aucun fichier sous `MG2D/` ne doit etre modifie par les scripts de maintenance.
