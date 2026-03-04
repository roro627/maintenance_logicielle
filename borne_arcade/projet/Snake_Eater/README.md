# Snake Eater

## Objectif

Snake Eater adapte le Snake classique sur la borne avec score, highscore persistant et boucle MG2D en plein ecran.

## Runtime et lancement

- Runtime principal: `Java avec MG2D`.
- Point d entree: `Snake_Eater`.
- Lanceur borne: `borne_arcade/Snake_Eater.sh`.
- Lancement depuis la racine: `./borne_arcade/Snake_Eater.sh`.

## Commandes borne

| Commande | Action |
| --- | --- |
| Joystick | Diriger le serpent. |
| Bouton 3 | Quitter la partie. |

## Fichiers importants

- `description.txt`: Description courte affichee dans le menu principal.
- `bouton.txt`: Mapping borne lu par le menu et les boites de description.
- `highscore`: Persistance locale du score.
- `photo_small.png`: Vignette affichee dans le catalogue de jeux.

## Tests et validation

- Test cible du jeu: `./scripts/tests/test_jeux_java_cibles.sh --jeu Snake_Eater`.
- Validation globale de la borne: `TEST_INSTALLATION_SIMULATION=1 TEST_DEPLOIEMENT_SIMULATION=1 BORNE_MODE_TEST=1 bash ./scripts/tests/lancer_suite.sh`.

## Maintenance et evolution

- Le jeu conserve un highscore local et un message de fin adapte a la performance du joueur.
- La compilation passe par `./borne_arcade/compilation.sh` et par le wrapper Java commun de la borne.

## Liens associes

- [Ajout d un jeu](../../../docs/ajout_jeu.md).
- [Tests](../../../docs/tests.md).
- [Utilisateur](../../../docs/utilisateur.md).
