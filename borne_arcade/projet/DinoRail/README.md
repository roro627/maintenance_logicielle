# DinoRail

## Objectif

DinoRail reprend le principe du dino runner de navigateur dans une version borne arcade Java basee sur MG2D.

## Runtime et lancement

- Runtime principal: `Java avec MG2D`.
- Point d entree: `DinoRail`.
- Lanceur borne: `borne_arcade/DinoRail.sh`.
- Lancement depuis la racine: `./borne_arcade/DinoRail.sh`.

## Commandes borne

| Commande | Action |
| --- | --- |
| Joystick | Deplacer le dinosaure et gerer les actions de course. |
| Bouton 3 | Quitter la partie. |

## Fichiers importants

- `description.txt`: Description courte affichee dans le menu principal.
- `bouton.txt`: Mapping borne lu par le menu et les boites de description.
- `highscore`: Persistance locale du score.
- `photo_small.png`: Vignette affichee dans le catalogue de jeux.

## Tests et validation

- Test cible du jeu: `./scripts/tests/test_jeux_java_cibles.sh --jeu DinoRail`.
- Validation globale de la borne: `TEST_INSTALLATION_SIMULATION=1 TEST_DEPLOIEMENT_SIMULATION=1 BORNE_MODE_TEST=1 ./scripts/tests/lancer_suite.sh`.

## Maintenance et evolution

- Le jeu charge des effets sonores et un affichage plein ecran depuis les ressources locales.
- La compilation passe par `./borne_arcade/compilation.sh` et par le wrapper Java commun de la borne.

## Liens associes

- [Ajout d un jeu](../../../docs/ajout_jeu.md).
- [Tests](../../../docs/tests.md).
- [Utilisateur](../../../docs/utilisateur.md).
