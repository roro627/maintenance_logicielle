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
- Classpath MG2D robuste (`test_classpath_mg2d.sh`) :
  - utilise `MG2D.jar` si complet,
  - bascule automatique vers cache compile sinon,
  - verifie le chargement de `MG2D.geometrie.Dessin`,
  - verifie les ressources audio `sfd.ser` et `l3reorder.ser`.
- Qualite des messages d erreur (`test_messages_erreur.sh`) :
  - verifie la structure `ERREUR + ACTION RECOMMANDEE`,
  - controle `arreter_sur_erreur`,
  - controle les lanceurs Java/Python/Love en smoke test.
- Lint automatise (`test_lint.sh`) :
  - shellcheck sur scripts shell,
  - checkstyle sur Java maintenu,
  - pylint (erreurs) sur perimetre Python `config/pylint_repertoires.txt`.
- Conformite docstrings (`test_docstrings.sh`) :
  - verification AST des docstrings Python sur `scripts/` et `NeonSumo`,
  - verification des blocs `Arguments/Retour` des fonctions shell critiques.
- Suivi des couts (`test_couts.sh`) :
  - presence et structure de `cost.md`,
  - coherence de `docs/couts.md` avec la source de suivi.

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

## CI

La verification automatique est versionnee dans
`.github/workflows/qualite.yml` et execute la suite complete
`scripts/tests/lancer_suite.sh` en mode simulation.

## Catalogue complet des scripts de test

- `scripts/tests/test_installation.sh`: valide le script d installation, la venv et l autostart.
- `scripts/tests/test_versions_compatibilite.sh`: controle les versions minimales Java/Python/pip/pytest/mkdocs/pygame/Lua/Love.
- `scripts/tests/test_ajout_jeu.sh`: controle les fichiers minimaux requis pour chaque jeu.
- `scripts/tests/test_catalogue_jeux_complet.sh`: controle strict du catalogue (fichiers, executables, sources, config non vide).
- `scripts/tests/test_integrite_mg2d.sh`: garantit l integrite du miroir MG2D et la regle AGENTS.
- `scripts/tests/test_classpath_mg2d.sh`: verifie classes MG2D et ressources audio (`sfd.ser`, `l3reorder.ser`).
- `scripts/tests/test_messages_erreur.sh`: impose des erreurs lisibles (`ERREUR` + `ACTION RECOMMANDEE`).
- `scripts/tests/test_unitaires_java.sh`: execute les tests unitaires Java menu/config/highscore/clavier.
- `scripts/tests/test_lint.sh`: lance shellcheck/checkstyle/pylint.
- `scripts/tests/test_docstrings.sh`: verifie docstrings Python et blocs doc des fonctions shell critiques.
- `scripts/tests/test_anti_regressions.sh`: controle regressions connues (chemins figes, deprecations, garde audio).
- `scripts/tests/test_architecture.sh`: controle architecture cible, absence de legacy hors `archives/`, et isolation des artefacts dans `build/.cache`.
- `scripts/tests/test_couts.sh`: verifie la presence et la coherence de `cost.md` et `docs/couts.md`.
- `scripts/tests/test_jeux.sh`: compile la borne, lance smoke-tests de tous les jeux, et tests NeonSumo.
- `scripts/tests/test_documentation.sh`: valide la generation du site et la presence des pages critiques.
- `scripts/tests/test_deploiement.sh`: valide le pipeline post-pull, son verrou et ses logs.
- `scripts/tests/test_materiel_checklist.sh`: valide la preuve de recette materielle.
