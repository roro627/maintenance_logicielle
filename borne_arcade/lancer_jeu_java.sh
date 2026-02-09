#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RACINE_PROJET="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [[ -f "${RACINE_PROJET}/scripts/lib/outils_communs.sh" ]]; then
  # shellcheck source=/dev/null
  source "${RACINE_PROJET}/scripts/lib/outils_communs.sh"
  charger_configuration_borne
else
  CHEMIN_MG2D="${RACINE_PROJET}/MG2D"
  RESOLUTION_X=1280
  RESOLUTION_Y=1024
fi

#######################################
# Lance un jeu Java de la borne.
# Arguments:
#   $1: nom du dossier jeu
#   $2: classe principale
#   $3..n: options java supplementaires
# Retour:
#   code du processus java
#######################################
main() {
  local nom_jeu="$1"
  local classe_principale="$2"
  shift 2
  local options_java=("$@")

  local resolution_x="${RESOLUTION_X:-1280}"
  local resolution_y="${RESOLUTION_Y:-1024}"

  if command -v xdotool >/dev/null 2>&1; then
    xdotool mousemove "${resolution_x}" "${resolution_y}" || true
  fi

  cd "${SCRIPT_DIR}/projet/${nom_jeu}"
  touch highscore
  java "${options_java[@]}" -cp ".:../..:${CHEMIN_MG2D}" "${classe_principale}"
}

main "$@"
