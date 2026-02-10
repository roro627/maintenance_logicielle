# Tuto rapide: installer et lancer la borne

## 1) Prerequis

- Linux ou Raspberry Pi OS
- `git`, `openjdk-17`, `python3`, `python3-pip`

## 2) Installation (depuis la racine du projet)

```bash
./scripts/install/installer_borne.sh
```

Ce script cree automatiquement `./.venv` pour les dependances Python.

## 3) Compiler/valider tous les jeux

```bash
./borne_arcade/clean.sh
./borne_arcade/compilation.sh
```

`compilation.sh`:
- compile les jeux Java,
- verifie la syntaxe des jeux Python,
- verifie la syntaxe des jeux Lua (si `luac` est installe).

## 4) Lancer la borne

```bash
./borne_arcade/lancerBorne.sh
```

## 5) (Optionnel) Activer la mise a jour automatique apres `git pull`

```bash
git config core.hooksPath .githooks
```

Le hook `post-merge` lancera automatiquement installation, compilation, tests et documentation.

## 6) Verification rapide

```bash
./scripts/tests/lancer_suite.sh
```

## 6 bis) Regenerer la documentation

```bash
./scripts/docs/generer_documentation.sh
```

La documentation HTML est generee dans `site/`.

## 7) Sur Raspberry Pi (autostart)

L autostart est configure automatiquement par `installer_borne.sh`
(`~/.config/autostart/borne.desktop`).
Au prochain redemarrage, la borne se lancera automatiquement.

## Depannage rapide
- Si le menu se lance sans musique de fond, verifier `borne_arcade/sound/bg/` (optionnel).
- Si le mapping clavier borne ne s applique pas, relancer:
```bash
./scripts/install/installer_borne.sh
```
Le script installe automatiquement le layout `borne` en local (`~/.xkb/symbols/borne`).
