# Deploiement automatique

## Objectif
Apres `git pull`, la borne execute automatiquement:
1. installation/mise a jour outils,
2. compilation,
3. lint,
4. tests,
5. generation documentation.

## Mecanisme
- Hook versionne: `.githooks/post-merge`
- Pipeline local: `scripts/deploiement/post_pull_update.sh`
- Verrou anti-concurrence: `.post_pull.lock`
- Journaux pipeline: `logs/post_pull_update_YYYYMMDD_HHMMSS.log`

## Activation
```bash
git config core.hooksPath .githooks
chmod +x .githooks/post-merge scripts/deploiement/post_pull_update.sh
```

## Execution manuelle du pipeline
```bash
./scripts/deploiement/post_pull_update.sh
```

Le pipeline applique automatiquement:
- installation,
- compilation,
- lint,
- suite de tests,
- regeneration documentation.

## Test
```bash
./scripts/tests/test_deploiement.sh
```

Le pipeline verifie aussi la compatibilite de versions via
`scripts/tests/test_versions_compatibilite.sh`.

La documentation regeneree par le pipeline est publiee dans `site/`.

## Diagnostic en cas d echec

- Consulter le dernier journal dans `logs/post_pull_update_*.log`.
- Verifier qu aucun verrou stale n est present (`.post_pull.lock`).
- Relancer ensuite `./scripts/deploiement/post_pull_update.sh`.
