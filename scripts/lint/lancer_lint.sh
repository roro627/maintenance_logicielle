#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

#######################################
# Execute shellcheck sur les scripts maintenus.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
executer_shellcheck() {
  if ! command -v shellcheck >/dev/null 2>&1; then
    journaliser "shellcheck absent: etape ignoree"
    return 0
  fi

  local fichiers
  mapfile -t fichiers < <(
    {
      find "${RACINE_PROJET}/scripts" -type f -name '*.sh'
      printf '%s\n' \
        "${RACINE_PROJET}/.githooks/post-merge" \
        "${REPERTOIRE_BORNE}/compilation.sh" \
        "${REPERTOIRE_BORNE}/clean.sh" \
        "${REPERTOIRE_BORNE}/lancerBorne.sh" \
        "${REPERTOIRE_BORNE}/ReflexeFlash.sh"
    } | sort -u
  )

  if [[ "${#fichiers[@]}" -eq 0 ]]; then
    journaliser "Aucun script shell a verifier"
    return 0
  fi

  journaliser "Execution shellcheck"
  shellcheck "${fichiers[@]}"
}

#######################################
# Execute checkstyle sur les classes Java maintenues.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
executer_checkstyle() {
  if ! command -v checkstyle >/dev/null 2>&1; then
    journaliser "checkstyle absent: etape ignoree"
    return 0
  fi

  local fichiers_java
  mapfile -t fichiers_java < <(
    printf '%s\n' \
      "${REPERTOIRE_BORNE}/Main.java" \
      "${REPERTOIRE_BORNE}/ConstantesMenu.java" \
      "${REPERTOIRE_BORNE}/AnalyseurConfigJeu.java" \
      "${REPERTOIRE_BORNE}/Graphique.java" \
      "${REPERTOIRE_BORNE}/Bouton.java" \
      "${REPERTOIRE_BORNE}/Pointeur.java" \
      "${REPERTOIRE_BORNE}/BoiteDescription.java" \
      "${REPERTOIRE_BORNE}/projet/ReflexeFlash/Main.java" \
      "${REPERTOIRE_BORNE}/projet/ReflexeFlash/Jeu.java" \
      "${REPERTOIRE_BORNE}/projet/ReflexeFlash/EtatJeu.java" \
      "${REPERTOIRE_BORNE}/tests/unit/TestUnitaireHighScore.java" \
      "${REPERTOIRE_BORNE}/tests/unit/TestUnitaireClavierBorneArcade.java" \
      "${REPERTOIRE_BORNE}/tests/unit/TestUnitaireAnalyseurConfigJeu.java" \
      "${REPERTOIRE_BORNE}/tests/unit/TestUnitaireEtatReflexeFlash.java"
  )

  journaliser "Execution checkstyle"
  checkstyle -c "${RACINE_PROJET}/config/checkstyle.xml" "${fichiers_java[@]}"
}

#######################################
# Execute pylint sur les scripts python maintenus.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
executer_pylint() {
  if ! command -v pylint >/dev/null 2>&1; then
    journaliser "pylint absent: etape ignoree"
    return 0
  fi

  local fichiers_py
  mapfile -t fichiers_py < <(find "${RACINE_PROJET}/scripts" -type f -name '*.py' | sort)

  if [[ "${#fichiers_py[@]}" -eq 0 ]]; then
    journaliser "Aucun fichier python cible pour pylint"
    return 0
  fi

  journaliser "Execution pylint"
  pylint --rcfile="${RACINE_PROJET}/.pylintrc" "${fichiers_py[@]}"
}

#######################################
# Point d entree lint.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
main() {
  charger_configuration_borne
  executer_shellcheck
  executer_checkstyle
  executer_pylint
  journaliser "Lint termine"
}

main "$@"
