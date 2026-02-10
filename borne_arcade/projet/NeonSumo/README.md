# Neon Sumo (NeonSumo)

## Pitch
Neon Sumo est un duel arcade 1v1. Le but est d ejecter l adversaire hors de l arene.

## Lancement
Depuis la racine du projet:
```bash
./borne_arcade/NeonSumo.sh
```

## Controles borne
- Joystick J1: fleches
- Joystick J2: O (haut), L (bas), K (gauche), M (droite)
- B1: Dash (`F` J1, `Q` J2)
- B2: Frein (`G` J1, `S` J2)
- B3: Bump (`H` J1, `D` J2)
- B4: Bouclier (`R` J1, `A` J2)
- B5: Taunt (`T` J1, `Z` J2)
- B6: Ultime (`Y` J1, `E` J2)

## Boucle de jeu
- Ecran titre
- Manche avec compte a rebours
- BO3 (premier a 2)
- Ecran resultat / revanche
- Retour menu

## Configuration equilibrage
Le fichier `config_jeu.json` contient tous les reglages:
- physique (acceleration, friction, vitesse)
- cooldowns
- puissance des actions
- retrecissement de l arene
- durees de manche

## Sons
Les fichiers MP3 sont dans `assets/sons/`.
Ils sont initialises vides pour integration ulterieure des sons definitifs.

## Tests
```bash
python3 -m unittest borne_arcade/projet/NeonSumo/tests/test_logique.py
```

## Dependances
- Python 3
- pygame
