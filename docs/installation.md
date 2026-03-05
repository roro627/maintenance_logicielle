# Installation

## Objectif

Automatiser l installation initiale avec un seul point d entree (`bootstrap_borne.sh`),
idempotent et relancable sans casser l existant.

## Commandes

### Installation automatisee recommandee

```bash
sudo bash ./bootstrap_borne.sh
```

Le script `bootstrap_borne.sh` enchaine:

- installation systeme ciblee (paquet par paquet si manquant),
- installation de `Docker Engine` depuis le depot officiel si absent, avec mapping automatique Raspberry Pi OS -> depot Docker Debian quand `raspbian` n est plus adapte, puis fallback vers `docker.io`/`docker-cli` si le depot officiel echoue,
- installation de `act` depuis la release officielle (`/usr/local/bin/act`) avec lien utilisateur `~/.local/bin/act`,
- ajout de l utilisateur appelant au groupe `docker` pour executer `act` sans `sudo`,
- installation de l outillage de qualite (dont `curl` pour les telechargements lint),
- creation/maintenance de la venv Python avec fallback `piwheels` sur Raspberry Pi OS,
- installation des dependances par jeu (`requirements.txt`),
- permissions scripts, autostart, layout clavier,
- droits partages multi-utilisateurs sur tout le depot exploitable (racine du projet, `config/`, `docs/`, `.github/`, `logs/`, `build/`, `.cache/`, `.venv/`, `site/`, `scripts/`, `.githooks/`, `borne_arcade/`), hors `.git/` et `MG2D/`,
- execution des etapes non-systeme (compilation/lint/tests/docs) sous l utilisateur appelant quand le bootstrap est lance via `sudo`,
- normalisation finale ownership/permissions du depot exploitable pour eviter les artefacts root bloquants et reappliquer le bit executable sur tous les lanceurs `.sh`, y compris `./borne_arcade/lancerBorne.sh`,
- compilation, lint, tests smoke, documentation.

Quand `Node.js` provient du depot officiel NodeSource, l installateur considere
`node` et `npm` comme satisfaits des qu ils sont disponibles en commande,
meme si le paquet Debian `npm` n est pas installe separement. Cela evite un
conflit `nodejs` vs `npm` sur Debian 11 lors des relances idempotentes.

Pour Java, le bootstrap exige toujours un JDK **17 minimum**, mais il ne
fige plus `openjdk-17-jdk` comme unique paquet. Il resout maintenant la
dependance logique `java-jdk` vers `openjdk-17-jdk` quand ce paquet est
present dans les depots, sinon vers `default-jdk` si la distribution ne
publie plus `openjdk-17-jdk` separement.

Pour `pygame`, le bootstrap installe aussi `python3-pygame` au niveau systeme
afin de recuperer les bibliotheques SDL/audio necessaires meme sur une image
Raspberry Pi OS minimale, puis conserve l installation Python projet dans la
venv.

Le bootstrap est **obligatoirement lance en sudo/root** (hors mode test).
Sinon il s arrete avec un message clair et la commande de relance.

### Outil optionnel pour la proposition de PR

Le workflow de migration versions peut proposer une PR via CLI avec `gh`.
Cette dependance n est pas obligatoire pour faire tourner la borne, mais elle est
requise pour l etape finale `proposer-pr`:

```bash
gh --version
```

### Outils optionnels pour l etape IA de migration

L etape `preparer-ia` utilise `codex exec` avec un provider Ollama et le modele
configure dans `config/assistant_ia_migration.json` (par defaut `qwen3:8b`).
Le bootstrap installe `codex` automatiquement via `npm`.
Si la distribution expose un Node.js trop ancien pour Codex (cas typique Debian 11),
le bootstrap prepare d abord Node.js 22.x via le depot officiel NodeSource, puis
relance l installation de `codex`.
Le serveur Ollama est joignable via `ollama.base_url` dans cette meme configuration
et n exige pas le binaire `ollama` sur la borne si Codex peut atteindre l URL distante.
En environnement conteneurise de validation, le bootstrap n exige pas `docker`, `act`
ni `codex` pour reutiliser un etat deja prepare.
En mode `BORNE_MODE_TEST=1`, l installation et la verification de `codex` sont ignorees
pour ne pas fausser la CI de simulation.
Ces dependances ne sont pas requises pour lancer les jeux, mais elles sont
necessaires pour l adaptation assistee du depot pendant une migration:

```bash
codex --help
```

### Relance idempotente

```bash
sudo bash ./bootstrap_borne.sh
```

### Relance forcee de l etape installation

```bash
BOOTSTRAP_FORCER_INSTALLATION=1 sudo bash ./bootstrap_borne.sh
```

### Reinitialisation locale pour retester depuis zero

