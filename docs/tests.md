# Strategie de tests

## Objectif

Garantir la qualite et limiter les regressions sur installation, execution des jeux,
deploiement, documentation et conformite projet.

## Procedure

### Suite complete

```bash
TEST_INSTALLATION_SIMULATION=1 TEST_DEPLOIEMENT_SIMULATION=1 BORNE_MODE_TEST=1 bash ./scripts/tests/lancer_suite.sh
```

### Smoke tests rapides

```bash
./scripts/tests/test_smoke.sh
```

### Validation CI/CD equivalente GitHub Actions

```bash
~/.local/bin/act -W .github/workflows/qualite.yml -j verification --container-architecture linux/amd64 -P ubuntu-latest=catthehacker/ubuntu:act-latest
```

### Validation CI/CD reelle Debian 11 (sans variables de test)

```bash
~/.local/bin/act -W .github/workflows/verification_reelle.yml -j verification_reelle_debian11 --container-architecture linux/amd64 -P ubuntu-latest=catthehacker/ubuntu:act-latest
```

## Couverture

### Contrat global vs test cible

- Contrat global: chaque jeu doit passer une verification structurelle commune via `scripts/tests/test_contrats_jeux.py`:
  presence du dossier, des fichiers obligatoires, du lanceur, du point d entree et smoke test non interactif.
- Test cible: chaque jeu declare en plus une `commande_test_cible` obligatoire dans `config/matrice_tests_jeux.json`.
- La suite `scripts/tests/test_jeux.sh` compile toute la borne, execute le test borne headless, puis laisse `scripts/tests/test_contrats_jeux.py` enchainer contrat global + test cible pour chaque jeu.
- Le test borne headless recharge aussi le classpath MG2D a l execution afin de verifier l alignement catalogue/logique menu sans fenetre graphique.

### Matrice de couverture par jeu

- `Columns`: `TestContratColumns.java` couvre combos, suppression animee, chute et deplacement de colonne.
- `CursedWare`: `scripts/tests/test_jeux_lua_cibles.sh` + `borne_arcade/projet/CursedWare/tests/test_contrat_minijeux.lua` couvrent syntaxe Lua si disponible et contrat API des mini-jeux; aucun lancement LÖVE headless n est impose a cette phase.
- `DinoRail`: `TestContratDinoRail.java` couvre collisions et sortie ecran.
- `InitialDrift`: `TestContratInitialDrift.java` couvre la fabrique pure de generation des ennemis.
- `JavaSpace`: `TestContratJavaSpace.java` couvre apparition/rebond du boss et bornage du joueur.
- `Kowasu_Renga`: `TestContratKowasuRenga.java` couvre le noyau pur briques/vies/score/acceleration.
- `MaintenanceMode`: `test_operations.py` et `test_interface.py`.
- `Minesweeper`: `TestContratMinesweeper.java`.
- `NeonSumo`: `test_logique.py` et `test_main_menu.py` couvrent collisions, etats attract, mapping complet des commandes borne et fallback numerique J1 (`1..6` + pavé numerique).
- `OsuTile`: `test_osutile.py`.
- `PianoTile`: `test_piano.py`.
- `Pong`: `TestContratPong.java` couvre rebonds, score, reset de manche et retour menu.
- `Puissance_X`: `TestContratPuissanceX.java` (alignements + alias numeriques borne sur l entree clavier).
- `Snake_Eater`: `TestContratSnakeEater.java` couvre persistance/highscore.
- `TronGame`: `test_tron_game.py`.
- `ball-blast`: `test_ball_blast.py`.

### Unitaires

