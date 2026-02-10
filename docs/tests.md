# Strategie de tests

## Unitaires

- `HighScore`: lecture/ecriture de fichier.
- `ClavierBorneArcade`: mapping des touches.
- `AnalyseurConfigJeu`: parsing de `description.txt` et `bouton.txt`.
- `Neon Sumo`: collisions, sortie arene, cooldowns, jauge ultime.

## Integration

- Presence des artefacts de jeux.
- Validation stricte du catalogue jeux (`test_catalogue_jeux_complet.sh`):
  - `description.txt`, `bouton.txt`, `highscore`, `photo_small.png`,
  - lanceur executable,
  - configuration non vide,
  - presence de sources.
- Compilation et validation syntaxique de tous les jeux.
- Smoke test de lancement pour tous les jeux (`BORNE_MODE_TEST_JEU=1`).
- Procedure d ajout de jeu.
- Anti regression chemins et deprecations Java (`test_anti_regressions.sh`).
- Integrite MG2D (`test_integrite_mg2d.sh`) :
  - regle AGENTS.md presente,
  - absence de `.class` dans `MG2D/`,
  - artefacts essentiels MG2D presents.
- Lint automatise (`test_lint.sh`) :
  - shellcheck sur scripts shell,
  - checkstyle sur Java maintenu,
  - pylint (erreurs) sur perimetre Python `config/pylint_repertoires.txt`.

## Systeme

- Installation automatisee.
- Deploiement automatise post `git pull`.
- Generation documentaire.
- Compatibilite versions outils/runtime (`test_versions_compatibilite.sh`).

## Materiel

Validation finale sur borne physique avec preuve obligatoire:

```bash
./scripts/tests/test_materiel_checklist.sh
```

Le fichier de preuve associe est `docs/validation_materielle.md`.
