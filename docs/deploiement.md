# Deploiement automatique

## Objectif

Apres `git pull`, executer automatiquement l installation/mise a jour,
la compilation, le lint, les tests et la regeneration documentation.

## Procedure

### Activation

```bash
sudo bash ./bootstrap_borne.sh
git config core.hooksPath .githooks
chmod +x .githooks/post-merge scripts/deploiement/post_pull_update.sh
```

### Execution manuelle

```bash
bash ./scripts/deploiement/post_pull_update.sh
```

Mecanismes utilises:

- hook versionne `.githooks/post-merge`,
- pipeline local `scripts/deploiement/post_pull_update.sh`,
- verrou anti-concurrence `.post_pull.lock`,
- journaux `logs/post_pull_update_YYYYMMDD_HHMMSS.log` (ou fallback automatique
  `~/.cache/maintenance_logicielle/logs/` si `logs/` n est pas accessible).

Le pipeline appelle l installateur en mode optionnel:

```bash
INSTALLATION_SYSTEME_OPTIONNEL=1 bash ./scripts/install/installer_borne.sh
```

Resultat:

- si les dependances systeme sont deja presentes, le deploiement continue sans root,
- si des dependances manquent, echec clair avec action recommandee (`sudo bash ./bootstrap_borne.sh`).
- les permissions partagees restent reappliquees (`logs/`, `build/`, `.cache/`, `.venv/`) pour eviter les blocages apres une installation root.
- la normalisation finale reapplique aussi le bit executable des hooks Git versionnes dans `.githooks/` (notamment `post-merge`) pour rester fiable sous `act` et apres un checkout/pull qui perd les metadonnees Unix.

### Workflow migration et PR

Le workflow de migration versions est expose en CLI via:

```bash
python scripts/migration/workflow_migration.py lister-cibles --format json
python scripts/migration/workflow_migration.py appliquer --cible java17
python scripts/migration/workflow_migration.py preparer-ia --cible java17
python scripts/migration/workflow_migration.py qualite --cible java17
python scripts/migration/workflow_migration.py proposer-pr --cible java17
```

Contraintes:

- `preparer-ia` genere un brief Markdown/JSON, lance `codex exec --json --oss --local-provider ollama -c model_reasoning_effort="high"` via `CODEX_OSS_BASE_URL` vers le serveur Ollama configure puis stocke une reponse Markdown et une trace JSONL.
- le comportement IA est versionne dans `config/assistant_ia_migration.json` et `config/prompt_migration_ia.md`.
- `proposer-pr` pousse la branche courante puis appelle `gh pr create`.
- `qualite` peut etre relancee sur le commit courant apres revision locale; l etat de session est alors resynchronise avant `proposer-pr`.
- la PR est refusee si la session migration n est pas coherente avec `HEAD`.
- la PR est refusee si le rapport qualite migration n est pas vert.
- la revue humaine et le merge restent manuels.

### Validation CI/CD locale (obligatoire en fin de run)

```bash
~/.local/bin/act -W .github/workflows/qualite.yml -j verification --container-architecture linux/amd64 -P ubuntu-latest=catthehacker/ubuntu:act-latest
```

### Validation CI/CD reelle (Debian 11, 2 Go RAM)

Pipeline dedie: `.github/workflows/verification_reelle.yml`

- declenchement automatique sur chaque commit (`push`), sans cron quotidien,
- environnement conteneur Debian 11 minimal,
- installation `apt` initiale du job protegee par plusieurs tentatives et timeouts reseau,
- limite memoire `2g`,
- clonage du depot depuis GitHub (`https://github.com/roro627/maintenance_logicielle`),
- execution complete sans variables de simulation.
- actions GitHub officielles alignees sur des versions Node 24 (`actions/checkout@v5`).

Execution locale equivalente via `act`:

```bash
~/.local/bin/act -W .github/workflows/verification_reelle.yml -j verification_reelle_debian11 --container-architecture linux/amd64 -P ubuntu-latest=catthehacker/ubuntu:act-latest
```

## Validation

```bash
bash ./scripts/tests/test_deploiement.sh
```

## Depannage

- Consulter le dernier journal dans `logs/post_pull_update_*.log`.
- Si le journal est absent dans `logs/`, verifier `~/.cache/maintenance_logicielle/logs/`.
- Verifier qu aucun verrou stale n est present (`.post_pull.lock`).
- Relancer `bash ./scripts/deploiement/post_pull_update.sh`.

## Liens associes

- Installation: `installation.md`
- Tests: `tests.md`
- Technique: `technique.md`
