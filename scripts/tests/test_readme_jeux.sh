#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

#######################################
# Verifie que les README de jeux sont
# normalises et regenerables.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_readme_jeux() {
  "${COMMANDE_PYTHON}" "${RACINE_PROJET}/scripts/docs/generer_readme_jeux.py" --verifier
}

#######################################
# Verifie l absence de variantes
# `readme.md` en minuscule.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_absence_readme_minuscule() {
  local chemin_intrus=""
  chemin_intrus="$(find "${REPERTOIRE_BORNE}/projet" -type f -name 'readme.md' -print -quit)"
  [[ -z "${chemin_intrus}" ]] \
    || arreter_sur_erreur \
      "README de jeu non normalise detecte: ${chemin_intrus}" \
      "Renommez ce fichier en README.md ou relancez scripts/docs/generer_readme_jeux.py."
}

#######################################
# Point d entree du test README jeux.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
main() {
  charger_configuration_borne
  verifier_readme_jeux
  verifier_absence_readme_minuscule
  journaliser "Test README jeux: OK"
}

main "$@"