Si vous devez repartir d un etat local propre, supprimer les artefacts generees
puis relancer le bootstrap:

```bash
rm -rf .venv build site .cache/bootstrap_borne
rm -f .etat_derniere_maj .post_pull.lock
```

Ensuite relancer:

```bash
sudo bash ./bootstrap_borne.sh
```

### Alternative manuelle (si besoin)

```bash
sudo bash ./scripts/install/installer_borne.sh
bash ./borne_arcade/compilation.sh
bash ./scripts/lint/lancer_lint.sh
bash ./scripts/tests/test_smoke.sh
bash ./scripts/docs/generer_documentation.sh
```

### Mode installation sans elevation (post-pull)

Pour un run automatique apres `git pull` sans bloquer si les dependances systeme
sont deja installees:

```bash
INSTALLATION_SYSTEME_OPTIONNEL=1 bash ./scripts/install/installer_borne.sh
```

Si une dependance systeme manque, le script echoue avec une action recommandee
(`sudo bash ./bootstrap_borne.sh`).

### Reglage affichage borne

Le comportement d affichage des lanceurs est centralise dans
`borne_arcade/config/borne.env`:

- `RESOLUTION_X=1280`
- `RESOLUTION_Y=1024`
- `MODE_AFFICHAGE_BORNE=fenetre_sans_bordure`
- `POSITION_FENETRE_X=0`
- `POSITION_FENETRE_Y=0`

Les scripts `lancer_jeu_python.sh`, `lancer_jeu_love.sh` et `lancer_jeu_java.sh`
propagent ces valeurs au jeu lance. `MaintenanceMode` les consomme directement et
ouvre son interface en `1280x1024` sans barre de titre par defaut.

## Validation

```bash
bash ./scripts/tests/test_installation.sh
bash ./scripts/tests/test_smoke.sh
bash ./scripts/tests/lancer_suite.sh
```

Le journal bootstrap est ecrit dans `logs/bootstrap_borne_YYYYMMDD_HHMMSS.log`.

## Depannage

- Erreur sudo: relancer avec `sudo bash ./bootstrap_borne.sh`.
- Erreur droits journaux (`Permission non accordee` dans `logs/`):
  relancer `sudo bash ./bootstrap_borne.sh` pour reappliquer les droits partages.
- Erreur droits build (`Permission non accordee`): corriger les droits puis relancer.
- Erreur lancement menu (`./borne_arcade/lancerBorne.sh: Permission non accordee`):
  relancer `sudo bash ./bootstrap_borne.sh` pour reappliquer les droits de partage sur tout le depot exploitable.
- Erreur lancement jeu (`Cannot run program \"./NomJeu.sh\": error=13, Permission non accordee`):
  relancer `sudo bash ./bootstrap_borne.sh` pour reappliquer les permissions d execution sur tous les lanceurs et wrappers `.sh`.

- Emplacement recommande du depot: dossier utilisateur (ex: `~/git/maintenance_logicielle`),
  pas un dossier systeme ou verrouille.
- Si `love` echoue sur Debian 11 minimal: le script applique automatiquement un contournement uniquement quand le paquet `love` est reellement casse en post-installation, puis corrige l etat `dpkg`.
- Si `apt` signale `Unable to locate package openjdk-17-jdk` sur Raspberry Pi OS / Debian `trixie`: relancer `sudo bash ./bootstrap_borne.sh`; le bootstrap choisit maintenant automatiquement `default-jdk` sur cette generation de distribution.
- Si Docker echoue sur Raspberry Pi OS: le bootstrap bascule deja sur le depot Docker Debian, puis tente `docker.io`/`docker-cli` si le depot officiel echoue. Si l erreur persiste, verifier `docker version`, `docker info` et les depots apt actifs.
- Si `pip install` est lent ou tente de compiler `pygame`/`numba` depuis les sources sur Raspberry Pi OS: verifier la connectivite vers `https://www.piwheels.org`; le bootstrap ajoute maintenant `piwheels` comme index supplementaire de secours.
- Si `act` reste inutilisable localement: verifier `docker info`, se deconnecter/reconnecter pour reappliquer le groupe `docker`, puis relancer `sudo bash ./bootstrap_borne.sh`.
- Si Docker vient juste d etre installe et que `docker info` ne repond qu avec `sudo`: fermer puis rouvrir la session utilisateur pour activer le groupe `docker`.
- Si `proposer-pr` echoue: verifier que `gh` est installe, authentifie (`gh auth status`) et que la branche de migration n est pas `main`.
- Si la borne ne demarre pas automatiquement: verifier `~/.config/autostart/borne.desktop`.
- Si le layout clavier ne s applique pas: verifier `~/.xkb/symbols/borne`.

## Liens associes

- Deploiement: `deploiement.md`
- Tests: `tests.md`
- Technique: `technique.md`
