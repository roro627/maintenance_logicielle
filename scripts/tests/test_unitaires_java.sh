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
  (
    cd "${REPERTOIRE_BORNE}"
    javac -cp ".:${CHEMIN_MG2D}" \
      LigneHighScore.java \
      HighScore.java \
      ClavierBorneArcade.java \
      AnalyseurConfigJeu.java \
      projet/ReflexeFlash/EtatJeu.java \
      projet/ReflexeFlash/Jeu.java \
      tests/unit/TestUnitaireHighScore.java \
      tests/unit/TestUnitaireClavierBorneArcade.java \
      tests/unit/TestUnitaireAnalyseurConfigJeu.java \
      tests/unit/TestUnitaireEtatReflexeFlash.java
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
  local classes
  classes=(
    TestUnitaireHighScore
    TestUnitaireClavierBorneArcade
    TestUnitaireAnalyseurConfigJeu
    TestUnitaireEtatReflexeFlash
  )

  local classe
  for classe in "${classes[@]}"; do
    (
      cd "${REPERTOIRE_BORNE}"
      java -cp ".:${CHEMIN_MG2D}:tests/unit:projet/ReflexeFlash" "${classe}"
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
