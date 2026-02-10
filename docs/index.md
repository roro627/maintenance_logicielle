# Documentation Borne Arcade

Cette documentation est la source de verite pour:
- architecture technique,
- installation sur Linux et Raspberry Pi OS,
- exploitation utilisateur,
- procedure d ajout de jeu,
- deploiement automatique apres `git pull`,
- strategie de tests et validation materielle,
- compatibilite des dependances.

## Contraintes non negociables
- Aucune modification sous `MG2D/` (miroir de `https://github.com/synave/MG2D`).
- Tous les scripts, commentaires et documentations modifies sont en francais.
- Toute correction doit ajouter un test anti regression.
- Les parametres ajustables sont centralises dans des fichiers de configuration.
- La validation materielle doit etre tracee dans `docs/validation_materielle.md`.
