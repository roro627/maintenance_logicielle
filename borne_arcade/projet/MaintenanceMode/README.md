# MaintenanceMode - Integration borne

## Objectif

Jeu utilitaire cache pour l exploitation de la borne:
- diagnostic rapide,
- git pull,
- pipeline post-pull,
- mise a jour OS.
- reset prerequis (mode sur: purge apt limitee aux paquets non-systeme + nettoyage local pour retest a zero).
- retour commit precedent (rollback git controle vers `HEAD~1` si depot propre).
- journal temps reel des commandes.
- execution asynchrone pour garder l interface fluide.
- journal scrollable verticalement (`PgUp`/`PgDn`) et horizontalement (`Gauche`/`Droite`).
- auto-scroll vertical activable (`A`), retour bas (`Fin`) et retour debut de ligne (`Home`).
- affichage coherent du journal: lignes recentes en bas et indicateurs de scroll synchronises.
- diagnostic tolerant aux dependances manquantes avec messages actionnables (sans crash).
- operations git durcies: verification explicite de la presence de `git` et message actionnable si indisponible.

## Deblocage

Le mode est verrouille au demarrage.
Dans le menu principal, une sequence secrete de boutons J1 permet de le debloquer.
Une fois debloque, le bouton J1B ouvre ce mode.

## Verrouillage

Depuis le mode maintenance, le bouton J1C verrouille la session et quitte.
Au redemarrage de la borne, le mode est de nouveau verrouille.

## Lancement

Le menu borne utilise le lanceur `borne_arcade/MaintenanceMode.sh`.
