# Documentation technique

## Objectif

Documenter les principes techniques du projet: architecture, automatisation,
qualite, configuration et contraintes MG2D.

## Architecture technique

- `borne_arcade/`: menu principal, jeux, scripts de lancement.
- `borne_arcade/ControleurMenuBorne.java` + `EtatMenuBorne.java`: logique pure du menu testable sans interface graphique.
- `borne_arcade/LanceurJeuMenu.java` + `LanceurJeuProcessus.java`: abstraction de lancement de jeu injectable en test.
- `borne_arcade/projet/MaintenanceMode/`: interface maintenance cache (pygame).
- `borne_arcade/projet/InitialDrift/FabriqueEnnemiInitialDrift.java`: generation pure des ennemis.
- `borne_arcade/projet/Pong/EtatPong.java` + `MoteurPong.java`: noyau pur des regles de manche.
- `borne_arcade/projet/Kowasu_Renga/BriqueKowasuRenga.java`, `EtatKowasuRenga.java`, `MoteurKowasuRenga.java`: noyau pur briques/score/vies.
- `scripts/`: installation, deploiement, lint, tests, docs.
- `scripts/docs/generer_readme_jeux.py`: generateur deterministe des README de jeux a partir du template et des metadonnees.
- `config/`: versions minimales et regles qualite.
- `config/matrice_tests_jeux.json`: source de verite des jeux et de leur test cible obligatoire.
- `config/readme_jeux.json`: source de verite editoriale des README de jeux.
- `config/cibles_migration.json`: source de verite declarative des cibles de migration versions.
- `docs/modeles/README_jeu.md`: template versionne des README de jeux.
- `scripts/migration/workflow_migration.py`: CLI stable du workflow de migration (`tsv` humain, `json` scriptable).
- `build/`: classes Java compilees.
- `.cache/`: cache technique (MG2D fallback).
- `.cache/maintenance_logicielle/etat_migration.json`: etat persistant hors sources du workflow de migration.
- `logs/`: traces d execution.

## Principes d implementation

- DRY: mutualisation dans `scripts/lib/outils_communs.sh`.
- KISS: scripts explicites, idempotents, orientes exploitation.
- Configuration centralisee dans `borne_arcade/config/borne.env`.
- Encodage des sources Java centralise dans `borne_arcade/config/borne.env` via `ENCODAGE_SOURCES_JAVA=UTF-8`;
  toutes les compilations shell passent par `executer_javac` pour rester deterministes meme en conteneur Debian minimal sans locale UTF-8 preconfiguree.
- Politique d affichage borne centralisee dans `borne_arcade/config/borne.env`:
  `RESOLUTION_X=1280`, `RESOLUTION_Y=1024`, `MODE_AFFICHAGE_BORNE`,
  `POSITION_FENETRE_X`, `POSITION_FENETRE_Y`.
- README de jeux generes depuis `docs/modeles/README_jeu.md` + `config/readme_jeux.json` pour eviter les divergences editoriales entre projets.
- Mode maintenance cache configure via `borne_arcade/config/maintenance_mode.properties`.
- Mode maintenance pygame parametre via `borne_arcade/projet/MaintenanceMode/config_maintenance.json` (fenetre, theme, journal, timeouts).
- Les wrappers `lancer_jeu_python.sh` et `lancer_jeu_love.sh` projettent la politique d affichage borne dans l environnement SDL;
  `lancer_jeu_java.sh` projette les memes valeurs en proprietes JVM (`-Dborne.*`) pour les jeux Java compatibles.
- Operations maintenance executees en arriere-plan (thread dedie) avec journal temps reel non bloquant pour eviter le freeze UI.
- `MaintenanceMode` ouvre maintenant sa fenetre en `1280x1024` et interprete
  `mode_affichage=fenetre|fenetre_sans_bordure|plein_ecran`, avec priorite donnee aux variables exportees par le lanceur.
- Runtime subprocess maintenance portable: lecture threadee de `stdout`, encodage `locale.getpreferredencoding(False)` et `errors=\"replace\"` pour eviter les crashes Windows (`select`/decode).
- Timeout subprocess maintenance durci: un minuteur dedie interrompt aussi les commandes silencieuses sans sortie,
  ce qui garde les messages `Commande expiree...` fiables sur Debian 11 comme sur les postes de dev.
- Journal maintenance scrollable en mode manuel (`PgUp`/`PgDn` + `Gauche`/`Droite`) avec auto-scroll pilotable (`A`/`Fin`) et indicateurs visuels vertical/horizontal synchronises.
- La hauteur visible du journal MaintenanceMode est recalculee depuis la geometrie effective de la fenetre,
  ce qui supprime la zone morte observee avec l ancienne configuration `1280x720`.