- HighScore (lecture/ecriture),
- mapping clavier borne,
- parsing configuration,
- controleur headless du menu borne (`borne_arcade/tests/unit/TestContratControleurMenuBorne.java`),
- logique pure de `Columns`, `InitialDrift`, `JavaSpace`, `Pong`, `Kowasu_Renga` et `Snake_Eater`,
- logique NeonSumo (collisions, sortie arene, cooldowns, ultime),
- configuration menu NeonSumo + logique d etats attract + coherence du mapping borne principal + fallback numerique J1 (`borne_arcade/projet/NeonSumo/tests/test_main_menu.py`),
- mode maintenance Python (`borne_arcade/projet/MaintenanceMode/tests/test_operations.py`):
  streaming logs temps reel, timeout actionnable y compris pour une commande silencieuse,
  journalisation des erreurs,
  fallback de dossier logs, operation `git_retour_precedent`,
  robustesse diagnostic en absence de pre-requis, gestion de l absence de `git`,
  retrait des anciennes options 10/11 du catalogue maintenance,
  capture des exceptions inattendues, persistence de session migration,
  execution IA `Codex/Ollama` avec brief Markdown+JSON, reponse Markdown, trace JSONL,
  rapport qualite migration, gardes avant `proposer-pr`
  et presence de la surcharge `model_reasoning_effort="high"` dans la commande Codex generee.
- logique d interface maintenance (`borne_arcade/projet/MaintenanceMode/tests/test_interface.py`):
  defilement vertical/horizontal du journal, auto-scroll, bornage de l historique, extraction de segment horizontal,
  focus combobox cible, preservation de la cible selectionnee apres rechargement,
  priorite de la configuration borne pour l affichage (`1280x1024`, mode sans bordure)
  et calcul du nombre de lignes visibles du journal sur la hauteur `1024`.
- configuration d affichage SDL/Pygame:
  verification de la reprise des variables `BORNE_*` dans `TronGame`, `OsuTile`,
  `ball-blast` et `PianoTile`.
- optimisation `ball-blast`:
  cache du panneau de score sans regeneration a score identique.
- CLI migration (`borne_arcade/projet/MaintenanceMode/tests/test_workflow_migration_cli.py`):
  contrat `--format json`, propagation de `--cible` et de `--dossier-sortie`.
- PianoTile (`borne_arcade/projet/PianoTile/tests/test_piano.py`):
  echec audio non bloquant et chronometrage de secours sans mixer actif.

### Integration et systeme

- catalogue jeux,
- test borne headless:
  compilation complete des `borne_arcade/*.java`,
  execution de `TestUnitaireCatalogueJeux.java`,
  execution de `TestContratControleurMenuBorne.java`,
  verification du tri alphabetique du catalogue et de la coherence selection initiale / navigation,
- compilation Java + verifications syntaxiques Python/Lua,
- ajout de jeu,
- deploiement post-pull,
- deploiement post-pull + verification permissions partagees (`logs/`, `build/`, `.cache/`, `.venv/`, scripts critiques, tous les `borne_arcade/**/*.sh`),
- installation + verification permissions partagees sur scripts, hooks, dossiers et ressources critiques (`bootstrap_borne.sh`, `scripts/deploiement/post_pull_update.sh`, `.githooks/post-merge`, `./borne_arcade/lancerBorne.sh`, `docs/`, `config/`, `borne.desktop`, images borne),
- installation + verification autostart utilisateur (`~/.config/autostart/borne.desktop`) avec commande `Exec` generee dynamiquement vers le chemin reel de `lancerBorne.sh`,
- README de jeux: presence, nommage `README.md`, regeneration deterministe et coherence entre template, matrice technique et metadonnees editoriales,
- generation documentation,
- architecture et couts,
- mode maintenance cache (presence, verrouillage, integration menu),
- mode maintenance cache (presence, verrouillage, integration menu, workflow migration cible),
- mode maintenance cache: application de migration en no-op non bloquant quand la cible est deja a jour (message d information actionnable),
- bootstrap robuste apres `sudo` (absence de regression sur normalisation permissions et execution non-systeme sous utilisateur appelant),
- bootstrap robuste apres `sudo` avec resynchronisation explicite de l autostart utilisateur (`borne.desktop`) a chaque execution,
- bootstrap robuste apres `sudo` y compris si les bits executables des lanceurs de jeux ont ete perdus lors d un checkout/pull,
- bootstrap robuste pour l outillage migration:
  garde `codex` inactive en mode test et mise a niveau automatique Node.js via NodeSource si la distribution est trop ancienne,
