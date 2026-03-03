# Documentation ArcadeCare

## Objectif

Ce dossier `docs/` est la source unique de documentation du projet ArcadeCare.
Il couvre installation, architecture, exploitation, tests, deploiement, compatibilite, couts et rendu.

## Standard documentaire

Toutes les pages documentaires suivent la meme trame:

1. `Objectif`
2. `Procedure` ou `Commandes`
3. `Validation`
4. `Depannage` (si applicable)
5. `Liens associes`

## Regles de maintenance

- Les documents projet doivent rester dans `docs/`.
- Les seuls fichiers racine a conserver pour la gouvernance sont `AGENTS.md`, `consignes.md` et `README.md`.
- Ne pas dupliquer les consignes de `AGENTS.md` et `consignes.md` dans chaque page.
- Les `README.md` des jeux de `borne_arcade/projet/` sont generes automatiquement depuis `docs/modeles/README_jeu.md`.

## Parcours recommande

1. Lire `installation.md` puis executer `sudo ./bootstrap_borne.sh`.
2. Lire `architecture.md` pour la structure du depot.
3. Executer `./scripts/tests/lancer_suite.sh` pour verifier l etat global.
   Pour diagnostiquer uniquement la borne et les jeux:
   `./scripts/tests/test_borne_headless.sh` puis `./scripts/tests/test_jeux.sh`.
4. Pour une migration de versions, utiliser `python scripts/migration/workflow_migration.py lister-cibles --format json`
   puis suivre le workflow `appliquer -> preparer-ia -> qualite -> proposer-pr`.
5. Verifier les README de jeux avec `python3 scripts/docs/generer_readme_jeux.py --verifier`.
6. Lire `utilisateur.md` et `ajout_jeu.md` selon le besoin.
7. Lire `rendu.md` pour le bilan final.

## Validation

```bash
python3 scripts/docs/generer_readme_jeux.py --verifier
./scripts/tests/test_documentation.sh
./scripts/docs/generer_documentation.sh
```

## Liens associes

- Technique: `technique.md`
- Installation: `installation.md`
- Deploiement: `deploiement.md`
- Tests: `tests.md`
- Couts: `cost.md`
