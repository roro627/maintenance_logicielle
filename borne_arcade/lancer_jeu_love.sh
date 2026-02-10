#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

#######################################
# Lance un jeu Lua via LÖVE.
# Arguments:
#   $1: nom du dossier jeu
# Retour:
#   code du processus love
#######################################
main() {
  local nom_jeu="$1"
  local mode_smoke_test="${BORNE_MODE_TEST_JEU:-0}"

  if [[ "${mode_smoke_test}" == "1" ]]; then
    [[ -d "${SCRIPT_DIR}/projet/${nom_jeu}" ]] || {
      echo "Dossier jeu introuvable: ${nom_jeu}" >&2
      return 1
    }
    [[ -f "${SCRIPT_DIR}/projet/${nom_jeu}/main.lua" ]] || {
      echo "Fichier main.lua introuvable pour ${nom_jeu}" >&2
      return 1
    }
    return 0
  fi

  cd "${SCRIPT_DIR}/projet/${nom_jeu}"
  touch highscore
  love .
}

main "$@"
