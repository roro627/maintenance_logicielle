#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

#######################################
# Compile les tests unitaires Java et dependances minimales.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
compiler_tests_unitaires_java() {
  local classpath_mg2d
  classpath_mg2d="$(obtenir_classpath_mg2d)"
  (
    cd "${REPERTOIRE_BORNE}"
    local fichiers_a_compiler
    fichiers_a_compiler=(
      LigneHighScore.java
      HighScore.java
      ClavierBorneArcade.java
      AnalyseurConfigJeu.java
      tests/unit/TestUnitaireHighScore.java
      tests/unit/TestUnitaireClavierBorneArcade.java
      tests/unit/TestUnitaireAnalyseurConfigJeu.java
    )

    javac -cp ".:${classpath_mg2d}" "${fichiers_a_compiler[@]}"
  )
}

#######################################
# Execute les classes de test unitaires Java.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
executer_tests_unitaires_java() {
  local classpath_mg2d
  local classes
  classes=(
    TestUnitaireHighScore
    TestUnitaireClavierBorneArcade
    TestUnitaireAnalyseurConfigJeu
  )
  classpath_mg2d="$(obtenir_classpath_mg2d)"
  local classpath_java=".:${classpath_mg2d}:tests/unit"

  local classe
  for classe in "${classes[@]}"; do
    (
      cd "${REPERTOIRE_BORNE}"
      java -cp "${classpath_java}" "${classe}"
    )
  done
}

#######################################
# Point d entree test unitaires Java.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
main() {
  charger_configuration_borne
  compiler_tests_unitaires_java
  executer_tests_unitaires_java
  journaliser "Tests unitaires Java: OK"
}

main "$@"
