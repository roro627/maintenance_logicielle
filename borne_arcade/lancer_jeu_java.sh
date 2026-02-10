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
# Retourne le classpath MG2D optimal
# (jar valide sinon cache compile).
# Arguments:
#   aucun
# Retour:
#   ecrit le classpath sur stdout
#######################################
obtenir_classpath_mg2d_lancement() {
  if declare -F obtenir_classpath_mg2d >/dev/null 2>&1; then
    obtenir_classpath_mg2d
    return 0
  fi
  echo "${CHEMIN_MG2D}"
}

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
  local mode_smoke_test="${BORNE_MODE_TEST_JEU:-0}"
  local classpath_mg2d

  local resolution_x="${RESOLUTION_X:-1280}"
  local resolution_y="${RESOLUTION_Y:-1024}"

  if [[ "${mode_smoke_test}" == "1" ]]; then
    [[ -d "${SCRIPT_DIR}/projet/${nom_jeu}" ]] || {
      echo "Dossier jeu introuvable: ${nom_jeu}" >&2
      return 1
    }
    if [[ ! -f "${SCRIPT_DIR}/projet/${nom_jeu}/${classe_principale}.java" ]] \
      && [[ ! -f "${SCRIPT_DIR}/projet/${nom_jeu}/${classe_principale}.class" ]]; then
      echo "Classe principale introuvable pour ${nom_jeu}: ${classe_principale}" >&2
      return 1
    fi
    return 0
  fi

  if command -v xdotool >/dev/null 2>&1; then
    xdotool mousemove "${resolution_x}" "${resolution_y}" || true
  fi

  classpath_mg2d="$(obtenir_classpath_mg2d_lancement)"
  cd "${SCRIPT_DIR}/projet/${nom_jeu}"
  touch highscore
  java "${options_java[@]}" -cp ".:../..:${classpath_mg2d}" "${classe_principale}"
}

main "$@"
