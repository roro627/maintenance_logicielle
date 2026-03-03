# CursedWare

## Objectif

CursedWare est une compilation de mini jeux inspires de WarioWare, jouable en borne avec une cadence rapide et un score global a battre.

## Runtime et lancement

- Runtime principal: `Lua avec LOVE2D`.
- Point d entree: `main.lua`.
- Lanceur borne: `borne_arcade/CursedWare.sh`.
- Lancement depuis la racine: `./borne_arcade/CursedWare.sh`.

## Commandes borne

| Commande | Action |
| --- | --- |
| Joystick | Naviguer ou se deplacer selon le mini jeu actif. |
| Bouton 2 | Executer l interaction principale du mini jeu. |
| Bouton 4 | Revenir ou quitter selon l ecran courant. |

## Fichiers importants

- `description.txt`: Description courte affichee dans le menu principal.
- `bouton.txt`: Mapping borne lu par le menu et les boites de description.
- `highscore`: Persistance locale du score.
- `photo_small.png`: Vignette affichee dans le catalogue de jeux.
- `tests/`: tests locaux du jeu.

## Tests et validation

- Test cible du jeu: `./scripts/tests/test_jeux_lua_cibles.sh --jeu CursedWare`.
- Validation globale de la borne: `TEST_INSTALLATION_SIMULATION=1 TEST_DEPLOIEMENT_SIMULATION=1 BORNE_MODE_TEST=1 ./scripts/tests/lancer_suite.sh`.

## Maintenance et evolution

- Le projet est base sur Lua et LOVE2D avec une organisation par mini jeux dans `minigames/`.
- Le lancement borne passe par le wrapper LOVE2D commun et doit rester compatible avec l execution depuis le dossier du jeu.
- Des tests locaux existent dans `tests/` et doivent etre maintenus a jour.
- La validation automatisee reste headless: syntaxe Lua et contrat des mini jeux sans lancer complet de LOVE2D.

## Liens associes

- [Ajout d un jeu](../../../docs/ajout_jeu.md).
- [Tests](../../../docs/tests.md).
- [Utilisateur](../../../docs/utilisateur.md).
