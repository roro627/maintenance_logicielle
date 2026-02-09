# Strategie de tests

## Unitaires
- `HighScore`: lecture/ecriture de fichier.
- `ClavierBorneArcade`: mapping des touches.
- `AnalyseurConfigJeu`: parsing de `description.txt` et `bouton.txt`.
- `ReflexeFlash`: transitions d etat.

## Integration
- Presence des artefacts de jeux.
- Compilation Java des composants borne.
- Procedure d ajout de jeu.
- Anti regression chemins et deprecations Java (`test_anti_regressions.sh`).

## Systeme
- Installation automatisee.
- Deploiement automatise post `git pull`.
- Generation documentaire.

## Materiel
Validation finale sur borne physique avec la checklist:
```bash
./scripts/tests/test_materiel_checklist.sh
```
