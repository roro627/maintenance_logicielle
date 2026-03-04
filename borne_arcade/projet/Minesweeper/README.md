# Minesweeper

## Objectif

Minesweeper adapte le demineur classique a la borne avec affichage MG2D, curseur clavier borne et highscore persistant.

## Runtime et lancement

- Runtime principal: `Java avec MG2D`.
- Point d entree: `Minesweeper`.
- Lanceur borne: `borne_arcade/Minesweeper.sh`.
- Lancement depuis la racine: `./borne_arcade/Minesweeper.sh`.

## Commandes borne

| Commande | Action |
| --- | --- |
| Joystick | Deplacer le curseur sur la grille. |
| Bouton 1 | Quitter la partie. |
| Bouton 4 | Creuser la case courante. |
| Bouton 5 | Poser ou retirer un drapeau. |
| Bouton 6 | Confirmer certaines actions de creusage selon le contexte. |

## Fichiers importants

- `description.txt`: Description courte affichee dans le menu principal.
- `bouton.txt`: Mapping borne lu par le menu et les boites de description.
- `highscore`: Persistance locale du score.
- `photo_small.png`: Vignette affichee dans le catalogue de jeux.

## Tests et validation

- Test cible du jeu: `./scripts/tests/test_jeux_java_cibles.sh --jeu Minesweeper`.
- Validation globale de la borne: `TEST_INSTALLATION_SIMULATION=1 TEST_DEPLOIEMENT_SIMULATION=1 BORNE_MODE_TEST=1 bash ./scripts/tests/lancer_suite.sh`.

## Maintenance et evolution

- Le jeu s appuie sur une vue MG2D, des effets sonores et une logique separee de niveau et de score.
- La compilation passe par `./borne_arcade/compilation.sh` et par le wrapper Java commun de la borne.

## Liens associes

- [Ajout d un jeu](../../../docs/ajout_jeu.md).
- [Tests](../../../docs/tests.md).
- [Utilisateur](../../../docs/utilisateur.md).
