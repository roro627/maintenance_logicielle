# Compatibilite des dependances

## Objectif

Centraliser les versions minimales et la politique de validation des dependances
pour Raspberry Pi OS et la borne arcade.

## Versions minimales supportees

### Noyau borne

- Java: OpenJDK 17 minimum.
- Paquet Java bootstrap: resolution dynamique `openjdk-17-jdk` puis
  `default-jdk` selon ce que la distribution expose, avec verification
  finale d un JDK >= 17.
- Python: 3.9 minimum.
- Lua: 5.3 minimum (5.4 recommande).
- LÖVE: 11.0 minimum.
- pip: 24.0 minimum.
- pytest: 8.0 minimum.
- mkdocs: 1.5 minimum.
- pygame: 2.5 minimum.
- Runtime pygame systeme: `python3-pygame` installe par le bootstrap pour
  garantir les bibliotheques SDL/audio minimales sur image Raspberry Pi OS
  reduite, meme si le projet utilise ensuite `pygame` dans la venv.
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
- Docker Engine: requis pour executer `act` localement, installe automatiquement via le depot officiel Docker; sur Raspberry Pi OS, le bootstrap cible d abord le depot Debian officiel, puis retombe sur `docker.io`/`docker-cli` si necessaire.
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
- Pour les dependances Python lourdes sur Raspberry Pi OS, l installateur ajoute
  `https://www.piwheels.org/simple` comme index pip supplementaire de secours
  afin d eviter autant que possible les compilations locales de `pygame`,
  `numba` et consorts.
- La dependance logique `java-jdk` reste idempotente sur les relances: la
  presence de `java` + `javac` avec une version compatible suffit, meme si le
  paquet Debian exact varie entre Debian 11, Bookworm et Trixie.
- L installation auto met a niveau Node.js via NodeSource quand `codex` ne peut pas tourner avec la version systeme.
- Les tests cible Lua utilisent `luac`/`lua` si disponibles; en leur absence, `CursedWare` conserve un validateur portable Python pour verifier le contrat statique des mini-jeux sans lancer LÖVE.
- La resolution des binaires Lua privilegie `lua5.4`/`luac5.4` puis `lua5.3`/`luac5.3` avant les alias generiques `lua`/`luac`, pour eviter un binaire legacy (ex: 5.1) quand une version compatible est deja installee.
- Le bootstrap `sudo` conserve la compatibilite d exploitation en executant compilation/lint/tests/docs sous l utilisateur appelant, puis en normalisant ownership/permissions sur tout le depot exploitable (`config/`, `docs/`, `.github/`, `build/`, `.venv/`, `logs/`, `.cache/`, `site/`, `scripts/`, `.githooks/`, `borne_arcade/` et la racine du projet), hors `.git/` et `MG2D/`.
- Cette normalisation reapplique aussi le bit executable sur tous les scripts `.sh` normalisables, y compris `bootstrap_borne.sh`, `./borne_arcade/lancerBorne.sh` et les lanceurs de jeux, pour rester compatible avec les checkouts Git en mode `100644`.
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
- Si `pygame` importe mal sur une image minimale malgre la venv: verifier que `python3-pygame` est bien installe, puis relancer `sudo bash ./bootstrap_borne.sh`.
- Si librosa manque: relancer `./scripts/install/installer_borne.sh` ou installer via `./.venv/bin/pip install -r borne_arcade/projet/PianoTile/requirements.txt`.
- Si `love` echoue sur Debian 11 minimal: le bootstrap applique un contournement automatique uniquement si `dpkg` montre un `love` non configure, puis relance `apt -f install`.
- Si `openjdk-17-jdk` est introuvable sur une distribution recente (ex: Raspberry Pi OS / Debian `trixie`): relancer `sudo bash ./bootstrap_borne.sh`; le bootstrap bascule automatiquement sur `default-jdk` puis verifie que Java 17 minimum est bien atteint.
- Si Docker echoue sur Raspberry Pi OS 32 bits ou `trixie`: relancer `sudo bash ./bootstrap_borne.sh`; le bootstrap reessaie maintenant via le depot Docker Debian, puis via `docker.io`/`docker-cli` si le depot officiel n expose pas les paquets attendus.
- Si `codex` echoue avec un message de version Node.js: relancer `sudo bash ./bootstrap_borne.sh` pour forcer l installation de Node.js 22.x via NodeSource.
- Si `docker info` echoue apres bootstrap: verifier le service Docker et rouvrir la session utilisateur pour reappliquer le groupe `docker`.
- Pour repartir d un etat local propre: supprimer `.venv`, `build`, `site`, `.cache/bootstrap_borne`, `.etat_derniere_maj` et `.post_pull.lock`, puis relancer `sudo bash ./bootstrap_borne.sh`.

## Liens associes

- Installation: `installation.md`
- Technique: `technique.md`
- Tests: `tests.md`
