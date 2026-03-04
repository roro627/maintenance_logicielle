# Guide utilisateur

## Objectif

Expliquer l usage de la borne: navigation menu, lancement des jeux,
commandes principales et depannage rapide.

## Procedure d usage

### Navigation menu

- Les jeux sont affiches par ordre alphabetique.
- Le panneau de droite suit toujours le jeu reellement selectionne et lance.
- Joystick J1 haut/bas: selection du jeu.
- Bouton J1A: lancer le jeu.
- Bouton J1Z: quitter le menu (confirmation).

### Mode maintenance cache

- Le mode est verrouille au lancement de la borne.
- Deblocage: sequence secrete configuree dans `borne_arcade/config/maintenance_mode.properties`.
- Ouverture apres debloquage: bouton configure (par defaut `J1B`).
- Une operation maintenance lancee (`F`) tourne en arriere-plan avec journal temps reel visible dans l ecran.
- `MaintenanceMode` s affiche en `1280x1024` sur la borne, sans barre de titre par defaut
  (`MODE_AFFICHAGE_BORNE=fenetre_sans_bordure` dans `borne_arcade/config/borne.env`).
- La cible de migration se choisit dans la combobox en haut de la colonne operations:
  `Tab` pour donner le focus,
  `Entree` pour ouvrir/fermer,
  `Haut`/`Bas` pour changer de cible,
  `Gauche`/`Droite` pour changer rapidement de cible quand la combobox est fermee.
- Le journal maintenance est scrollable: `PgUp`/`PgDn` (historique/recent), `Gauche`/`Droite` (horizontal), `A` pour activer/desactiver l auto-scroll, `Fin` pour revenir en bas, `Home` pour revenir au debut de ligne.
- Le journal est affiche de facon coherente: les lignes recentes restent en bas de la zone.
- Le diagnostic signale explicitement les pre-requis manquants (avec action recommandee) au lieu de planter.
- Une commande maintenance bloquee ou silencieuse est interrompue au timeout avec un message actionnable au lieu de rester en attente indefinie.
- Pendant une operation, la sortie est bloquee pour eviter les etats partiels.
- Workflow migration borne:
  1. `Recharger cibles migration`
  2. choisir la cible
  3. `Appliquer migration cible`
  4. `Lancer assistant IA migration`
  5. suivre la reponse IA en temps reel, puis laisser l IA/humain finaliser code, tests, docs et scripts
  6. `Relancer qualite complete`
  7. `Proposer PR migration`
- Sur un poste non Debian/Raspberry Pi, la detection reste consultable mais l application reelle d une migration apt est refusee avec un message clair.
- Option reset disponible: `Reset prerequis` (mode sur: purge des prerequis non-systeme seulement, sans autoremove global, + nettoyage local). Les paquets Python systeme (`python3`, `python3-venv`, `python3-pip`) sont explicitement proteges pour eviter toute casse de la VM/systeme.
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
