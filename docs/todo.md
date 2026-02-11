# Suivi TODO

## Objectif

Tracer l etat des demandes prioritaires du lot en cours.

## Etat

- [x] Gerer proprement les erreurs de permissions build au lancement/compilation.
- [x] Ajouter un mode maintenance deverrouillable par sequence secrete avec actions d exploitation.
- [x] Optimiser la fluidite du menu principal.
- [x] Corriger le lancement de PianoTile.

## Validation

```bash
TEST_INSTALLATION_SIMULATION=1 TEST_DEPLOIEMENT_SIMULATION=1 BORNE_MODE_TEST=1 ./scripts/tests/lancer_suite.sh
```

## Liens associes

- Technique: `technique.md`
- Tests: `tests.md`
