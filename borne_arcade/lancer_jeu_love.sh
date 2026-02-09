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
  cd "${SCRIPT_DIR}/projet/${nom_jeu}"
  touch highscore
  love .
}

main "$@"
