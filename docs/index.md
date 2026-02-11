# Documentation Borne Arcade

Cette documentation est la source de verite pour:
- architecture technique,
- installation sur Linux et Raspberry Pi OS,
- exploitation utilisateur,
- procedure d ajout de jeu,
- deploiement automatique apres `git pull`,
- strategie de tests et validation materielle,
- compatibilite des dependances,
- verification CI automatisee,
- suivi des couts et rendu final.

## Contraintes non negociables
- Aucune modification sous `MG2D/` (miroir de `https://github.com/synave/MG2D`).
- Tous les scripts, commentaires et documentations modifies sont en francais.
- Toute correction doit ajouter un test anti regression.
- Les parametres ajustables sont centralises dans des fichiers de configuration.
- La validation materielle doit etre tracee dans `docs/validation_materielle.md`.

## Parcours recommande

1. Lire `installation.md` pour preparer l environnement.
2. Lire `architecture.md` pour comprendre l organisation des dossiers.
3. Executer `./scripts/tests/lancer_suite.sh` pour verifier l etat global.
4. Lire `utilisateur.md` pour l exploitation de la borne.
5. Lire `ajout_jeu.md` avant toute integration de nouveau jeu.
6. Consulter `ARCHITECTURE.md` pour les regles de rangement detaillees.
7. Consulter `rendu.md` pour le bilan final de conformite.
