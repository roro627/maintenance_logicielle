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
- Collision passive entre capsules (push au contact)
- Hit feedback: flash ecran, freeze frame court, particules directionnelles sur dash/bump/ultime
- Arene neon vivante: glow anime + lignes electriques reactives aux impacts
- Systeme de style en direct: chaines d impacts, esquives proches, sauvetages du bord
- BO3 (premier a 2)
- Ecran resultat / revanche
- Retour menu

## Configuration equilibrage
Le fichier `config_jeu.json` contient tous les reglages:
- physique (acceleration, friction, vitesse)
- collision passive (`coefficient_rebond_collision`)
- cooldowns
- puissance des actions
- retrecissement de l arene
- durees de manche
- style (`style.*`)
- effets visuels arene (`effets_arene.*`)

## HUD lisibilite combat
- Icones B1/B3/B4 pres de chaque joueur:
  - B1 = Dash
  - B3 = Bump
  - B4 = Bouclier
- Chaque icone se remplit selon le cooldown restant.
- Panneaux style J1/J2:
  - score style cumule en direct
  - combo courant
  - dernier bonus recu (`CHAIN`, `ESQUIVE`, `SAVE`)

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
