#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

#######################################
# Execute toutes les suites de tests automatiques.
# Arguments:
#   aucun
# Retour:
#   0 si toutes les suites passent
#######################################
executer_suites_principales() {
  local scripts_tests=(
    "test_installation.sh"
    "test_versions_compatibilite.sh"
    "test_ajout_jeu.sh"
    "test_catalogue_jeux_complet.sh"
    "test_integrite_mg2d.sh"
    "test_classpath_mg2d.sh"
    "test_messages_erreur.sh"
    "test_unitaires_java.sh"
    "test_smoke.sh"
    "test_lint.sh"
    "test_docstrings.sh"
    "test_anti_regressions.sh"
    "test_architecture.sh"
    "test_couts.sh"
    "test_jeux.sh"
    "test_readme_jeux.sh"
    "test_documentation.sh"
  )
  local script_test=""

  for script_test in "${scripts_tests[@]}"; do
    executer_script_shell "${SCRIPT_DIR}/${script_test}"
  done
}

#######################################
# Point d entree de la suite complete.
# Arguments:
#   aucun
# Retour:
#   0 si toutes les suites passent
#######################################
main() {
  executer_suites_principales
  if [[ "${EVITER_TEST_DEPLOIEMENT:-0}" != "1" ]]; then
    executer_script_shell "${SCRIPT_DIR}/test_deploiement.sh"
  fi

  executer_script_shell "${SCRIPT_DIR}/test_materiel_checklist.sh"
}

main "$@"
