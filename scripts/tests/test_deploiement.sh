#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

#######################################
# Verifie le pipeline post pull en mode test.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_pipeline_post_pull() {
  BORNE_MODE_TEST=1 EVITER_TEST_DEPLOIEMENT=1 "${RACINE_PROJET}/scripts/deploiement/post_pull_update.sh"
  [[ -f "${RACINE_PROJET}/.etat_derniere_maj" ]] || arreter_sur_erreur "Marqueur .etat_derniere_maj absent"
}

#######################################
# Point d entree test deploiement.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
main() {
  charger_configuration_borne
  verifier_pipeline_post_pull
  journaliser "Test deploiement: OK"
}

main "$@"
