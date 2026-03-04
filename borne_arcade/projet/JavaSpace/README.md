# Java Space

## Objectif

Java Space est un shoot em up Java dans un univers de science fiction ou le joueur pilote un vaisseau et enchaine les vagues d ennemis.

## Runtime et lancement

- Runtime principal: `Java avec MG2D`.
- Point d entree: `Main`.
- Lanceur borne: `borne_arcade/JavaSpace.sh`.
- Lancement depuis la racine: `./borne_arcade/JavaSpace.sh`.

## Commandes borne

| Commande | Action |
| --- | --- |
| Joystick | Deplacer le vaisseau. |
| Bouton 4 | Tirer. |

## Fichiers importants

- `description.txt`: Description courte affichee dans le menu principal.
- `bouton.txt`: Mapping borne lu par le menu et les boites de description.
- `highscore`: Persistance locale du score.
- `photo_small.png`: Vignette affichee dans le catalogue de jeux.

## Tests et validation

- Test cible du jeu: `./scripts/tests/test_jeux_java_cibles.sh --jeu JavaSpace`.
- Validation globale de la borne: `TEST_INSTALLATION_SIMULATION=1 TEST_DEPLOIEMENT_SIMULATION=1 BORNE_MODE_TEST=1 bash ./scripts/tests/lancer_suite.sh`.

## Maintenance et evolution

- Le jeu gere son menu et sa boucle de partie dans un moteur Java historique propre au projet.
- La compilation passe par `./borne_arcade/compilation.sh` et par le wrapper Java commun de la borne.

## Liens associes

- [Ajout d un jeu](../../../docs/ajout_jeu.md).
- [Tests](../../../docs/tests.md).
- [Utilisateur](../../../docs/utilisateur.md).
