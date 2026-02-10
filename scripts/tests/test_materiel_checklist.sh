#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

#######################################
# Verifie la presence de la preuve de validation materielle.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_preuve_validation_materielle() {
  local fichier_preuve="${RACINE_PROJET}/docs/validation_materielle.md"
  [[ -f "${fichier_preuve}" ]] || arreter_sur_erreur "Preuve validation materielle absente: ${fichier_preuve}"

  rg -q "^Date validation: [0-9]{4}-[0-9]{2}-[0-9]{2}$" "${fichier_preuve}" \
    || arreter_sur_erreur "Date validation manquante dans ${fichier_preuve}"
  rg -q "^Borne: Raspberry Pi 3 Model B$" "${fichier_preuve}" \
    || arreter_sur_erreur "Borne cible incorrecte dans ${fichier_preuve}"
  rg -q "^Validateur: .+" "${fichier_preuve}" \
    || arreter_sur_erreur "Nom validateur manquant dans ${fichier_preuve}"
  rg -q "^- \\[x\\] Demarrage automatique via borne.desktop$" "${fichier_preuve}" \
    || arreter_sur_erreur "Checklist autostart non validee"
  rg -q "^- \\[x\\] Navigation joystick J1 dans le menu$" "${fichier_preuve}" \
    || arreter_sur_erreur "Checklist joystick menu non validee"
  rg -q "^- \\[x\\] Lancement et retour menu pour chaque jeu$" "${fichier_preuve}" \
    || arreter_sur_erreur "Checklist jeux non validee"
  rg -q "^- \\[x\\] Son menu et son jeu$" "${fichier_preuve}" \
    || arreter_sur_erreur "Checklist audio non validee"
  rg -q "^- \\[x\\] Ecriture et lecture highscore persistante$" "${fichier_preuve}" \
    || arreter_sur_erreur "Checklist highscore non validee"
  rg -q "^- \\[x\\] Resolution ecran 4:3 correcte$" "${fichier_preuve}" \
    || arreter_sur_erreur "Checklist resolution non validee"
  rg -q "^- \\[x\\] Bouton de sortie borne operationnel$" "${fichier_preuve}" \
    || arreter_sur_erreur "Checklist sortie non validee"
}

#######################################
# Verifie que la date de validation n est pas future.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_date_validation() {
  local fichier_preuve="${RACINE_PROJET}/docs/validation_materielle.md"
  local date_validation
  local date_jour

  date_validation="$(sed -n 's/^Date validation: //p' "${fichier_preuve}")"
  date_jour="$(date '+%Y-%m-%d')"

  if [[ "${date_validation}" > "${date_jour}" ]]; then
    arreter_sur_erreur "Date validation materielle future: ${date_validation}"
  fi
}

#######################################
# Point d entree validation materielle.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
main() {
  charger_configuration_borne
  verifier_preuve_validation_materielle
  verifier_date_validation
  journaliser "Validation materielle: OK"
}

main "$@"
