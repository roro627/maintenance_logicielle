# Tron Game

## Objectif

Tron Game est un duel de motos lumineuses type Tron ou les joueurs doivent survivre plus longtemps que leur adversaire dans l arene.

## Runtime et lancement

- Runtime principal: `Python`.
- Point d entree: `main.py`.
- Lanceur borne: `borne_arcade/TronGame.sh`.
- Lancement depuis la racine: `./borne_arcade/TronGame.sh`.
- Dependances Python locales: `pip install -r borne_arcade/projet/TronGame/requirements.txt`.

## Commandes borne

| Commande | Action |
| --- | --- |
| Joystick J1 et J2 | Diriger les deux motos lumineuses. |
| Bouton 1 | Redemarrer une manche ou valider un ecran. |
| Bouton 2 | Mettre en pause ou reprendre. |
| Bouton 3 | Quitter vers le menu principal. |

## Fichiers importants

- `description.txt`: Description courte affichee dans le menu principal.
- `bouton.txt`: Mapping borne lu par le menu et les boites de description.
- `highscore`: Persistance locale du score.
- `photo_small.png`: Vignette affichee dans le catalogue de jeux.
- `requirements.txt`: dependances Python specifiques au jeu.
- `tests/`: tests locaux du jeu.
- `GUIDE_UTILISATEUR.md`: documentation locale complementaire.
- `DOCUMENTATION_DEVELOPPEUR.md`: documentation locale complementaire.

## Tests et validation

- Test cible du jeu: `./scripts/tests/test_jeux_python_cibles.sh --jeu TronGame`.
- Validation globale de la borne: `TEST_INSTALLATION_SIMULATION=1 TEST_DEPLOIEMENT_SIMULATION=1 BORNE_MODE_TEST=1 ./scripts/tests/lancer_suite.sh`.

## Maintenance et evolution

- Le projet dispose deja d une documentation locale utilisateur et developpeur a conserver synchronisee avec le README.
- Le lancement borne passe par le wrapper Python commun et doit rester compatible avec `python3`.
- Les dependances specifiques sont centralisees dans `requirements.txt`.
- Des tests locaux existent dans `tests/` et doivent etre maintenus a jour.
- Maintenir synchronises le README et la documentation locale complementaire du jeu.
- Le dossier `utils/` contient des scripts auxiliaires pour les ressources et ne doit pas etre confondu avec le point d entree principal.

## Liens associes

- [Ajout d un jeu](../../../docs/ajout_jeu.md).
- [Tests](../../../docs/tests.md).
- [Utilisateur](../../../docs/utilisateur.md).
- [GUIDE_UTILISATEUR.md](GUIDE_UTILISATEUR.md).
- [DOCUMENTATION_DEVELOPPEUR.md](DOCUMENTATION_DEVELOPPEUR.md).
