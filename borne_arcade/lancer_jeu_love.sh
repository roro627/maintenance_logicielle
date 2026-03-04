#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RACINE_PROJET="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [[ -f "${RACINE_PROJET}/scripts/lib/outils_communs.sh" ]]; then
  # shellcheck source=/dev/null
  source "${RACINE_PROJET}/scripts/lib/outils_communs.sh"
  charger_configuration_borne
else
  RESOLUTION_X=1280
  RESOLUTION_Y=1024
  MODE_AFFICHAGE_BORNE=fenetre_sans_bordure
  POSITION_FENETRE_X=0
  POSITION_FENETRE_Y=0
fi

#######################################
# Lance un jeu Lua via LOVE.
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
      echo "ERREUR: Dossier jeu introuvable: ${nom_jeu}" >&2
      echo "ACTION RECOMMANDEE: verifiez le nom du jeu et la presence du dossier borne_arcade/projet/${nom_jeu}." >&2
      return 1
    }
    [[ -f "${SCRIPT_DIR}/projet/${nom_jeu}/main.lua" ]] || {
      echo "ERREUR: Fichier main.lua introuvable pour ${nom_jeu}" >&2
      echo "ACTION RECOMMANDEE: ajoutez un point d entree main.lua dans borne_arcade/projet/${nom_jeu}/." >&2
      return 1
    }
    return 0
  fi

  if declare -F preparer_environnement_affichage_sdl >/dev/null 2>&1; then
    preparer_environnement_affichage_sdl
  else
    export BORNE_RESOLUTION_X="${RESOLUTION_X:-1280}"
    export BORNE_RESOLUTION_Y="${RESOLUTION_Y:-1024}"
    export BORNE_MODE_AFFICHAGE="${MODE_AFFICHAGE_BORNE:-fenetre_sans_bordure}"
    export BORNE_POSITION_FENETRE_X="${POSITION_FENETRE_X:-0}"
    export BORNE_POSITION_FENETRE_Y="${POSITION_FENETRE_Y:-0}"
    export SDL_VIDEO_WINDOW_POS="${BORNE_POSITION_FENETRE_X},${BORNE_POSITION_FENETRE_Y}"
    export SDL_VIDEO_CENTERED=0
  fi

  cd "${SCRIPT_DIR}/projet/${nom_jeu}"
  touch highscore
  love .
}

main "$@"
