# Documentation technique

## Objectif

Documenter les principes techniques du projet: architecture, automatisation,
qualite, configuration et contraintes MG2D.

## Architecture technique

- `borne_arcade/`: menu principal, jeux, scripts de lancement.
- `borne_arcade/projet/MaintenanceMode/`: interface maintenance cache (pygame).
- `scripts/`: installation, deploiement, lint, tests, docs.
- `config/`: versions minimales et regles qualite.
- `build/`: classes Java compilees.
- `.cache/`: cache technique (MG2D fallback).
- `logs/`: traces d execution.

## Principes d implementation

- DRY: mutualisation dans `scripts/lib/outils_communs.sh`.
- KISS: scripts explicites, idempotents, orientes exploitation.
- Configuration centralisee dans `borne_arcade/config/borne.env`.
- Mode maintenance cache configure via `borne_arcade/config/maintenance_mode.properties`.
- Mode maintenance pygame parametre via `borne_arcade/projet/MaintenanceMode/config_maintenance.json` (fenetre, theme, journal, timeouts).
- Operations maintenance executees en arriere-plan (thread dedie) avec journal temps reel non bloquant pour eviter le freeze UI.
- Journal maintenance scrollable en mode manuel (`PgUp`/`PgDn` + `Gauche`/`Droite`) avec auto-scroll pilotable (`A`/`Fin`) et indicateurs visuels vertical/horizontal synchronises.
- Journal maintenance aligne sur les usages console: lignes recentes affichees en bas et barre verticale orientee recent->bas.
- Journal maintenance resilient: selection automatique d un dossier logs ecrivable (`logs/`, puis `~/.cache/maintenance_logicielle/logs/`, puis `/tmp/maintenance_logicielle/logs/`) et retour d erreur actionnable en cas d exception inattendue.
- Diagnostic maintenance durci: verification explicite des pre-requis borne et gestion robuste des sorties vides/commandes absentes.
- Operations git maintenance durcies: `git pull` et `retour commit precedent` verifient d abord la presence de git, puis retournent une erreur actionnable.
- Reset prerequis integre au mode maintenance en mode sur: purge apt limitee aux paquets non-systeme de la borne, paquets systeme critiques proteges (dont `python3`, `python3-venv`, `python3-pip`), suppression de `autoremove --purge`, puis nettoyage des artefacts locaux (`.venv`, `build`, `site`, etat bootstrap).
- Installation systeme idempotente: verification paquet par paquet puis installation des dependances manquantes.
- Permissions partagees appliquees par l installateur pour eviter les blocages multi-utilisateurs (`logs/`, `build/`, `.cache/`, `.venv/`, scripts et fichiers de jeu).
- Dependance LÖVE obligatoire: installation stricte dans le bootstrap, avec contournement automatique Debian 11 si le paquet `love` casse sa post-installation.
- Privileges systeme obligatoires au bootstrap (`sudo`/root), avec echec explicite et action recommandee si indisponibles.
- Bootstrap lance via `sudo`: les etapes non-systeme (compilation/lint/tests/docs) sont executees avec l utilisateur appelant (`SUDO_USER`) pour eviter les artefacts root dans `build/`.
- Bootstrap finalise par une normalisation ownership/permissions de `build/`, `logs/`, `.cache/`, `.venv/` et `site/`.
- Pipeline post-pull resilient: installation en mode systeme optionnel et fallback de journalisation vers `~/.cache/maintenance_logicielle/logs/` si `logs/` n est pas accessible.
- Hook `post-merge` durci: controle de la presence de git et messages d erreur explicites si depot/script indisponible.
- Protection permissions build: message clair si `build/` n est pas accessible en ecriture.
- Menu optimise: suppression des chargements repetes police/son en boucle.
- Menu NeonSumo ameliore: rendu titre neon anime parametre via `config_jeu.json` (`menu_titre`) sans impacter la boucle gameplay.
- NeonSumo attract durci: les collisions/eliminations en mode attract declenchent une reinitialisation IA sans sortie vers les etats competitifs.
- PianoTile robuste: fallback sans `librosa` si la dependance n est pas disponible.
- PianoTile durci: lecture audio non bloquante (message actionnable en cas d echec ALSA/PulseAudio), chronometrage de secours sans audio et sortie d urgence `Echap` pendant une partie.
- CI/CD et tests automatisees via `.github/workflows/qualite.yml` et `scripts/tests/lancer_suite.sh`.
- Pipeline reel ajoute: `.github/workflows/verification_reelle.yml` (Debian 11 minimal, 2 Go RAM, sans variables de simulation).

## Chaine d automatisation

1. `bootstrap_borne.sh`
2. `scripts/install/installer_borne.sh`
3. `borne_arcade/compilation.sh`
4. `scripts/lint/lancer_lint.sh`
5. `scripts/tests/test_smoke.sh`
6. `scripts/tests/lancer_suite.sh`
7. validation CI locale `act` (job `verification`)
8. validation CI reelle Debian 11 `act` (job `verification_reelle_debian11`)
9. `scripts/docs/generer_documentation.sh`
10. `scripts/deploiement/post_pull_update.sh`

## Contraintes MG2D

Le dossier `MG2D/` est un miroir canonique de `https://github.com/synave/MG2D`.
Aucune modification locale n est autorisee dans `MG2D/`.

## Validation

```bash
./scripts/tests/test_integrite_mg2d.sh
./scripts/tests/test_architecture.sh
./scripts/tests/lancer_suite.sh
```

## Liens associes

- Architecture: `architecture.md`
- Installation: `installation.md`
- Tests: `tests.md`
