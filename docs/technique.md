# Documentation technique

## Objectif

Documenter les principes techniques du projet: architecture, automatisation,
qualite, configuration et contraintes MG2D.

## Architecture technique

- `borne_arcade/`: menu principal, jeux, scripts de lancement.
- `borne_arcade/projet/MaintenanceMode/`: interface maintenance cache (pygame).
- `scripts/`: installation, deploiement, lint, tests, docs.
- `config/`: versions minimales et regles qualite.
- `build/`: classes Java compilees.
- `.cache/`: cache technique (MG2D fallback).
- `logs/`: traces d execution.

## Principes d implementation

- DRY: mutualisation dans `scripts/lib/outils_communs.sh`.
- KISS: scripts explicites, idempotents, orientes exploitation.
- Configuration centralisee dans `borne_arcade/config/borne.env`.
- Mode maintenance cache configure via `borne_arcade/config/maintenance_mode.properties`.
- Installation systeme idempotente: verification paquet par paquet puis installation des dependances manquantes.
- Privileges systeme obligatoires au bootstrap (`sudo`/root), avec echec explicite et action recommandee si indisponibles.
- Protection permissions build: message clair si `build/` n est pas accessible en ecriture.
- Menu optimise: suppression des chargements repetes police/son en boucle.
- PianoTile robuste: fallback sans `librosa` si la dependance n est pas disponible.
- CI/CD et tests automatisees via `.github/workflows/qualite.yml` et `scripts/tests/lancer_suite.sh`.

## Chaine d automatisation

1. `bootstrap_borne.sh`
2. `scripts/install/installer_borne.sh`
3. `borne_arcade/compilation.sh`
4. `scripts/lint/lancer_lint.sh`
5. `scripts/tests/test_smoke.sh`
6. `scripts/tests/lancer_suite.sh`
7. validation CI locale `act` (job `verification`)
8. `scripts/docs/generer_documentation.sh`
9. `scripts/deploiement/post_pull_update.sh`

## Contraintes MG2D

Le dossier `MG2D/` est un miroir canonique de `https://github.com/synave/MG2D`.
Aucune modification locale n est autorisee dans `MG2D/`.

## Validation

```bash
./scripts/tests/test_integrite_mg2d.sh
./scripts/tests/test_architecture.sh
./scripts/tests/lancer_suite.sh
```

## Liens associes

- Architecture: `architecture.md`
- Installation: `installation.md`
- Tests: `tests.md`
