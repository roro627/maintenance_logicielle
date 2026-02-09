#!/usr/bin/env bash
set -euo pipefail

#######################################
# Affiche la checklist de validation materielle.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
main() {
  cat <<'TXT'
Checklist validation materielle (borne physique):
- Demarrage automatique via borne.desktop
- Navigation joystick J1 dans le menu
- Lancement et retour menu pour chaque jeu
- Son menu + son jeu
- Ecriture/lecture highscore persistante
- Resolution ecran correcte (4:3)
- Bouton de sortie borne operationnel
TXT

  if [[ "${VALIDATION_MATERIELLE_OK:-0}" == "1" ]]; then
    echo "Validation materielle declaree OK"
  else
    echo "Validation materielle non automatisable ici: executer sur borne physique"
  fi
}

main "$@"
