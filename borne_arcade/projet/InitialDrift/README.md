# Initial Drift

## Objectif

Initial Drift est un jeu de conduite en vue arcade ou il faut tenir le plus longtemps possible en evitant trafic, chars et obstacles.

## Runtime et lancement

- Runtime principal: `Java avec MG2D`.
- Point d entree: `Main`.
- Lanceur borne: `borne_arcade/InitialDrift.sh`.
- Lancement depuis la racine: `./borne_arcade/InitialDrift.sh`.

## Commandes borne

| Commande | Action |
| --- | --- |
| Joystick | Piloter la voiture. |
| Bouton 3 | Quitter la partie. |

## Fichiers importants

- `description.txt`: Description courte affichee dans le menu principal.
- `bouton.txt`: Mapping borne lu par le menu et les boites de description.
- `highscore`: Persistance locale du score.
- `photo_small.png`: Vignette affichee dans le catalogue de jeux.

## Tests et validation

- Test cible du jeu: `./scripts/tests/test_jeux_java_cibles.sh --jeu InitialDrift`.
- Validation globale de la borne: `TEST_INSTALLATION_SIMULATION=1 TEST_DEPLOIEMENT_SIMULATION=1 BORNE_MODE_TEST=1 ./scripts/tests/lancer_suite.sh`.

## Maintenance et evolution

- La generation des ennemis est maintenant isolee dans une fabrique Java testable.
- La compilation passe par `./borne_arcade/compilation.sh` et par le wrapper Java commun de la borne.

## Liens associes

- [Ajout d un jeu](../../../docs/ajout_jeu.md).
- [Tests](../../../docs/tests.md).
- [Utilisateur](../../../docs/utilisateur.md).
