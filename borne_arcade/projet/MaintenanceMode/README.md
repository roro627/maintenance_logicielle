# Maintenance Mode

## Objectif

Maintenance Mode est le jeu utilitaire cache de la borne pour le diagnostic, les operations git et le workflow de migration de versions.

## Runtime et lancement

- Runtime principal: `Python`.
- Point d entree: `main.py`.
- Lanceur borne: `borne_arcade/MaintenanceMode.sh`.
- Lancement depuis la racine: `./borne_arcade/MaintenanceMode.sh`.

## Commandes borne

| Commande | Action |
| --- | --- |
| Joystick | Naviguer dans les listes, les panneaux et les selections. |
| Bouton 1 | Executer l action selectionnee. |
| Bouton 2 | Declencher l action secondaire de l ecran courant. |
| Bouton 3 | Verrouiller puis quitter le mode maintenance. |

## Fichiers importants

- `description.txt`: Description courte affichee dans le menu principal.
- `bouton.txt`: Mapping borne lu par le menu et les boites de description.
- `highscore`: Persistance locale du score.
- `photo_small.png`: Vignette affichee dans le catalogue de jeux.
- `config_maintenance.json`: configuration supplementaire du jeu.
- `tests/`: tests locaux du jeu.

## Tests et validation

- Test cible du jeu: `./scripts/tests/test_jeux_python_cibles.sh --jeu MaintenanceMode`.
- Validation globale de la borne: `TEST_INSTALLATION_SIMULATION=1 TEST_DEPLOIEMENT_SIMULATION=1 BORNE_MODE_TEST=1 bash ./scripts/tests/lancer_suite.sh`.

## Maintenance et evolution

- Le mode maintenance integre le diagnostic borne, le git pull, le post pull, le reset des prerequis et l assistant de migration IA.
- Le lancement borne passe par le wrapper Python commun et doit rester compatible avec `python3`.
- Des tests locaux existent dans `tests/` et doivent etre maintenus a jour.
- Surveiller `config_maintenance.json` pour toute evolution de configuration.
- La configuration de l interface et des timeouts est centralisee dans `config_maintenance.json`.

## Liens associes

- [Ajout d un jeu](../../../docs/ajout_jeu.md).
- [Tests](../../../docs/tests.md).
- [Utilisateur](../../../docs/utilisateur.md).
