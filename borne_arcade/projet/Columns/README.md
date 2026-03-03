# Columns

## Objectif

Columns est un jeu de puzzle arcade ou il faut aligner des gemmes de meme couleur pour les faire disparaitre avant que la grille ne se remplisse.

## Runtime et lancement

- Runtime principal: `Java avec MG2D`.
- Point d entree: `Main`.
- Lanceur borne: `borne_arcade/Columns.sh`.
- Lancement depuis la racine: `./borne_arcade/Columns.sh`.

## Commandes borne

| Commande | Action |
| --- | --- |
| Joystick | Deplacer la colonne de gemmes et ajuster sa position. |
| Bouton 3 | Quitter la partie. |
| Bouton 4 | Intervertir l ordre des gemmes de la colonne courante. |

## Fichiers importants

- `description.txt`: Description courte affichee dans le menu principal.
- `bouton.txt`: Mapping borne lu par le menu et les boites de description.
- `highscore`: Persistance locale du score.
- `photo_small.png`: Vignette affichee dans le catalogue de jeux.

## Tests et validation

- Test cible du jeu: `./scripts/tests/test_jeux_java_cibles.sh --jeu Columns`.
- Validation globale de la borne: `TEST_INSTALLATION_SIMULATION=1 TEST_DEPLOIEMENT_SIMULATION=1 BORNE_MODE_TEST=1 ./scripts/tests/lancer_suite.sh`.

## Maintenance et evolution

- Le jeu repose sur une boucle Java MG2D historique avec affichage plein ecran.
- La compilation passe par `./borne_arcade/compilation.sh` et par le wrapper Java commun de la borne.

## Liens associes

- [Ajout d un jeu](../../../docs/ajout_jeu.md).
- [Tests](../../../docs/tests.md).
- [Utilisateur](../../../docs/utilisateur.md).
