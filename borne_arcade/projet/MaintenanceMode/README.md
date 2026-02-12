# MaintenanceMode - Integration borne

## Objectif

Jeu utilitaire cache pour l exploitation de la borne:
- diagnostic rapide,
- git pull,
- pipeline post-pull,
- mise a jour OS.
- reset prerequis (purge apt + nettoyage local pour retest a zero).
- journal temps reel des commandes.
- execution asynchrone pour garder l interface fluide.
- journal scrollable (PgUp/PgDn) avec auto-scroll activable (`A`) et retour bas (`Fin`).

## Deblocage

Le mode est verrouille au demarrage.
Dans le menu principal, une sequence secrete de boutons J1 permet de le debloquer.
Une fois debloque, le bouton J1B ouvre ce mode.

## Verrouillage

Depuis le mode maintenance, le bouton J1C verrouille la session et quitte.
Au redemarrage de la borne, le mode est de nouveau verrouille.

## Lancement

Le menu borne utilise le lanceur `borne_arcade/MaintenanceMode.sh`.
