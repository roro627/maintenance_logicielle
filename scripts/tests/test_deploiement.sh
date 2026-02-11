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
  if [[ "${TEST_DEPLOIEMENT_SIMULATION:-0}" == "1" ]]; then
    BORNE_MODE_TEST=1 EVITER_TEST_DEPLOIEMENT=1 "${RACINE_PROJET}/scripts/deploiement/post_pull_update.sh"
  else
    EVITER_TEST_DEPLOIEMENT=1 "${RACINE_PROJET}/scripts/deploiement/post_pull_update.sh"
  fi
  [[ -f "${RACINE_PROJET}/.etat_derniere_maj" ]] || arreter_sur_erreur "Marqueur .etat_derniere_maj absent"
  [[ ! -f "${RACINE_PROJET}/.post_pull.lock" ]] || arreter_sur_erreur "Verrou .post_pull.lock non libere apres pipeline"
  find "${RACINE_PROJET}/logs" -maxdepth 1 -type f -name 'post_pull_update_*.log' | grep -q . \
    || arreter_sur_erreur "Journal post-pull absent dans logs/"
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
