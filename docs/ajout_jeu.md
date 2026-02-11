# Procedure ajout de jeu

## Objectif

Ajouter un jeu dans la borne avec une integration conforme (fichiers obligatoires,
lanceur, tests et documentation).

## Procedure

1. Creer `borne_arcade/projet/<nom_jeu>/`.
2. Ajouter les fichiers obligatoires:
   - `description.txt`
   - `bouton.txt`
   - `highscore`
   - `photo_small.png`
3. Ajouter le code du jeu (Java/Python/Lua).
4. Creer le lanceur `borne_arcade/<nom_jeu>.sh`.
5. Rendre le lanceur executable.

## Commandes

```bash
./scripts/tests/test_ajout_jeu.sh
./scripts/tests/test_catalogue_jeux_complet.sh
./scripts/tests/test_jeux.sh
```

## Validation

```bash
./borne_arcade/compilation.sh
./scripts/tests/lancer_suite.sh
```

## Liens associes

- Utilisateur: `utilisateur.md`
- Installation: `installation.md`
- Tests: `tests.md`
