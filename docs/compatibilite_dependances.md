# Compatibilite des dependances

## Objectif

Centraliser les versions minimales et la politique de validation des dependances
pour Raspberry Pi OS et la borne arcade.

## Versions minimales supportees

### Noyau borne
- Java: OpenJDK 17 minimum.
- Python: 3.10 minimum.
- Lua: 5.3 minimum (5.4 recommande).
- LÖVE: 11.0 minimum.
- pip: 24.0 minimum.
- pytest: 8.0 minimum.
- mkdocs: 1.5 minimum.
- pygame: 2.5 minimum.

### Bibliotheques
- MG2D: miroir local strict du depot officiel `https://github.com/synave/MG2D`, non modifie localement.
- JavaZoom JLayer: version embarquee dans `borne_arcade/javazoom`.
- pygame: requis pour certains jeux Python.

## Procedure avant ajout de dependance

1. Verifier la documentation officielle.
2. Verifier la disponibilite sur Raspberry Pi OS.
3. Verifier la licence.
4. Documenter la decision ici si dependance niche/risquee.

## Validation automatisee

- Les versions minimales sont centralisees dans `config/versions_minimales.env`.
- Le script `scripts/tests/test_versions_compatibilite.sh` valide Java, Python, pip, pytest, mkdocs, pygame,
  et Lua/LÖVE si necessaire.

## Commandes

```bash
./scripts/tests/test_versions_compatibilite.sh
```

## Depannage

- Si une version est trop ancienne: mettre a jour via `apt` ou `pip` selon l outil.
- Si LÖVE ou Lua manque: installer `love` et `lua5.4`.
- Si pygame manque dans la venv: relancer `./scripts/install/installer_borne.sh`.

## Liens associes

- Installation: `installation.md`
- Technique: `technique.md`
- Tests: `tests.md`
