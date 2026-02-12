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
- Une operation maintenance lancee (`F`) tourne en arriere-plan avec journal temps reel visible dans l ecran.
- Le journal maintenance est scrollable: `PgUp`/`PgDn` (historique/recent), `Gauche`/`Droite` (horizontal), `A` pour activer/desactiver l auto-scroll, `Fin` pour revenir en bas, `Home` pour revenir au debut de ligne.
- Le journal est affiche de facon coherente: les lignes recentes restent en bas de la zone.
- Le diagnostic signale explicitement les pre-requis manquants (avec action recommandee) au lieu de planter.
- Pendant une operation, la sortie est bloquee pour eviter les etats partiels.
- Option reset disponible: `Reset prerequis` (purge apt prerequis borne + nettoyage local) pour rejouer une installation depuis zero.
- Option rollback disponible: `Retour commit precedent` (retour `HEAD~1`) uniquement si le depot est propre.
- Les operations git (`Git pull`, rollback) affichent maintenant un message explicite si `git` est absent.
- Reverrouillage manuel: dans `MaintenanceMode`, bouton `J1C` (touche `H`).
- Au redemarrage, le mode maintenance redevient verrouille automatiquement.
- Si le jeu maintenance est selectionne sans debloquage, son lancement est refuse.

### En jeu
Chaque jeu decrit ses commandes dans `borne_arcade/projet/<jeu>/bouton.txt`.

### NeonSumo (resume)
- But: ejecter l adversaire hors de l arene.
- Match: BO3.
- B1 Dash, B2 Frein, B3 Bump, B4 Bouclier, B5 Taunt, B6 Ultime.
- Menu titre ameliore: theme neon anime, panneau controles lisible et rappel clair de l attract mode.
- Mode attract robuste: une collision/elimination en mode demo relance automatiquement une nouvelle manche IA sans sortir du mode attract.

### PianoTile (resume)
- Le jeu tente d utiliser `librosa` pour analyser le rythme.
- Si `librosa` est indisponible, un mode fallback genere des notes automatiquement
  pour garder le jeu jouable.
- Si l audio ne peut pas demarrer (ALSA/PulseAudio), la partie reste jouable avec
  un chronometrage de secours et un message actionnable est affiche en console.
- Pendant une partie PianoTile, `Echap` force le retour propre sans bloquer la borne.

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
