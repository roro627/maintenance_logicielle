#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

#######################################
# Execute toutes les suites de tests automatiques.
# Arguments:
#   aucun
# Retour:
#   0 si toutes les suites passent
#######################################
main() {
  "${SCRIPT_DIR}/test_installation.sh"
  "${SCRIPT_DIR}/test_versions_compatibilite.sh"
  "${SCRIPT_DIR}/test_ajout_jeu.sh"
  "${SCRIPT_DIR}/test_catalogue_jeux_complet.sh"
  "${SCRIPT_DIR}/test_integrite_mg2d.sh"
  "${SCRIPT_DIR}/test_classpath_mg2d.sh"
  "${SCRIPT_DIR}/test_messages_erreur.sh"
  "${SCRIPT_DIR}/test_unitaires_java.sh"
  "${SCRIPT_DIR}/test_smoke.sh"
  "${SCRIPT_DIR}/test_lint.sh"
  "${SCRIPT_DIR}/test_docstrings.sh"
  "${SCRIPT_DIR}/test_anti_regressions.sh"
  "${SCRIPT_DIR}/test_architecture.sh"
  "${SCRIPT_DIR}/test_couts.sh"
  "${SCRIPT_DIR}/test_jeux.sh"
  "${SCRIPT_DIR}/test_documentation.sh"

  if [[ "${EVITER_TEST_DEPLOIEMENT:-0}" != "1" ]]; then
    "${SCRIPT_DIR}/test_deploiement.sh"
  fi

  "${SCRIPT_DIR}/test_materiel_checklist.sh"
}

main "$@"
