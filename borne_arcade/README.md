# Borne Arcade - Maintenance

## Vue d ensemble
Ce repertoire contient:
- le menu principal Java,
- les scripts de lancement des jeux,
- les jeux dans `projet/`.

La bibliotheque MG2D est utilisee en lecture seule depuis `../MG2D`.

## Installation rapide
Depuis la racine du projet:
```bash
./scripts/install/installer_borne.sh
```

## Compilation
```bash
./borne_arcade/clean.sh
./borne_arcade/compilation.sh
```

## Lancement borne
```bash
./borne_arcade/lancerBorne.sh
```

## Deploiement automatique apres git pull
```bash
git config core.hooksPath .githooks
```
Le hook `.githooks/post-merge` appelle `scripts/deploiement/post_pull_update.sh`.

## Documentation complete
La documentation complete est dans `docs/` et est generee par:
```bash
./scripts/docs/generer_documentation.sh
```
