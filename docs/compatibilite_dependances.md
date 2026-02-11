# Compatibilite des dependances

## Noyau borne
- Java: OpenJDK 17 minimum.
- Python: 3.10 minimum.
- Lua: 5.3 minimum (5.4 recommande).
- LÖVE: 11.0 minimum.
- pip: 24.0 minimum.
- pytest: 8.0 minimum.
- mkdocs: 1.5 minimum.
- pygame: 2.5 minimum.

## Bibliotheques
- MG2D: miroir local strict du depot officiel `https://github.com/synave/MG2D`, non modifie localement.
- JavaZoom JLayer: version embarquee dans `borne_arcade/javazoom`.
- pygame: requis pour certains jeux Python.

## Verification avant ajout de dependance
1. Verifier documentation officielle.
2. Verifier disponibilite Raspberry Pi OS.
3. Verifier licence.
4. Ajouter justification dans ce document si dependance niche.

## Verification automatisee
- Le fichier `config/versions_minimales.env` centralise les versions minimales supportees.
- Le script `scripts/tests/test_versions_compatibilite.sh` valide automatiquement:
  - Java, Python, pip, pytest, mkdocs,
  - pygame,
  - Lua/LÖVE si des jeux Lua sont presents et outils installes.

## Installation recommandee Raspberry Pi OS

```bash
sudo apt update && sudo apt full-upgrade -y
sudo apt install -y git openjdk-17-jdk python3 python3-venv python3-pip \
  checkstyle pylint shellcheck xdotool love lua5.4
```
