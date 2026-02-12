# Compatibilite des dependances

## Objectif

Centraliser les versions minimales et la politique de validation des dependances
pour Raspberry Pi OS et la borne arcade.

## Versions minimales supportees

### Noyau borne
- Java: OpenJDK 17 minimum.
- Python: 3.9 minimum.
- Lua: 5.3 minimum (5.4 recommande).
- LÖVE: 11.0 minimum.
- pip: 24.0 minimum.
- pytest: 8.0 minimum.
- mkdocs: 1.5 minimum.
- pygame: 2.5 minimum.
- librosa: 0.10 minimum (PianoTile), avec fallback runtime si absent.
- LÖVE est obligatoire et valide automatiquement dans les tests de compatibilite.
- Le minimum Python est aligne sur Debian 11 (base de la verification CI reelle).

### Bibliotheques
- MG2D: miroir local strict du depot officiel `https://github.com/synave/MG2D`, non modifie localement.
- JavaZoom JLayer: version embarquee dans `borne_arcade/javazoom`.
- pygame: requis pour certains jeux Python.
- librosa: requis prefere pour l analyse rythme PianoTile (`borne_arcade/projet/PianoTile/requirements.txt`).
- libsndfile1: dependance systeme audio pour l ecosysteme librosa.
- curl: dependance systeme requise pour telecharger automatiquement les binaires lint quand necessaire.

## Procedure avant ajout de dependance

1. Verifier la documentation officielle.
2. Verifier la disponibilite sur Raspberry Pi OS.
3. Verifier la licence.
4. Documenter la decision ici si dependance niche/risquee.

## Validation automatisee

- Les versions minimales sont centralisees dans `config/versions_minimales.env`.
- Le script `scripts/tests/test_versions_compatibilite.sh` valide Java, Python, pip, pytest, mkdocs, pygame,
  puis Lua et LÖVE (obligatoires des qu un jeu Lua est present).
- L installation auto verifie et installe les paquets systeme manquants (dont `libsndfile1`) via `scripts/install/installer_borne.sh`.
- Le bootstrap `sudo` conserve la compatibilite d exploitation en executant compilation/lint/tests/docs sous l utilisateur appelant, puis en normalisant ownership/permissions de `build/`, `.venv/`, `logs/` et `.cache/`.

## Commandes

```bash
./scripts/tests/test_versions_compatibilite.sh
```

## Depannage

- Si une version est trop ancienne: mettre a jour via `apt` ou `pip` selon l outil.
- Si LÖVE ou Lua manque: installer `love` et `lua5.4`.
- Si pygame manque dans la venv: relancer `./scripts/install/installer_borne.sh`.
- Si librosa manque: relancer `./scripts/install/installer_borne.sh` ou installer via `./.venv/bin/pip install -r borne_arcade/projet/PianoTile/requirements.txt`.
- Si `love` echoue sur Debian 11 minimal: le bootstrap applique un contournement automatique puis relance `apt -f install`.
- Pour repartir de zero: lancer `Reset prerequis` depuis `MaintenanceMode`, puis `sudo ./bootstrap_borne.sh` pour reinstaller.

## Liens associes

- Installation: `installation.md`
- Technique: `technique.md`
- Tests: `tests.md`
