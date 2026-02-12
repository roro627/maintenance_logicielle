# Strategie de tests

## Objectif

Garantir la qualite et limiter les regressions sur installation, execution des jeux,
deploiement, documentation et conformite projet.

## Procedure

### Suite complete

```bash
TEST_INSTALLATION_SIMULATION=1 TEST_DEPLOIEMENT_SIMULATION=1 BORNE_MODE_TEST=1 ./scripts/tests/lancer_suite.sh
```

### Smoke tests rapides

```bash
./scripts/tests/test_smoke.sh
```

### Validation CI/CD equivalente GitHub Actions

```bash
~/.local/bin/act -W .github/workflows/qualite.yml -j verification --container-architecture linux/amd64 -P ubuntu-latest=catthehacker/ubuntu:act-latest
```

### Validation CI/CD reelle Debian 11 (sans variables de test)

```bash
~/.local/bin/act -W .github/workflows/verification_reelle.yml -j verification_reelle_debian11 --container-architecture linux/amd64 -P ubuntu-latest=catthehacker/ubuntu:act-latest
```

## Couverture

### Unitaires
- HighScore (lecture/ecriture),
- mapping clavier borne,
- parsing configuration,
- logique NeonSumo (collisions, sortie arene, cooldowns, ultime),
- configuration menu NeonSumo + logique d etats attract (`borne_arcade/projet/NeonSumo/tests/test_main_menu.py`),
- mode maintenance Python (`borne_arcade/projet/MaintenanceMode/tests/test_operations.py`):
  streaming logs temps reel, timeout actionnable, journalisation des erreurs,
  fallback de dossier logs, operation `reset_pre_requis`, operation `git_retour_precedent`,
  robustesse diagnostic en absence de pre-requis, gestion de l absence de `git` et capture des exceptions inattendues.
- logique d interface maintenance (`borne_arcade/projet/MaintenanceMode/tests/test_interface.py`):
  defilement vertical/horizontal du journal, auto-scroll, bornage de l historique et extraction de segment horizontal.
- PianoTile (`borne_arcade/projet/PianoTile/tests/test_piano.py`):
  echec audio non bloquant et chronometrage de secours sans mixer actif.

### Integration et systeme
- catalogue jeux,
- compilation Java + verifications syntaxiques Python/Lua,
- ajout de jeu,
- deploiement post-pull,
- deploiement post-pull + verification permissions partagees (`logs/`, `build/`, `.cache/`, `.venv/`, scripts critiques),
- generation documentation,
- architecture et couts,
- mode maintenance cache (presence, verrouillage, integration menu),
- mode maintenance cache (presence, verrouillage, integration menu, operation reset prerequis),
- bootstrap robuste apres `sudo` (absence de regression sur normalisation permissions et execution non-systeme sous utilisateur appelant),
- robustesse PianoTile en absence de `librosa`,
- validation materielle (checklist).

### Qualite outillage
- shellcheck,
- checkstyle,
- pylint,
- docstrings,
- messages d erreur actionnables.

## Validation

Scripts principaux:
- `scripts/tests/test_installation.sh`
- `scripts/tests/test_smoke.sh`
- `scripts/tests/test_jeux.sh`
- `scripts/tests/test_deploiement.sh`
- `scripts/tests/test_documentation.sh`
- `scripts/tests/test_integrite_mg2d.sh`
- `scripts/tests/test_architecture.sh`
- `scripts/tests/test_couts.sh`
- `scripts/tests/test_anti_regressions.sh`
- `.github/workflows/verification_reelle.yml`

## Depannage

- En cas d echec, relancer le script de test en erreur seul.
- Consulter `logs/` pour les pipelines post-pull/bootstrap.
- Corriger la cause puis relancer `./scripts/tests/lancer_suite.sh`.
- En cas d echec CI locale, corriger puis relancer `act` jusqu a statut vert.

## Liens associes

- Installation: `installation.md`
- Deploiement: `deploiement.md`
- Technique: `technique.md`
