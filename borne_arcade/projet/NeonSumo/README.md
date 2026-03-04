# Neon Sumo

## Objectif

Neon Sumo est un duel arcade 1v1 ou il faut ejecter l adversaire de l arene en exploitant dash, bump, bouclier et ultime.

## Runtime et lancement

- Runtime principal: `Python`.
- Point d entree: `main.py`.
- Lanceur borne: `borne_arcade/NeonSumo.sh`.
- Lancement depuis la racine: `./borne_arcade/NeonSumo.sh`.
- Dependances Python locales: `pip install -r borne_arcade/projet/NeonSumo/requirements.txt`.

## Commandes borne

| Commande | Action |
| --- | --- |
| Joystick | Diriger le joueur courant dans l arene. |
| Bouton 1 | Dash. |
| Bouton 2 | Frein. |
| Bouton 3 | Bump. |
| Bouton 4 | Bouclier. |
| Bouton 5 | Taunt. |
| Bouton 6 | Ultime. |

## Fichiers importants

- `description.txt`: Description courte affichee dans le menu principal.
- `bouton.txt`: Mapping borne lu par le menu et les boites de description.
- `highscore`: Persistance locale du score.
- `photo_small.png`: Vignette affichee dans le catalogue de jeux.
- `requirements.txt`: dependances Python specifiques au jeu.
- `config_jeu.json`: configuration supplementaire du jeu.
- `tests/`: tests locaux du jeu.

## Tests et validation

- Test cible du jeu: `./scripts/tests/test_jeux_python_cibles.sh --jeu NeonSumo`.
- Validation globale de la borne: `TEST_INSTALLATION_SIMULATION=1 TEST_DEPLOIEMENT_SIMULATION=1 BORNE_MODE_TEST=1 bash ./scripts/tests/lancer_suite.sh`.

## Maintenance et evolution

- Le jeu propose un mode attract robuste, un HUD lisible, un rappel complet des commandes sur l ecran titre et une arene neon qui retrecit au fil de la manche.
- Le lancement borne passe par le wrapper Python commun et doit rester compatible avec `python3`.
- Les dependances specifiques sont centralisees dans `requirements.txt`.
- Des tests locaux existent dans `tests/` et doivent etre maintenus a jour.
- Surveiller `config_jeu.json` pour toute evolution de configuration.
- Le fichier `config_jeu.json` centralise l equilibrage, les effets visuels et le menu titre anime.

## Liens associes

- [Ajout d un jeu](../../../docs/ajout_jeu.md).
- [Tests](../../../docs/tests.md).
- [Utilisateur](../../../docs/utilisateur.md).
