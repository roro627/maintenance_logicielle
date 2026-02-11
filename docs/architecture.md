# Architecture du depot

## Structure

- `borne_arcade/`: code actif de la borne et des jeux.
- `MG2D/`: miroir canonique externe (lecture seule).
- `docs/`: documentation MkDocs.
- `scripts/`: installation, deploiement, lint, tests, generation docs.
- `config/`: versions minimales et regles qualite.
- `src/`: point d entree logique architecture.
- `tests/`: point d entree logique des tests.
- `archives/`: anciennes versions centralisees.
- `build/`: artefacts de compilation Java.
- `.cache/`: cache technique (MG2D fallback).
- `logs/`: journaux de pipeline.

## Regles

1. Les artefacts generes vont dans `build/`, `site/`, `.cache/`, `logs/`.
2. Les fichiers legacy vont dans `archives/`.
3. MG2D n est pas modifie manuellement, uniquement resynchronise depuis upstream.
4. Les tests automatises doivent verifier cette organisation.

## Verification

```bash
./scripts/tests/test_architecture.sh
```
