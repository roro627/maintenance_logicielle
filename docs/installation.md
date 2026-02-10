# Installation

## Linux de developpement
```bash
sudo apt update
sudo apt install -y git openjdk-17-jdk python3 python3-venv python3-pip checkstyle pylint shellcheck xdotool lua5.4
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip mkdocs pytest
./scripts/install/installer_borne.sh
```

## Raspberry Pi OS
```bash
sudo apt update && sudo apt full-upgrade -y
sudo apt install -y git openjdk-17-jdk python3 python3-venv python3-pip checkstyle pylint shellcheck xdotool love lua5.4
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip mkdocs pytest pygame
./scripts/install/installer_borne.sh
```

## Verification
```bash
./scripts/tests/test_installation.sh
./borne_arcade/clean.sh
./borne_arcade/compilation.sh
```

Le script d installation prepare automatiquement un environnement virtuel
`./.venv` pour les dependances Python du projet.

Le script `borne_arcade/compilation.sh` valide tous les jeux:
- Java: compilation `javac`
- Python: verification syntaxique
- Lua: verification syntaxique si `luac` est disponible

## Generation de la documentation
```bash
./scripts/docs/generer_documentation.sh
```

Les pages HTML sont generees dans `site/`.

## Notes clavier borne
Le script d installation copie automatiquement le layout clavier `borne`:
- en local: `~/.xkb/symbols/borne`
- et tente aussi une copie systeme si les droits le permettent.

## Autostart borne
Le script d installation copie automatiquement:
- `borne_arcade/borne.desktop` vers `~/.config/autostart/borne.desktop`.
