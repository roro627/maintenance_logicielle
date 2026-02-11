# Procedure ajout de jeu

## Etapes

1. Creer `borne_arcade/projet/<nom_jeu>/`.
2. Ajouter les fichiers obligatoires:
   - `description.txt`
   - `bouton.txt`
   - `highscore`
   - `photo_small.png`
3. Ajouter le code du jeu (Java/Python/Lua).
4. Creer le lanceur racine `borne_arcade/<nom_jeu>.sh`.
5. Rendre le script executable.
6. Verifier compilation et smoke-test.
7. Lancer la suite de tests d integration.

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
./scripts/tests/test_catalogue_jeux_complet.sh
./scripts/tests/test_jeux.sh
```

## Controle final avant merge

```bash
./borne_arcade/compilation.sh
./scripts/tests/lancer_suite.sh
```
