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

### Outils optionnels de migration

- Codex CLI: requiert Node.js 16 minimum pour demarrer correctement.
- Bootstrap migration: cible Node.js 22.x via le depot officiel NodeSource si la version
  fournie par la distribution est trop ancienne pour Codex.
- Quand Node.js est fourni par NodeSource, la presence effective des commandes
  `node` et `npm` fait foi; l installateur n exige pas le paquet Debian `npm`
  separe si `npm` est deja embarque avec `nodejs`.
- Ollama distant: acces via `ollama.base_url`, sans obligation d installer le binaire
  `ollama` sur la borne.

### Bibliotheques

- MG2D: miroir local strict du depot officiel `https://github.com/synave/MG2D`, non modifie localement.
- JavaZoom JLayer: version embarquee dans `borne_arcade/javazoom`.
- pygame: requis pour certains jeux Python.
- librosa: requis prefere pour l analyse rythme PianoTile (`borne_arcade/projet/PianoTile/requirements.txt`).
- libsndfile1: dependance systeme audio pour l ecosysteme librosa.
- curl: dependance systeme requise pour telecharger automatiquement les binaires lint quand necessaire.
- Docker Engine: requis pour executer `act` localement, installe automatiquement via le depot officiel Docker sur Debian/Raspberry Pi OS/Ubuntu.
- act: version cible `0.2.84`, installee automatiquement depuis la release officielle GitHub.
- GitHub CLI (`gh`): dependance optionnelle, requise seulement pour l etape `proposer-pr` du workflow migration.

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
- L installation auto met a niveau Node.js via NodeSource quand `codex` ne peut pas tourner avec la version systeme.
- Les tests cible Lua utilisent `luac`/`lua` si disponibles; en leur absence, `CursedWare` conserve un validateur portable Python pour verifier le contrat statique des mini-jeux sans lancer LÖVE.
- Le bootstrap `sudo` conserve la compatibilite d exploitation en executant compilation/lint/tests/docs sous l utilisateur appelant, puis en normalisant ownership/permissions de `build/`, `.venv/`, `logs/`, `.cache/`, `site/`, `scripts/`, `.githooks/` et `borne_arcade/`.
- Cette normalisation reapplique aussi le bit executable sur tous les scripts `.sh` de `scripts/` et `borne_arcade/`, y compris les lanceurs de jeux, pour rester compatible avec les checkouts Git en mode `100644`.
- Le bootstrap prepare aussi l execution locale des workflows GitHub en validant `docker info` puis `act -W .github/workflows -l`.
- Le workflow migration versions reste portable pour la detection/brief IA/tests sur poste non Debian; l execution reelle de l assistant IA depend de `codex` et d un serveur Ollama joignable via `ollama.base_url`; l application reelle des migrations apt reste reservee a Raspberry Pi OS / Debian, avec verification explicite via `/etc/os-release`.

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
- Si `codex` echoue avec un message de version Node.js: relancer `sudo bash ./bootstrap_borne.sh` pour forcer l installation de Node.js 22.x via NodeSource.
- Si `docker info` echoue apres bootstrap: verifier le service Docker et rouvrir la session utilisateur pour reappliquer le groupe `docker`.
- Pour repartir de zero: lancer `Reset prerequis` depuis `MaintenanceMode`, puis `sudo bash ./bootstrap_borne.sh` pour reinstaller.

## Liens associes

- Installation: `installation.md`
- Technique: `technique.md`
- Tests: `tests.md`
