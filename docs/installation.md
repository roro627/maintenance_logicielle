# Installation

## Linux de developpement
```bash
sudo apt update
sudo apt install -y git openjdk-17-jdk python3 python3-venv python3-pip checkstyle pylint shellcheck xdotool
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip mkdocs pytest
./scripts/install/installer_borne.sh
```

## Raspberry Pi OS
```bash
sudo apt update && sudo apt full-upgrade -y
sudo apt install -y git openjdk-17-jdk python3 python3-venv python3-pip checkstyle pylint shellcheck xdotool love
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip mkdocs pytest pygame
./scripts/install/installer_borne.sh
cp borne_arcade/borne.desktop ~/.config/autostart/borne.desktop
```

## Verification
```bash
./scripts/tests/test_installation.sh
```

## Notes clavier borne
Le script d installation copie automatiquement le layout clavier `borne`:
- en local: `~/.xkb/symbols/borne`
- et tente aussi une copie systeme si les droits le permettent.
