# Installation

## Objectif

Automatiser l installation initiale avec un seul point d entree (`bootstrap_borne.sh`),
idempotent et relancable sans casser l existant.

## Commandes

### Installation automatisee recommandee

```bash
chmod +x ./bootstrap_borne.sh
sudo ./bootstrap_borne.sh
```

Le script `bootstrap_borne.sh` enchaine:

- installation systeme ciblee (paquet par paquet si manquant),
- installation de l outillage de qualite (dont `curl` pour les telechargements lint),
- creation/maintenance de la venv Python,
- installation des dependances par jeu (`requirements.txt`),
- permissions scripts, autostart, layout clavier,
- droits partages multi-utilisateurs sur `logs/`, `build/`, `.cache/`, `.venv/` et fichiers d exploitation,
- execution des etapes non-systeme (compilation/lint/tests/docs) sous l utilisateur appelant quand le bootstrap est lance via `sudo`,
- normalisation finale ownership/permissions (`build/`, `logs/`, `.cache/`, `.venv/`, `site/`) pour eviter les artefacts root bloquants,
- compilation, lint, tests smoke, documentation.

Le bootstrap est **obligatoirement lance en sudo/root** (hors mode test).
Sinon il s arrete avec un message clair et la commande de relance.

### Relance idempotente

```bash
sudo ./bootstrap_borne.sh
```

### Relance forcee de l etape installation

```bash
BOOTSTRAP_FORCER_INSTALLATION=1 sudo ./bootstrap_borne.sh
```

### Alternative manuelle (si besoin)

```bash
sudo ./scripts/install/installer_borne.sh
./borne_arcade/compilation.sh
./scripts/lint/lancer_lint.sh
./scripts/tests/test_smoke.sh
./scripts/docs/generer_documentation.sh
```

### Mode installation sans elevation (post-pull)

Pour un run automatique apres `git pull` sans bloquer si les dependances systeme
sont deja installees:

```bash
INSTALLATION_SYSTEME_OPTIONNEL=1 ./scripts/install/installer_borne.sh
```

Si une dependance systeme manque, le script echoue avec une action recommandee
(`sudo ./bootstrap_borne.sh`).

## Validation

```bash
./scripts/tests/test_installation.sh
./scripts/tests/test_smoke.sh
./scripts/tests/lancer_suite.sh
```

Le journal bootstrap est ecrit dans `logs/bootstrap_borne_YYYYMMDD_HHMMSS.log`.

## Depannage

- Erreur sudo: relancer avec `sudo ./bootstrap_borne.sh`.
- Erreur droits journaux (`Permission non accordee` dans `logs/`):
  relancer `sudo ./bootstrap_borne.sh` pour reappliquer les droits partages.
- Erreur droits build (`Permission non accordee`): corriger les droits puis relancer.

```bash
sudo chown -R "$USER:$USER" ./build ./.venv ./logs ./.cache ./site
./borne_arcade/clean.sh
./borne_arcade/compilation.sh
```

- Emplacement recommande du depot: dossier utilisateur (ex: `~/git/maintenance_logicielle`),
  pas un dossier systeme ou verrouille.
- Si `love` echoue sur Debian 11 minimal: le script applique automatiquement un contournement, puis corrige l etat `dpkg`.
- Si la borne ne demarre pas automatiquement: verifier `~/.config/autostart/borne.desktop`.
- Si le layout clavier ne s applique pas: verifier `~/.xkb/symbols/borne`.

## Liens associes

- Deploiement: `deploiement.md`
- Tests: `tests.md`
- Technique: `technique.md`
