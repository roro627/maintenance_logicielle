# Guide utilisateur

## Objectif

Expliquer l usage de la borne: navigation menu, lancement des jeux,
commandes principales et depannage rapide.

## Procedure d usage

### Navigation menu
- Joystick J1 haut/bas: selection du jeu.
- Bouton J1A: lancer le jeu.
- Bouton J1Z: quitter le menu (confirmation).

### Mode maintenance cache
- Le mode est verrouille au lancement de la borne.
- Deblocage: sequence secrete configuree dans `borne_arcade/config/maintenance_mode.properties`.
- Ouverture apres debloquage: bouton configure (par defaut `J1B`).
- Reverrouillage manuel: dans `MaintenanceMode`, bouton `J1C` (touche `H`).
- Au redemarrage, le mode maintenance redevient verrouille automatiquement.
- Si le jeu maintenance est selectionne sans debloquage, son lancement est refuse.

### En jeu
Chaque jeu decrit ses commandes dans `borne_arcade/projet/<jeu>/bouton.txt`.

### NeonSumo (resume)
- But: ejecter l adversaire hors de l arene.
- Match: BO3.
- B1 Dash, B2 Frein, B3 Bump, B4 Bouclier, B5 Taunt, B6 Ultime.

### PianoTile (resume)
- Le jeu tente d utiliser `librosa` pour analyser le rythme.
- Si `librosa` est indisponible, un mode fallback genere des notes automatiquement
  pour garder le jeu jouable.

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
