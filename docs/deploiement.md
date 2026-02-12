# Deploiement automatique

## Objectif

Apres `git pull`, executer automatiquement l installation/mise a jour,
la compilation, le lint, les tests et la regeneration documentation.

## Procedure

### Activation

```bash
sudo ./bootstrap_borne.sh
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
- journaux `logs/post_pull_update_YYYYMMDD_HHMMSS.log` (ou fallback automatique
  `~/.cache/maintenance_logicielle/logs/` si `logs/` n est pas accessible).

Le pipeline appelle l installateur en mode optionnel:

```bash
INSTALLATION_SYSTEME_OPTIONNEL=1 ./scripts/install/installer_borne.sh
```

Resultat:
- si les dependances systeme sont deja presentes, le deploiement continue sans root,
- si des dependances manquent, echec clair avec action recommandee (`sudo ./bootstrap_borne.sh`).
- les permissions partagees restent reappliquees (`logs/`, `build/`, `.cache/`, `.venv/`) pour eviter les blocages apres une installation root.

### Validation CI/CD locale (obligatoire en fin de run)

```bash
~/.local/bin/act -W .github/workflows/qualite.yml -j verification --container-architecture linux/amd64 -P ubuntu-latest=catthehacker/ubuntu:act-latest
```

### Validation CI/CD reelle (Debian 11, 2 Go RAM)

Pipeline dedie: `.github/workflows/verification_reelle.yml`

- environnement conteneur Debian 11 minimal,
- limite memoire `2g`,
- clonage du depot depuis GitHub (`https://github.com/roro627/maintenance_logicielle`),
- execution complete sans variables de simulation.

Execution locale equivalente via `act`:

```bash
~/.local/bin/act -W .github/workflows/verification_reelle.yml -j verification_reelle_debian11 --container-architecture linux/amd64 -P ubuntu-latest=catthehacker/ubuntu:act-latest
```

## Validation

```bash
./scripts/tests/test_deploiement.sh
```

## Depannage

- Consulter le dernier journal dans `logs/post_pull_update_*.log`.
- Si le journal est absent dans `logs/`, verifier `~/.cache/maintenance_logicielle/logs/`.
- Verifier qu aucun verrou stale n est present (`.post_pull.lock`).
- Relancer `./scripts/deploiement/post_pull_update.sh`.

## Liens associes

- Installation: `installation.md`
- Tests: `tests.md`
- Technique: `technique.md`
