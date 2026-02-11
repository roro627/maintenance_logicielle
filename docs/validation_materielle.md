# Validation materielle borne

## Objectif

Tracer la validation sur borne physique (Raspberry Pi 3 Model B) avec une checklist
reproductible pour recette terrain.

## Procedure

Date validation: 2026-02-11
Borne: Raspberry Pi 3 Model B
Validateur: Equipe SAE maintenance logicielle

## Checklist

- [x] Demarrage automatique via borne.desktop
- [x] Navigation joystick J1 dans le menu
- [x] Lancement et retour menu pour chaque jeu
- [x] Son menu et son jeu
- [x] Ecriture et lecture highscore persistante
- [x] Resolution ecran 4:3 correcte
- [x] Bouton de sortie borne operationnel
- [x] Deblocage mode maintenance via sequence secrete
- [x] Reverrouillage mode maintenance via bouton J1C
- [x] Reverrouillage automatique du mode maintenance apres redemarrage

## Validation

```bash
./scripts/tests/test_materiel_checklist.sh
```

## Depannage

- Si autostart absent: relancer `./scripts/install/installer_borne.sh`.
- Si un bouton ne repond plus: verifier le mapping dans `bouton.txt` du jeu et le cablage.
- Si le son est absent: verifier les ressources audio et le volume ALSA.

## Liens associes

- Utilisateur: `utilisateur.md`
- Tests: `tests.md`
- Installation: `installation.md`
