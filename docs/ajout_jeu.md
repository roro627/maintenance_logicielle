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
3. Declarer le jeu dans `config/matrice_tests_jeux.json` avec son `runtime`, son lanceur et sa `commande_test_cible`.
4. Ajouter l entree editoriale du jeu dans `config/readme_jeux.json`.
5. Ajouter le code du jeu (Java/Python/Lua).
6. Si le jeu Python a des dependances, ajouter `requirements.txt` dans `borne_arcade/projet/<nom_jeu>/`.
7. Creer le lanceur `borne_arcade/<nom_jeu>.sh`.
8. Generer le README local du jeu avec `python3 scripts/docs/generer_readme_jeux.py --jeu <nom_jeu>`.
9. Rendre le lanceur executable.

## Evolution d un jeu existant

Si vous modifiez le gameplay ou le rendu d un jeu deja integre (ex: menu titre NeonSumo):

1. Garder les reglages dans la configuration du jeu (`config_jeu.json`).
2. Ajouter/mettre a jour des tests unitaires pour la logique ajoutee.
3. Pour un mode attract/demo, verifier explicitement qu une elimination relance bien la demo sans bloquer l etat attract.
4. Mettre a jour `config/readme_jeux.json` si le resume, les commandes ou les notes de maintenance changent.
5. Regenerer le README du jeu avec `python3 scripts/docs/generer_readme_jeux.py --jeu <nom_jeu>`.
6. Mettre a jour `docs/utilisateur.md`, `docs/tests.md` et `docs/rendu.md` si le comportement visible ou la strategie de tests evolue.

## Commandes

```bash
./scripts/tests/test_ajout_jeu.sh
./scripts/tests/test_catalogue_jeux_complet.sh
./scripts/tests/test_jeux.sh
./scripts/tests/test_readme_jeux.sh
./scripts/tests/test_anti_regressions.sh
python3 scripts/docs/generer_readme_jeux.py --verifier
```

## Validation

```bash
python3 scripts/docs/generer_readme_jeux.py --jeu <nom_jeu>
./borne_arcade/compilation.sh
./scripts/tests/lancer_suite.sh
```

## Liens associes

- Utilisateur: `utilisateur.md`
- Installation: `installation.md`
- Tests: `tests.md`
