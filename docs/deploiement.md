# Deploiement automatique

## Objectif
Apres `git pull`, la borne execute automatiquement:
1. installation/mise a jour outils,
2. compilation,
3. tests,
4. generation documentation.

## Mecanisme
- Hook versionne: `.githooks/post-merge`
- Pipeline local: `scripts/deploiement/post_pull_update.sh`

## Activation
```bash
git config core.hooksPath .githooks
chmod +x .githooks/post-merge scripts/deploiement/post_pull_update.sh
```

## Test
```bash
./scripts/tests/test_deploiement.sh
```
