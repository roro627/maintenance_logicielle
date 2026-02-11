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

## Couverture

### Unitaires
- HighScore (lecture/ecriture),
- mapping clavier borne,
- parsing configuration,
- logique NeonSumo (collisions, sortie arene, cooldowns, ultime).

### Integration et systeme
- catalogue jeux,
- compilation Java + verifications syntaxiques Python/Lua,
- ajout de jeu,
- deploiement post-pull,
- generation documentation,
- architecture et couts,
- mode maintenance cache (presence, verrouillage, integration menu),
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

## Depannage

- En cas d echec, relancer le script de test en erreur seul.
- Consulter `logs/` pour les pipelines post-pull/bootstrap.
- Corriger la cause puis relancer `./scripts/tests/lancer_suite.sh`.
- En cas d echec CI locale, corriger puis relancer `act` jusqu a statut vert.

## Liens associes

- Installation: `installation.md`
- Deploiement: `deploiement.md`
- Technique: `technique.md`
