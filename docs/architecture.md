# Architecture du depot

## Objectif

Definir une structure stable et maintenable du depot, avec separation claire entre code actif,
documentation, automatisation, configuration, tests, archives et artefacts generes.

## Structure

- `borne_arcade/`: code actif de la borne et des jeux.
  Le menu graphique reste dans `Graphique.java`, mais la logique testable de navigation/lancement est isolee dans `ControleurMenuBorne.java` et `EtatMenuBorne.java`.
  Les abstractions de lancement borne vivent dans `LanceurJeuMenu.java` et `LanceurJeuProcessus.java`.
- `MG2D/`: miroir canonique externe (lecture seule).
- `docs/`: documentation MkDocs (source unique).
  `docs/modeles/` contient les templates documentaires versionnes, dont `README_jeu.md`.
- `scripts/`: installation, deploiement, lint, tests, generation docs.
  `scripts/docs/generer_readme_jeux.py` genere les README de jeux depuis un template unique.
  `scripts/migration/` porte le workflow CLI de migration versions.
- `config/`: versions minimales et regles qualite.
  `config/matrice_tests_jeux.json` reference chaque jeu du catalogue et sa commande de test cible obligatoire.
  `config/readme_jeux.json` centralise le contenu editorial des README de jeux.
  `config/cibles_migration.json` decrit les composants migrables et leurs commandes apt.
  `config/assistant_ia_migration.json` et `config/prompt_migration_ia.md` pilotent l etape IA `Codex/Ollama`.
- `archives/`: anciennes versions centralisees.
- `build/`: artefacts de compilation Java.
- `.cache/`: cache technique (ex: fallback classes MG2D).
  `.cache/maintenance_logicielle/etat_migration.json` conserve la session migration en cours hors git.
- `logs/`: journaux de pipeline.

## Regles

1. Les artefacts generes vont dans `build/`, `site/`, `.cache/` et `logs/`.
2. Les fichiers legacy vont dans `archives/`.
3. `MG2D/` n est jamais modifie localement; seulement resynchronise depuis upstream.
4. Les documents projet vivent dans `docs/`.
5. Les tests automatises doivent proteger ces regles.
6. Tout nouveau jeu dans `borne_arcade/projet/` doit etre ajoute a `config/matrice_tests_jeux.json` avec une `commande_test_cible`.
7. Tout nouveau jeu doit aussi etre decrit dans `config/readme_jeux.json` puis regenerer son `README.md` local.
8. Toute cible de migration versions doit etre declaree dans `config/cibles_migration.json`; le code ne doit pas dupliquer ces definitions.
9. Toute evolution de l etape IA de migration doit passer par `config/assistant_ia_migration.json` ou `config/prompt_migration_ia.md`, pas par des constantes dispersees.

## Validation

```bash
./scripts/tests/test_architecture.sh
```

## Liens associes

- Technique: `technique.md`
- Installation: `installation.md`
- Deploiement: `deploiement.md`
