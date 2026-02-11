# Guide utilisateur

## Navigation menu
- Joystick J1 haut/bas: selection du jeu.
- Bouton J1A: lancer le jeu.
- Bouton J1Z: quitter le menu (confirmation).
- Le menu revient automatiquement apres fermeture d un jeu.

## Jeu Neon Sumo (NeonSumo)
- But: ejecter l adversaire hors de l arene.
- Match: BO3 (premier a 2 manches).
- Actions:
  - B1: Dash
  - B2: Frein
  - B3: Bump
  - B4: Bouclier
  - B5: Taunt
  - B6: Ultime

## Pendant un jeu
Chaque jeu documente ses commandes dans `borne_arcade/projet/<jeu>/bouton.txt`.

## Retour menu
Le script de lancement du jeu doit rendre la main au menu a la fin du processus.

## Depannage utilisateur
- Si un jeu ne se lance pas: relancer `./borne_arcade/compilation.sh`.
- Si la borne ne se lance pas au demarrage: relancer `./scripts/install/installer_borne.sh`.
- Si un son manque sur un jeu: verifier les ressources audio du dossier du jeu.
