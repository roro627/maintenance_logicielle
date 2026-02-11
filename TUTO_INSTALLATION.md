# Tuto rapide: installer et lancer la borne

## 1) Prerequis

- Linux ou Raspberry Pi OS
- `git`, `openjdk-17`, `python3`, `python3-venv`, `python3-pip`
- `checkstyle`, `pylint`, `shellcheck`, `xdotool`, `love`, `lua5.4`

## 2) Installation (depuis la racine du projet)

```bash
python3 -m venv .venv
. .venv/bin/activate
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
- place les classes Java dans `build/classes/`.

## 4) Lancer la borne

```bash
./borne_arcade/lancerBorne.sh
```

## 5) (Optionnel) Activer la mise a jour automatique apres `git pull`

```bash
git config core.hooksPath .githooks
```

Le hook `post-merge` lancera automatiquement installation, compilation, tests et documentation.

Pipeline manuel equivalent:
```bash
./scripts/deploiement/post_pull_update.sh
```

## 6) Verification rapide

```bash
./scripts/tests/lancer_suite.sh
```

## 6 bis) Regenerer la documentation

```bash
./scripts/docs/generer_documentation.sh
./.venv/bin/python -m mkdocs build -f mkdocs.yml --strict
```

La documentation HTML est generee dans `site/`.

Pour tester le site local:
```bash
cd site
python3 -m http.server 8765
```

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

## Documentation complete

La documentation detaillee est dans `docs/` et publiee dans le site MkDocs:
- installation: `docs/installation.md`
- deploiement: `docs/deploiement.md`
- tests: `docs/tests.md`
