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
- creation/maintenance de la venv Python,
- installation des dependances par jeu (`requirements.txt`),
- permissions scripts, autostart, layout clavier,
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

## Validation

```bash
./scripts/tests/test_installation.sh
./scripts/tests/test_smoke.sh
./scripts/tests/lancer_suite.sh
```

Le journal bootstrap est ecrit dans `logs/bootstrap_borne_YYYYMMDD_HHMMSS.log`.

## Depannage

- Erreur sudo: relancer avec `sudo ./bootstrap_borne.sh`.
- Erreur droits build (`Permission non accordee`): corriger les droits puis relancer.

```bash
sudo chown -R "$USER:$USER" ./build
./borne_arcade/clean.sh
./borne_arcade/compilation.sh
```

- Emplacement recommande du depot: dossier utilisateur (ex: `~/git/maintenance_logicielle`),
  pas un dossier systeme ou verrouille.
- Si la borne ne demarre pas automatiquement: verifier `~/.config/autostart/borne.desktop`.
- Si le layout clavier ne s applique pas: verifier `~/.xkb/symbols/borne`.

## Liens associes

- Deploiement: `deploiement.md`
- Tests: `tests.md`
- Technique: `technique.md`
