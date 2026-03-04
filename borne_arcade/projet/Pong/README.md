# Pong

## Objectif

Pong est l adaptation arcade du grand classique a deux raquettes, avec menu borne, score de manche et acceleration progressive.

## Runtime et lancement

- Runtime principal: `Java avec MG2D`.
- Point d entree: `Main`.
- Lanceur borne: `borne_arcade/Pong.sh`.
- Lancement depuis la racine: `./borne_arcade/Pong.sh`.

## Commandes borne

| Commande | Action |
| --- | --- |
| Joystick | Deplacer la barre. |
| Bouton 3 | Quitter la partie. |
| Bouton 4 | Lancer la balle. |

## Fichiers importants

- `description.txt`: Description courte affichee dans le menu principal.
- `bouton.txt`: Mapping borne lu par le menu et les boites de description.
- `highscore`: Persistance locale du score.
- `photo_small.png`: Vignette affichee dans le catalogue de jeux.

## Tests et validation

- Test cible du jeu: `./scripts/tests/test_jeux_java_cibles.sh --jeu Pong`.
- Validation globale de la borne: `TEST_INSTALLATION_SIMULATION=1 TEST_DEPLOIEMENT_SIMULATION=1 BORNE_MODE_TEST=1 bash ./scripts/tests/lancer_suite.sh`.

## Maintenance et evolution

- Le noyau de regles de manche est maintenant decouple du rendu dans des classes Java dediees.
- La compilation passe par `./borne_arcade/compilation.sh` et par le wrapper Java commun de la borne.

## Liens associes

- [Ajout d un jeu](../../../docs/ajout_jeu.md).
- [Tests](../../../docs/tests.md).
- [Utilisateur](../../../docs/utilisateur.md).
