# PianoTile

## Objectif

PianoTile est une adaptation borne du jeu de rythme piano avec navigation au clavier borne, selection de morceaux et score persistant.

## Runtime et lancement

- Runtime principal: `Python`.
- Point d entree: `app/game.py`.
- Lanceur borne: `borne_arcade/PianoTile.sh`.
- Lancement depuis la racine: `./borne_arcade/PianoTile.sh`.
- Dependances Python locales: `pip install -r borne_arcade/projet/PianoTile/requirements.txt`.

## Commandes borne

| Commande | Action |
| --- | --- |
| Joystick | Naviguer dans les menus et les interfaces de selection. |
| Boutons 1 a 4 | Jouer les quatre colonnes de notes pendant la partie. |
| Bouton 5 | Selectionner, reprendre ou confirmer dans les menus. |
| Bouton 6 | Revenir en arriere ou quitter l ecran courant. |

## Fichiers importants

- `description.txt`: Description courte affichee dans le menu principal.
- `bouton.txt`: Mapping borne lu par le menu et les boites de description.
- `highscore`: Persistance locale du score.
- `photo_small.png`: Vignette affichee dans le catalogue de jeux.
- `requirements.txt`: dependances Python specifiques au jeu.
- `tests/`: tests locaux du jeu.

## Tests et validation

- Test cible du jeu: `./scripts/tests/test_jeux_python_cibles.sh --jeu PianoTile`.
- Validation globale de la borne: `TEST_INSTALLATION_SIMULATION=1 TEST_DEPLOIEMENT_SIMULATION=1 BORNE_MODE_TEST=1 ./scripts/tests/lancer_suite.sh`.

## Maintenance et evolution

- Le jeu tente d utiliser `librosa` pour analyser le rythme, avec un fallback si la dependance est absente.
- Le lancement borne passe par le wrapper Python commun et doit rester compatible avec `python3`.
- Les dependances specifiques sont centralisees dans `requirements.txt`.
- Des tests locaux existent dans `tests/` et doivent etre maintenus a jour.
- Le runtime audio doit rester non bloquant; en cas d echec ALSA ou PulseAudio, la partie doit rester jouable.

## Liens associes

- [Ajout d un jeu](../../../docs/ajout_jeu.md).
- [Tests](../../../docs/tests.md).
- [Utilisateur](../../../docs/utilisateur.md).