- Journal maintenance aligne sur les usages console: lignes recentes affichees en bas et barre verticale orientee recent->bas.
- Journal maintenance resilient: selection automatique d un dossier logs ecrivable (`logs/`, puis `~/.cache/maintenance_logicielle/logs/`, puis `/tmp/maintenance_logicielle/logs/`) et retour d erreur actionnable en cas d exception inattendue.
- Workflow migration borne complet:
  detection CLI des versions installees/candidates,
  selection d une cible dans la combobox MaintenanceMode,
  application de la migration via commande systeme,
  generation d un brief IA double (`.md` + `.json`) puis execution de `codex exec --json`,
  relance qualite complete avec rapport JSON,
  proposition de PR via `gh pr create` seulement si la session et la qualite sont coherentes.
- Contrat JSON stable des cibles de migration:
  `id`, `titre`, `description`, `type`, `version_installee`, `version_candidate`,
  `migration_disponible`, `resume_migration`, `commande_migration_lisible`,
  `supportee_sur_hote`, `raison_indisponibilite`, et `version_paquet_installee` pour les paquets apt.
- Portabilite workflow migration:
  diagnostic, brief IA, tests et orchestration CLI restent executables sur poste Windows/macOS;
  l application reelle de migration apt reste reservee a Raspberry Pi OS / Debian avec message actionnable sinon.
- Session migration persistante:
  cible, versions, branche/commit git, etape IA executee, chemins du brief/de la reponse/de la trace et statut qualite sont traces dans `.cache/maintenance_logicielle/etat_migration.json`.
- Rapport qualite migration:
  `logs/rapport_qualite_migration_<cible>_<timestamp>.json` fait foi avant `proposer-pr`.
- Assistant IA migration:
  `config/assistant_ia_migration.json` pilote `Codex CLI + Ollama + Context7`;
  `ollama.base_url` y pointe vers le serveur Ollama distant et est projete en `CODEX_OSS_BASE_URL` pour Codex;
  le prompt versionne vit dans `config/prompt_migration_ia.md`;
  l execution produit un brief Markdown/JSON, une reponse Markdown et une trace JSONL temps reel;
  la commande CLI supportee repose sur `codex exec --json --oss --local-provider ollama`.
- Diagnostic maintenance durci: verification explicite des pre-requis borne et gestion robuste des sorties vides/commandes absentes.
- Operations git maintenance durcies: `git pull` et `retour commit precedent` verifient d abord la presence de git, puis retournent une erreur actionnable.
- Reset prerequis integre au mode maintenance en mode sur: purge apt limitee aux paquets non-systeme de la borne, paquets systeme critiques proteges (dont `python3`, `python3-venv`, `python3-pip`), suppression de `autoremove --purge`, puis nettoyage des artefacts locaux (`.venv`, `build`, `site`, etat bootstrap).
- Installation systeme idempotente: verification paquet par paquet puis installation des dependances manquantes.
- Codex CLI est installe automatiquement par le bootstrap via `npm install -g @openai/codex`, puis verifie par `codex --version`.
- Si Node.js est absent ou trop ancien pour Codex, l installateur prepare d abord Node.js 22.x via le depot officiel NodeSource.
- Relance idempotente Debian 11/NodeSource: la detection des dependances systeme considere `node`/`npm` disponibles par la commande, ce qui evite de tenter un `apt install npm` conflictuel apres installation de `nodejs` via NodeSource.
- En mode `BORNE_MODE_TEST=1`, l installation et la verification de Codex CLI sont ignorees pour garder les validations de simulation deterministes.
- Preparation `act` integree au bootstrap sur machine locale: installation/reutilisation de Docker Engine, ajout de l utilisateur appelant au groupe `docker`, installation de `act` dans `/usr/local/bin`, lien `~/.local/bin/act`, puis verification `docker info` et `act -W .github/workflows -l`.
- Verification Docker locale tolerante au premier bootstrap via `sudo`: l installateur valide Docker avec elevation si le groupe `docker` vient juste d etre applique, puis recommande une reconnexion utilisateur.
- Environnement conteneurise detecte: la preparation locale `Docker/act` est ignoree pour eviter les faux echecs CI sans daemon Docker.
- Permissions partagees appliquees par l installateur pour eviter les blocages multi-utilisateurs (`logs/`, `build/`, `.cache/`, `.venv/`, scripts et fichiers de jeu).
- Execution shell portable: les workflows GitHub Actions, le bootstrap, le pipeline post-pull et les scripts orienteurs de tests lancent les `.sh` via `bash` ou helper partage pour rester robustes meme si le depot est checkout avec des fichiers en mode Git `100644`.
- Dependance LÖVE obligatoire: installation stricte dans le bootstrap, avec contournement automatique Debian 11 si le paquet `love` casse sa post-installation.
- Privileges systeme obligatoires au bootstrap (`sudo`/root), avec echec explicite et action recommandee si indisponibles.
- Bootstrap lance via `sudo`: les etapes non-systeme (compilation/lint/tests/docs) sont executees avec l utilisateur appelant (`SUDO_USER`) pour eviter les artefacts root dans `build/`.
- Bootstrap finalise par une normalisation ownership/permissions de `build/`, `logs/`, `.cache/`, `.venv/` et `site/`.
- Pipeline post-pull resilient: installation en mode systeme optionnel et fallback de journalisation vers `~/.cache/maintenance_logicielle/logs/` si `logs/` n est pas accessible.
- Hook `post-merge` durci: controle de la presence de git et messages d erreur explicites si depot/script indisponible.
- Protection permissions build: message clair si `build/` n est pas accessible en ecriture.
- Menu optimise: suppression des chargements repetes police/son en boucle.
- Menu borne testable hors rendu: navigation, fermeture, verrouillage maintenance et lancement de jeu sont portes par `ControleurMenuBorne`.
- Catalogue borne durci: tri alphabetique sans casse dans `CatalogueJeux`,
  selection initiale alignee sur le premier jeu affiche et panneau descriptif
  synchronise avec le meme index logique que le lancement du jeu.
