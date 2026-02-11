# Architecture du depot

## Objectif

Cette convention organise le depot pour separer clairement:
- le code actif,
- la documentation,
- l automatisation,
- la configuration,
- les tests,
- les archives historiques.

## Structure cible

- `src/`: point d entree logique du code actif (documentation d architecture).
- `docs/`: sources MkDocs (documentation fonctionnelle et technique).
- `scripts/`: outillage d installation/deploiement/lint/tests/docs.
- `config/`: regles de qualite et versions minimales.
- `tests/`: point d entree logique des tests (documentation de navigation).
- `archives/`: anciennes versions et fichiers legacy deplaces.
- `build/`: artefacts de compilation (classes Java generees).
- `.cache/`: cache technique (ex: classes MG2D fallback).
- `logs/`: traces d execution (pipeline post-pull).

## Regles de rangement

1. Ne pas laisser de fichier legacy dans `borne_arcade/` ou `scripts/`.
2. Tout ancien fichier de travail doit aller dans `archives/` avec contexte.
3. Les artefacts generes doivent rester dans `build/`, `.cache/`, `logs/` ou `site/`.
4. Les tests automatiques doivent proteger ces regles.

## Exception MG2D

Le dossier `MG2D/` reste un miroir externe canonique et n est pas repackage
dans `src/` pour respecter l integrite imposee par `AGENTS.md`.
