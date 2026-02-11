# Deploiement automatique

## Objectif

Apres `git pull`, executer automatiquement l installation/mise a jour,
la compilation, le lint, les tests et la regeneration documentation.

## Procedure

### Activation

```bash
./bootstrap_borne.sh
git config core.hooksPath .githooks
chmod +x .githooks/post-merge scripts/deploiement/post_pull_update.sh
```

### Execution manuelle

```bash
./scripts/deploiement/post_pull_update.sh
```

Mecanismes utilises:
- hook versionne `.githooks/post-merge`,
- pipeline local `scripts/deploiement/post_pull_update.sh`,
- verrou anti-concurrence `.post_pull.lock`,
- journaux `logs/post_pull_update_YYYYMMDD_HHMMSS.log`.

## Validation

```bash
./scripts/tests/test_deploiement.sh
```

## Depannage

- Consulter le dernier journal dans `logs/post_pull_update_*.log`.
- Verifier qu aucun verrou stale n est present (`.post_pull.lock`).
- Relancer `./scripts/deploiement/post_pull_update.sh`.

## Liens associes

- Installation: `installation.md`
- Tests: `tests.md`
- Technique: `technique.md`
