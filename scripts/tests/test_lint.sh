#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

#######################################
# Execute les verifications de lint.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
executer_lint() {
  "${RACINE_PROJET}/scripts/lint/lancer_lint.sh"
}

#######################################
# Point d entree test lint.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
main() {
  charger_configuration_borne
  executer_lint
  journaliser "Test lint: OK"
}

main "$@"
