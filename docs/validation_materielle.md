# Validation materielle borne

## Objectif

Tracer la validation sur borne physique (Raspberry Pi 3 Model B) avec une checklist
reproductible pour recette terrain.

## Procedure

Date validation: 2026-02-11
Borne: Raspberry Pi 3 Model B
Validateur: Equipe SAE ArcadeCare

## Checklist

- [x] Demarrage automatique via borne.desktop
- [x] Navigation joystick J1 dans le menu
- [x] Boutons J1 B1..B6 fonctionnels (mapping nominal et fallback numerique 1..6)
- [x] Catalogue trie alphabetiquement et panneau droit synchronise avec la selection
- [x] Lancement et retour menu pour chaque jeu
- [x] Son menu et son jeu
- [x] Ecriture et lecture highscore persistante
- [x] Resolution ecran 1280x1024 correcte
- [x] Jeux SDL critiques affiches sans barre de titre ou en plein ecran selon `borne.env`
- [x] `MaintenanceMode` occupe correctement la hauteur `1024` sans zone morte majeure
- [x] Bouton de sortie borne operationnel
- [x] Deblocage mode maintenance via sequence secrete
- [x] Reverrouillage mode maintenance via bouton J1C
- [x] Reverrouillage automatique du mode maintenance apres redemarrage

## Validation

```bash
./scripts/tests/test_materiel_checklist.sh
```

## Depannage

- Si autostart absent: relancer `sudo bash ./bootstrap_borne.sh` pour resynchroniser `~/.config/autostart/borne.desktop` avec le chemin reel du depot.
- Si un bouton ne repond plus: verifier le mapping dans `bouton.txt` du jeu et le cablage.
- Si seuls les boutons J1 ne repondent pas: verifier le layout `borne`; en secours, utiliser `1..6` (ou pavé numerique) pour B1..B6.
- Si le son est absent: verifier les ressources audio et le volume ALSA.

## Liens associes

- Utilisateur: `utilisateur.md`
- Tests: `tests.md`
- Installation: `installation.md`
