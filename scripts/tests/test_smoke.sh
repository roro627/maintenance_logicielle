#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

#######################################
# Verifie les versions minimales des
# runtimes et outils critiques.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_versions_critiques() {
  "${SCRIPT_DIR}/test_versions_compatibilite.sh"
}

#######################################
# Verifie l integrite de MG2D.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_integrite_mg2d() {
  "${SCRIPT_DIR}/test_integrite_mg2d.sh"
}

#######################################
# Verifie le classpath MG2D (jar/cache)
# et les ressources audio critiques.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_classpath_mg2d() {
  "${SCRIPT_DIR}/test_classpath_mg2d.sh"
}

#######################################
# Execute les tests unitaires Java
# critiques du menu borne.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_tests_unitaires_java() {
  "${SCRIPT_DIR}/test_unitaires_java.sh"
}

#######################################
# Execute les tests unitaires Python
# critiques du jeu NeonSumo.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_tests_unitaires_neon_sumo() {
  (
    cd "${RACINE_PROJET}"
    "${COMMANDE_PYTHON}" -m unittest borne_arcade/projet/NeonSumo/tests/test_logique.py
  )
}

#######################################
# Point d entree du test smoke.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
main() {
  charger_configuration_borne
  verifier_versions_critiques
  verifier_integrite_mg2d
  verifier_classpath_mg2d
  verifier_tests_unitaires_java
  verifier_tests_unitaires_neon_sumo
  journaliser "Test smoke: OK"
}

main "$@"
