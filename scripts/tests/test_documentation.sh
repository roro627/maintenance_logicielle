#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

#######################################
# Genere et verifie les artefacts documentaires.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_generation_documentation() {
  "${RACINE_PROJET}/scripts/docs/generer_documentation.sh"
  [[ -d "${RACINE_PROJET}/docs/build" ]] || arreter_sur_erreur "Repertoire docs/build absent"

  if [[ -f "${RACINE_PROJET}/docs/build/index.html" ]]; then
    return 0
  fi

  [[ -f "${RACINE_PROJET}/docs/build/index.md" ]] || arreter_sur_erreur "Index de documentation absent"
}

#######################################
# Point d entree test documentation.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
main() {
  charger_configuration_borne
  verifier_generation_documentation
  journaliser "Test documentation: OK"
}

main "$@"
