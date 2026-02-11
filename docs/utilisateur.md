# Guide utilisateur

## Objectif

Expliquer l usage de la borne: navigation menu, lancement des jeux,
commandes principales et depannage rapide.

## Procedure d usage

### Navigation menu
- Joystick J1 haut/bas: selection du jeu.
- Bouton J1A: lancer le jeu.
- Bouton J1Z: quitter le menu (confirmation).

### En jeu
Chaque jeu decrit ses commandes dans `borne_arcade/projet/<jeu>/bouton.txt`.

### NeonSumo (resume)
- But: ejecter l adversaire hors de l arene.
- Match: BO3.
- B1 Dash, B2 Frein, B3 Bump, B4 Bouclier, B5 Taunt, B6 Ultime.

## Validation

- Le retour menu doit etre automatique a la fermeture d un jeu.
- Les highscores doivent etre persistants entre sessions.

## Depannage

- Jeu ne se lance pas: `./borne_arcade/compilation.sh`.
- Borne non lancee au demarrage: `./scripts/install/installer_borne.sh`.
- Son manquant: verifier les ressources audio du jeu.

## Liens associes

- Installation: `installation.md`
- Ajout jeu: `ajout_jeu.md`
- Tests: `tests.md`
