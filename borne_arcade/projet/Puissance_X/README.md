# Puissance X

## Objectif

Puissance X etend le principe du Puissance 4 avec un nombre parametrable de joueurs, d alignements et de parties contre IA.

## Runtime et lancement

- Runtime principal: `Java avec MG2D`.
- Point d entree: `Main`.
- Lanceur borne: `borne_arcade/Puissance_X.sh`.
- Lancement depuis la racine: `./borne_arcade/Puissance_X.sh`.

## Commandes borne

| Commande | Action |
| --- | --- |
| Joystick | Placer ou deplacer le pion courant. |
| Bouton 1 | Valider le coup. |
| Bouton 4 | Annuler ou revenir selon le contexte. |

## Fichiers importants

- `description.txt`: Description courte affichee dans le menu principal.
- `bouton.txt`: Mapping borne lu par le menu et les boites de description.
- `highscore`: Persistance locale du score.
- `photo_small.png`: Vignette affichee dans le catalogue de jeux.

## Tests et validation

- Test cible du jeu: `./scripts/tests/test_jeux_java_cibles.sh --jeu Puissance_X`.
- Validation globale de la borne: `TEST_INSTALLATION_SIMULATION=1 TEST_DEPLOIEMENT_SIMULATION=1 BORNE_MODE_TEST=1 bash ./scripts/tests/lancer_suite.sh`.

## Maintenance et evolution

- Le jeu est configurable et peut etre utilise a plusieurs joueurs ou contre des intelligences artificielles.
- La compilation passe par `./borne_arcade/compilation.sh` et par le wrapper Java commun de la borne.

## Liens associes

- [Ajout d un jeu](../../../docs/ajout_jeu.md).
- [Tests](../../../docs/tests.md).
- [Utilisateur](../../../docs/utilisateur.md).
