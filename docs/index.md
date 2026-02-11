# Documentation Borne Arcade

## Objectif

Ce dossier `docs/` est la source unique de documentation du projet.
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

## Parcours recommande

1. Lire `installation.md` puis executer `sudo ./bootstrap_borne.sh`.
2. Lire `architecture.md` pour la structure du depot.
3. Executer `./scripts/tests/lancer_suite.sh` pour verifier l etat global.
4. Lire `utilisateur.md` et `ajout_jeu.md` selon le besoin.
5. Lire `rendu.md` pour le bilan final.

## Validation

```bash
./scripts/tests/test_documentation.sh
./scripts/docs/generer_documentation.sh
```

## Liens associes

- Technique: `technique.md`
- Installation: `installation.md`
- Deploiement: `deploiement.md`
- Tests: `tests.md`
- Couts: `cost.md`
