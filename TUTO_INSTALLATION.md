# Tuto rapide: installer et lancer la borne

## 1) Prerequis

- Linux ou Raspberry Pi OS
- `git`, `openjdk-17`, `python3`, `python3-pip`

## 2) Installation (depuis la racine du projet)

```bash
./scripts/install/installer_borne.sh
```

## 3) Compiler le menu et les jeux Java

```bash
./borne_arcade/clean.sh
./borne_arcade/compilation.sh
```

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

## 7) Sur Raspberry Pi (autostart)

```bash
mkdir -p ~/.config/autostart
cp borne_arcade/borne.desktop ~/.config/autostart/borne.desktop
```

Au prochain redemarrage, la borne se lancera automatiquement.
