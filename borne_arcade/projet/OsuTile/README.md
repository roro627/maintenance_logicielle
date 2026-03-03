# OsuTile

## Objectif

OsuTile est un jeu de rythme ou il faut frapper les bonnes colonnes au bon moment a partir de cartes derivees de fichiers `.osu`.

## Runtime et lancement

- Runtime principal: `Python`.
- Point d entree: `main.py`.
- Lanceur borne: `borne_arcade/OsuTile.sh`.
- Lancement depuis la racine: `./borne_arcade/OsuTile.sh`.

## Commandes borne

| Commande | Action |
| --- | --- |
| Joystick | Naviguer dans les menus de selection. |
| Boutons 1 a 4 | Jouer les quatre colonnes de notes pendant la partie. |
| Bouton 5 | Selectionner, reprendre ou valider selon le menu courant. |
| Bouton 6 | Quitter, revenir au menu ou recommencer selon l ecran courant. |

## Fichiers importants

- `description.txt`: Description courte affichee dans le menu principal.
- `bouton.txt`: Mapping borne lu par le menu et les boites de description.
- `highscore`: Persistance locale du score.
- `photo_small.png`: Vignette affichee dans le catalogue de jeux.
- `tests/`: tests locaux du jeu.

## Tests et validation

- Test cible du jeu: `./scripts/tests/test_jeux_python_cibles.sh --jeu OsuTile`.
- Validation globale de la borne: `TEST_INSTALLATION_SIMULATION=1 TEST_DEPLOIEMENT_SIMULATION=1 BORNE_MODE_TEST=1 ./scripts/tests/lancer_suite.sh`.

## Maintenance et evolution

- Le jeu exporte les beatmaps `.osu` vers des cartes Python dans `maps/` quand elles sont absentes.
- Le lancement borne passe par le wrapper Python commun et doit rester compatible avec `python3`.
- Des tests locaux existent dans `tests/` et doivent etre maintenus a jour.
- Verifier la coherence entre `beatmaps/`, `maps/` et les tests locaux lors de l ajout d une nouvelle chanson.

## Liens associes

- [Ajout d un jeu](../../../docs/ajout_jeu.md).
- [Tests](../../../docs/tests.md).
- [Utilisateur](../../../docs/utilisateur.md).
