# Kowasu Renga

## Objectif

Kowasu Renga est un casse briques classique base sur MG2D, adapte au format borne avec score et acceleration progressive.

## Runtime et lancement

- Runtime principal: `Java avec MG2D`.
- Point d entree: `Kowasu_Renga`.
- Lanceur borne: `borne_arcade/Kowasu_Renga.sh`.
- Lancement depuis la racine: `./borne_arcade/Kowasu_Renga.sh`.

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

- Test cible du jeu: `./scripts/tests/test_jeux_java_cibles.sh --jeu Kowasu_Renga`.
- Validation globale de la borne: `TEST_INSTALLATION_SIMULATION=1 TEST_DEPLOIEMENT_SIMULATION=1 BORNE_MODE_TEST=1 bash ./scripts/tests/lancer_suite.sh`.

## Maintenance et evolution

- Le noyau briques, vies, score et acceleration est maintenant factorise dans des classes Java dediees.
- La compilation passe par `./borne_arcade/compilation.sh` et par le wrapper Java commun de la borne.

## Liens associes

- [Ajout d un jeu](../../../docs/ajout_jeu.md).
- [Tests](../../../docs/tests.md).
- [Utilisateur](../../../docs/utilisateur.md).
