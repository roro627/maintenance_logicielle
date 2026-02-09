# Procedure ajout de jeu

## Etapes
1. Creer `borne_arcade/projet/<nom_jeu>/`.
2. Ajouter les fichiers obligatoires:
   - `description.txt`
   - `bouton.txt`
   - `highscore`
3. Ajouter le code du jeu (Java/Python/Lua).
4. Creer le lanceur racine `borne_arcade/<nom_jeu>.sh`.
5. Rendre le script executable.
6. Lancer les tests d ajout de jeu.

## Exemple ReflexeFlash
```bash
mkdir -p borne_arcade/projet/ReflexeFlash
printf "ReflexeFlash\nJeu de reflexes.\n" > borne_arcade/projet/ReflexeFlash/description.txt
printf "Joystick:Monter/Descendre:A:Valider:B:Action:X:Pause:Y:Option:Z:Quitter\n" > borne_arcade/projet/ReflexeFlash/bouton.txt
touch borne_arcade/projet/ReflexeFlash/highscore
chmod +x borne_arcade/ReflexeFlash.sh
./scripts/tests/test_ajout_jeu.sh
```