- bootstrap robuste pour Raspberry Pi OS:
  mapping `raspbian` vers le depot Docker Debian quand necessaire, fallback `docker.io`/`docker-cli` et fallback `piwheels` pour les installations Python lourdes,
- compilations Java deterministes:
  toutes les commandes shell `javac` passent par un encodage source explicite `UTF-8`,
  ce qui evite les echecs `unmappable character ... for encoding US-ASCII` dans le workflow reel Debian 11 minimal,
- cache MG2D robuste:
  `test_classpath_mg2d.sh` verifie aussi qu un cache `.class` compile avec un bytecode Java trop recent est invalide puis recompile automatiquement,
- robustesse PianoTile en absence de `librosa`,
- validation materielle (checklist).
- workflow migration portable:
  `versions-installees --format json` / `versions-candidates --format json` sans crash sur poste non Debian,
  avec message d indisponibilite actionnable pour l application reelle.

### Qualite outillage

- shellcheck,
- checkstyle,
- pylint,
- docstrings,
- uniformite des README de jeux,
- messages d erreur actionnables.

## Validation

Scripts principaux:

- `scripts/tests/test_installation.sh`
- `scripts/tests/test_smoke.sh`
- `scripts/tests/test_jeux.sh`
- `scripts/tests/test_borne_headless.sh`
- `scripts/tests/test_jeux_java_cibles.sh`
- `scripts/tests/test_jeux_python_cibles.sh`
- `scripts/tests/test_jeux_lua_cibles.sh`
- `scripts/tests/test_deploiement.sh`
- `scripts/tests/test_documentation.sh`
- `scripts/tests/test_readme_jeux.sh`
- `scripts/tests/test_integrite_mg2d.sh`
- `scripts/tests/test_architecture.sh`
- `scripts/tests/test_couts.sh`
- `scripts/tests/test_anti_regressions.sh`
- `.github/workflows/verification_reelle.yml`

## Depannage

- En cas d echec, relancer le script de test en erreur seul.
- Si `test_contrats_jeux.py` signale `commande_test_cible obligatoire`, completer `config/matrice_tests_jeux.json` avant toute autre correction.
- Si `test_readme_jeux.sh` echoue, regenerer les README avec `python3 scripts/docs/generer_readme_jeux.py` puis relancer la verification.
- Si un jeu Java charge mal ses ressources en test cible, verifier que le wrapper l execute bien depuis `borne_arcade/projet/<jeu>/`.
- Si `CursedWare` echoue sans `lua`, corriger d abord le validateur portable `scripts/tests/test_cursedware_minijeux.py`; si `lua` est disponible, verifier aussi `borne_arcade/projet/CursedWare/tests/test_contrat_minijeux.lua`.
- Si le workflow migration refuse `proposer-pr`, verifier d abord `.cache/maintenance_logicielle/etat_migration.json` puis le dernier `logs/rapport_qualite_migration_*.json`.
- Si le workflow reel Debian 11 echoue en compilation Java avec `US-ASCII`, verifier d abord `ENCODAGE_SOURCES_JAVA` dans `borne_arcade/config/borne.env` et l usage exclusif du helper `executer_javac`.
- Consulter `logs/` pour les pipelines post-pull/bootstrap.
- Corriger la cause puis relancer `bash ./scripts/tests/lancer_suite.sh`.
- En cas d echec CI locale, corriger puis relancer `act` jusqu a statut vert.

## Liens associes

- Installation: `installation.md`
- Deploiement: `deploiement.md`
- Technique: `technique.md`