- Menu NeonSumo ameliore: rendu titre neon anime parametre via `config_jeu.json` (`menu_titre`) sans impacter la boucle gameplay.
- NeonSumo attract durci: les collisions/eliminations en mode attract declenchent une reinitialisation IA sans sortie vers les etats competitifs.
- PianoTile robuste: fallback sans `librosa` si la dependance n est pas disponible.
- PianoTile durci: lecture audio non bloquante (message actionnable en cas d echec ALSA/PulseAudio), chronometrage de secours sans audio et sortie d urgence `Echap` pendant une partie.
- Jeux SDL/Pygame adaptes a la borne: `TronGame`, `OsuTile`, `ball-blast` et `PianoTile`
  reprennent desormais `BORNE_RESOLUTION_X/Y` et `BORNE_MODE_AFFICHAGE`
  pour rester dans `1280x1024` sans barre de titre ou en plein ecran.
- CI/CD et tests automatisees via `.github/workflows/qualite.yml` et `bash ./scripts/tests/lancer_suite.sh`.
- Pipeline reel ajoute: `.github/workflows/verification_reelle.yml` (Debian 11 minimal, 2 Go RAM, sans variables de simulation).
- Garde anti-regression encodage Java: `scripts/tests/test_anti_regressions.sh` refuse toute invocation shell de `javac` hors helper centralise.
- Cache MG2D durci: les classes compilees en cache sont maintenant revalidees contre la version majeure supportee par le `javac` courant, ce qui evite de reutiliser un cache genere avec une JDK plus recente que l environnement de test.
- Orchestrateur jeux unique: `scripts/tests/test_contrats_jeux.py` applique contrat global puis test cible declare par jeu.
- Wrappers specialises: `scripts/tests/test_jeux_java_cibles.sh`, `scripts/tests/test_jeux_python_cibles.sh`, `scripts/tests/test_jeux_lua_cibles.sh`.
- Garde fou documentaire jeux: `scripts/tests/test_readme_jeux.sh` verifie la regeneration exacte des `README.md` et le nommage normalise.
- Politique CursedWare: validation headless par syntaxe/contrat mini-jeu, sans execution LÖVE complete en CI.

## Chaine d automatisation

1. `bootstrap_borne.sh`
2. `scripts/install/installer_borne.sh`
3. `borne_arcade/compilation.sh`
4. `scripts/lint/lancer_lint.sh`
5. `scripts/tests/test_smoke.sh`
6. `scripts/tests/lancer_suite.sh`
7. validation CI locale `act` (job `verification`)
8. validation CI reelle Debian 11 `act` (job `verification_reelle_debian11`)
9. `scripts/migration/workflow_migration.py` pour la detection, l assistant IA, la qualite et la PR de migration
10. `scripts/docs/generer_readme_jeux.py`
11. `scripts/docs/generer_documentation.sh`
12. `scripts/deploiement/post_pull_update.sh`

## Contraintes MG2D

Le dossier `MG2D/` est un miroir canonique de `https://github.com/synave/MG2D`.
Aucune modification locale n est autorisee dans `MG2D/`.

## Validation

```bash
./scripts/tests/test_integrite_mg2d.sh
./scripts/tests/test_architecture.sh
bash ./scripts/tests/lancer_suite.sh
```

## Liens associes

- Architecture: `architecture.md`
- Installation: `installation.md`
- Tests: `tests.md`
