#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

#######################################
# Execute la sequence de mise a jour post pull.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
executer_pipeline_post_pull() {
  journaliser "Pipeline post-pull: installation"
  "${RACINE_PROJET}/scripts/install/installer_borne.sh"

  journaliser "Pipeline post-pull: compilation"
  "${REPERTOIRE_BORNE}/compilation.sh"

  journaliser "Pipeline post-pull: lint"
  "${RACINE_PROJET}/scripts/lint/lancer_lint.sh"

  journaliser "Pipeline post-pull: tests"
  EVITER_TEST_DEPLOIEMENT=1 "${RACINE_PROJET}/scripts/tests/lancer_suite.sh"

  journaliser "Pipeline post-pull: documentation"
  "${RACINE_PROJET}/scripts/docs/generer_documentation.sh"

  date '+%Y-%m-%d %H:%M:%S' > "${RACINE_PROJET}/.etat_derniere_maj"
}

#######################################
# Point d entree du script post pull.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
main() {
  charger_configuration_borne
  executer_pipeline_post_pull
  journaliser "Mise a jour post-pull terminee"
}

main "$@"
