# Architecture du depot

## Objectif

Definir une structure stable et maintenable du depot, avec separation claire entre code actif,
documentation, automatisation, configuration, tests, archives et artefacts generes.

## Structure

- `borne_arcade/`: code actif de la borne et des jeux.
- `MG2D/`: miroir canonique externe (lecture seule).
- `docs/`: documentation MkDocs (source unique).
- `scripts/`: installation, deploiement, lint, tests, generation docs.
- `config/`: versions minimales et regles qualite.
- `archives/`: anciennes versions centralisees.
- `build/`: artefacts de compilation Java.
- `.cache/`: cache technique (ex: fallback classes MG2D).
- `logs/`: journaux de pipeline.

## Regles

1. Les artefacts generes vont dans `build/`, `site/`, `.cache/` et `logs/`.
2. Les fichiers legacy vont dans `archives/`.
3. `MG2D/` n est jamais modifie localement; seulement resynchronise depuis upstream.
4. Les documents projet vivent dans `docs/`.
5. Les tests automatises doivent proteger ces regles.

## Validation

```bash
./scripts/tests/test_architecture.sh
```

## Liens associes

- Technique: `technique.md`
- Installation: `installation.md`
- Deploiement: `deploiement.md`
