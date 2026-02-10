# Compatibilite des dependances

## Noyau borne
- Java: OpenJDK 17 (LTS), stable sur Raspberry Pi OS.
- Python: 3.x present par defaut sur Raspberry Pi OS.
- LÖVE: paquet `love` pour jeux Lua.

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
