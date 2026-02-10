#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RACINE_PROJET="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [[ -f "${RACINE_PROJET}/scripts/lib/outils_communs.sh" ]]; then
  # shellcheck source=/dev/null
  source "${RACINE_PROJET}/scripts/lib/outils_communs.sh"
  charger_configuration_borne
else
  COMMANDE_PYTHON=python3
fi

#######################################
# Lance un jeu Python de la borne.
# Arguments:
#   $1: nom du dossier jeu
#   $2: script d entree relatif au dossier jeu
# Retour:
#   code du processus python
#######################################
main() {
  local nom_jeu="$1"
  local script_entree="$2"
  local mode_smoke_test="${BORNE_MODE_TEST_JEU:-0}"

  if [[ "${mode_smoke_test}" == "1" ]]; then
    [[ -d "${SCRIPT_DIR}/projet/${nom_jeu}" ]] || {
      echo "Dossier jeu introuvable: ${nom_jeu}" >&2
      return 1
    }
    if [[ -d "${SCRIPT_DIR}/projet/${nom_jeu}/${script_entree}" ]]; then
      [[ -f "${SCRIPT_DIR}/projet/${nom_jeu}/${script_entree}/__main__.py" ]] || {
        echo "Point d entree Python introuvable pour ${nom_jeu}: ${script_entree}/__main__.py" >&2
        return 1
      }
      return 0
    fi

    [[ -f "${SCRIPT_DIR}/projet/${nom_jeu}/${script_entree}" ]] || {
      echo "Point d entree Python introuvable pour ${nom_jeu}: ${script_entree}" >&2
      return 1
    }
    return 0
  fi

  cd "${SCRIPT_DIR}/projet/${nom_jeu}"
  touch highscore
  "${COMMANDE_PYTHON}" "${script_entree}"
}

main "$@"
