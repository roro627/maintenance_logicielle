# Ball Blast

## Objectif

Ball Blast est un jeu d action arcade ou le joueur deplace un canon pour detruire des boules rebondissantes et faire monter le score.

## Runtime et lancement

- Runtime principal: `Python`.
- Point d entree: `./src`.
- Lanceur borne: `borne_arcade/ball-blast.sh`.
- Lancement depuis la racine: `./borne_arcade/ball-blast.sh`.
- Dependances Python locales: `pip install -r borne_arcade/projet/ball-blast/requirements.txt`.

## Commandes borne

| Commande | Action |
| --- | --- |
| Joystick | Deplacer le canon a gauche et a droite. |
| Bouton 1 | Interagir et valider dans les menus ou lors de la saisie du score. |
| Bouton 4 | Revenir en arriere ou quitter l ecran courant. |

## Fichiers importants

- `description.txt`: Description courte affichee dans le menu principal.
- `bouton.txt`: Mapping borne lu par le menu et les boites de description.
- `highscore`: Persistance locale du score.
- `photo_small.png`: Vignette affichee dans le catalogue de jeux.
- `requirements.txt`: dependances Python specifiques au jeu.
- `tests/`: tests locaux du jeu.

## Tests et validation

- Test cible du jeu: `./scripts/tests/test_jeux_python_cibles.sh --jeu ball-blast`.
- Validation globale de la borne: `TEST_INSTALLATION_SIMULATION=1 TEST_DEPLOIEMENT_SIMULATION=1 BORNE_MODE_TEST=1 bash ./scripts/tests/lancer_suite.sh`.

## Maintenance et evolution

- La fin de partie propose une saisie de pseudo sur trois lettres pour enregistrer le highscore local.
- Le lancement borne passe par le wrapper Python commun et doit rester compatible avec `python3`.
- Les dependances specifiques sont centralisees dans `requirements.txt`.
- Des tests locaux existent dans `tests/` et doivent etre maintenus a jour.
- Le jeu utilise des ressources audio et graphiques chargees depuis `assets/`, precharge ses frames d explosion et met en cache son panneau de score pour rester fluide en `1280x1024`.

## Liens associes

- [Ajout d un jeu](../../../docs/ajout_jeu.md).
- [Tests](../../../docs/tests.md).
- [Utilisateur](../../../docs/utilisateur.md).
