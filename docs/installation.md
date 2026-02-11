# Installation

## Objectif

Automatiser l installation initiale et les relances de maintenance avec un point d entree unique,
idempotent et non interactif autant que possible.

## Commandes

### Installation automatisee recommandee

```bash
chmod +x ./bootstrap_borne.sh
./bootstrap_borne.sh
```

Le script `bootstrap_borne.sh` enchaine:
- detection des dependances systeme ciblees et installation des paquets manquants,
- preparation venv Python et dependances projet,
- permissions scripts et autostart,
- compilation, lint, tests smoke, generation documentation.

Pour les etapes systeme, un compte **root** ou **sudo valide** est obligatoire.
Si sudo n est pas utilisable, le bootstrap s arrete avec un message d action clair.

### Relance idempotente

```bash
./bootstrap_borne.sh
```

### Relance forcee de l etape installation

```bash
BOOTSTRAP_FORCER_INSTALLATION=1 ./bootstrap_borne.sh
```

### Alternative manuelle (si besoin)

```bash
./scripts/install/installer_borne.sh
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

- Si le bootstrap echoue sur les privileges: valider sudo (`sudo -v`) puis relancer.
- Si un paquet systeme manque encore: relancer en root ou avec `sudo` valide.
- Si la borne ne demarre pas automatiquement: verifier `~/.config/autostart/borne.desktop`.
- Si le layout clavier ne s applique pas: verifier `~/.xkb/symbols/borne` puis relancer l installation.

## Liens associes

- Deploiement: `deploiement.md`
- Tests: `tests.md`
- Technique: `technique.md`
