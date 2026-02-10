# Procedure ajout de jeu

## Etapes

1. Creer `borne_arcade/projet/<nom_jeu>/`.
2. Ajouter les fichiers obligatoires:
   - `description.txt`
   - `bouton.txt`
   - `highscore`
3. Ajouter le code du jeu (Java/Python/Lua).
4. Ajouter `photo_small.png` pour l apercu menu.
5. Creer le lanceur racine `borne_arcade/<nom_jeu>.sh`.
6. Rendre le script executable.
7. Lancer les tests d ajout de jeu.

## Exemple Python complet: Neon Sumo (`NeonSumo`)

```bash
mkdir -p borne_arcade/projet/NeonSumo/assets/sons
printf "Neon Sumo\nDuel arcade 1v1.\n" > borne_arcade/projet/NeonSumo/description.txt
printf "Joystick:Dash:B2:B3:B4:B5:B6\n" > borne_arcade/projet/NeonSumo/bouton.txt
printf "AAA-0\n" > borne_arcade/projet/NeonSumo/highscore
cp borne_arcade/projet/Pong/photo_small.png borne_arcade/projet/NeonSumo/photo_small.png
touch borne_arcade/projet/NeonSumo/assets/sons/dash.mp3
cat > borne_arcade/NeonSumo.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail
"$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lancer_jeu_python.sh" "NeonSumo" "main.py"
SH
chmod +x borne_arcade/NeonSumo.sh
./scripts/tests/test_ajout_jeu.sh
```
