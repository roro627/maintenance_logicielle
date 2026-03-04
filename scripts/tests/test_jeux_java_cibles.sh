#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

JEU_CIBLE="${1:-}"
if [[ "${JEU_CIBLE:-}" == "--jeu" ]]; then
  JEU_CIBLE="${2:-}"
fi

DOSSIER_CLASSES_JEUX_CIBLES=""

#######################################
# Retourne la liste des jeux Java avec
# tests cibles pour cette suite.
# Arguments:
#   aucun
# Retour:
#   ecrit la liste sur stdout
#######################################
lister_jeux_java_cibles() {
  printf '%s\n' \
    "Columns" \
    "DinoRail" \
    "InitialDrift" \
    "JavaSpace" \
    "Kowasu_Renga" \
    "Minesweeper" \
    "Pong" \
    "Puissance_X" \
    "Snake_Eater"
}

#######################################
# Filtre la liste cible selon --jeu.
# Arguments:
#   aucun
# Retour:
#   ecrit la liste sur stdout
#######################################
lister_jeux_java_selectionnes() {
  if [[ -n "${JEU_CIBLE}" ]]; then
    printf '%s\n' "${JEU_CIBLE}"
    return 0
  fi
  lister_jeux_java_cibles
}

#######################################
# Retourne le nom de classe de test Java.
# Arguments:
#   $1: nom du jeu
# Retour:
#   ecrit le nom de classe sur stdout
#######################################
obtenir_classe_test_java() {
  case "$1" in
    Columns) echo "TestContratColumns" ;;
    DinoRail) echo "TestContratDinoRail" ;;
    InitialDrift) echo "TestContratInitialDrift" ;;
    JavaSpace) echo "TestContratJavaSpace" ;;
    Kowasu_Renga) echo "TestContratKowasuRenga" ;;
    Minesweeper) echo "TestContratMinesweeper" ;;
    Pong) echo "TestContratPong" ;;
    Puissance_X) echo "TestContratPuissanceX" ;;
    Snake_Eater) echo "TestContratSnakeEater" ;;
    *) arreter_sur_erreur "Jeu Java cible inconnu: $1" "Utilisez un jeu Java reference dans config/matrice_tests_jeux.json." ;;
  esac
}

#######################################
# Retourne les fichiers a compiler pour
# un jeu Java cible donne.
# Arguments:
#   $1: nom du jeu
# Retour:
#   ecrit la liste sur stdout
#######################################
obtenir_fichiers_test_java() {
  case "$1" in
    Columns)
      printf '%s\n' "${REPERTOIRE_BORNE}"/projet/Columns/*.java "${REPERTOIRE_BORNE}/tests/jeux_java/TestContratColumns.java" ;;
    DinoRail)
      printf '%s\n' "${REPERTOIRE_BORNE}"/projet/DinoRail/*.java "${REPERTOIRE_BORNE}/tests/jeux_java/TestContratDinoRail.java" ;;
    InitialDrift)
      printf '%s\n' "${REPERTOIRE_BORNE}"/projet/InitialDrift/*.java "${REPERTOIRE_BORNE}/tests/jeux_java/TestContratInitialDrift.java" ;;
    JavaSpace)
      printf '%s\n' "${REPERTOIRE_BORNE}"/projet/JavaSpace/*.java "${REPERTOIRE_BORNE}/tests/jeux_java/TestContratJavaSpace.java" ;;
    Kowasu_Renga)
      printf '%s\n' "${REPERTOIRE_BORNE}"/projet/Kowasu_Renga/*.java "${REPERTOIRE_BORNE}/tests/jeux_java/TestContratKowasuRenga.java" ;;
    Minesweeper)
      printf '%s\n' "${REPERTOIRE_BORNE}"/projet/Minesweeper/*.java "${REPERTOIRE_BORNE}/tests/jeux_java/TestContratMinesweeper.java" ;;
    Pong)
      printf '%s\n' "${REPERTOIRE_BORNE}"/projet/Pong/*.java "${REPERTOIRE_BORNE}/tests/jeux_java/TestContratPong.java" ;;
    Puissance_X)
      printf '%s\n' "${REPERTOIRE_BORNE}"/projet/Puissance_X/*.java "${REPERTOIRE_BORNE}/tests/jeux_java/TestContratPuissanceX.java" ;;
    Snake_Eater)
      printf '%s\n' "${REPERTOIRE_BORNE}"/projet/Snake_Eater/*.java "${REPERTOIRE_BORNE}/tests/jeux_java/TestContratSnakeEater.java" ;;
    *)
      arreter_sur_erreur "Jeu Java cible inconnu: $1" "Utilisez un jeu Java reference dans config/matrice_tests_jeux.json." ;;
  esac
}

#######################################
# Compile les sources et tests Java
# d un jeu cible donne.
# Arguments:
#   $1: nom du jeu
# Retour:
#   0
#######################################
compiler_test_java_cible() {
  local nom_jeu="$1"
  local classpath_mg2d
  local fichiers_a_compiler=()
  local fichier
  classpath_mg2d="$(obtenir_classpath_mg2d)"
  DOSSIER_CLASSES_JEUX_CIBLES="${DOSSIER_BUILD_CLASSES_TESTS}/jeux_java_cibles/${nom_jeu}"

  while IFS= read -r fichier; do
    fichiers_a_compiler+=("${fichier}")
  done < <(obtenir_fichiers_test_java "${nom_jeu}")

  (
    cd "${REPERTOIRE_BORNE}"
    rm -rf "${DOSSIER_CLASSES_JEUX_CIBLES}"
    mkdir -p "${DOSSIER_CLASSES_JEUX_CIBLES}"
    executer_javac -d "${DOSSIER_CLASSES_JEUX_CIBLES}" -cp ".:${classpath_mg2d}" \
      "${fichiers_a_compiler[@]}"
  )
}

#######################################
# Execute le test cible d un jeu Java.
# Arguments:
#   $1: nom du jeu
# Retour:
#   0
#######################################
executer_test_java_cible() {
  local nom_jeu="$1"
  local classe_test
  classe_test="$(obtenir_classe_test_java "${nom_jeu}")"
  compiler_test_java_cible "${nom_jeu}"
  (
    cd "${REPERTOIRE_BORNE}/projet/${nom_jeu}"
    java -cp ".:${DOSSIER_CLASSES_JEUX_CIBLES}:$(obtenir_classpath_mg2d)" "${classe_test}"
  )
  printf 'OK %s : test cible\n' "${nom_jeu}"
}

#######################################
# Point d entree des tests Java cibles.
# Arguments:
#   --jeu <nom> optionnel
# Retour:
#   0
#######################################
main() {
  charger_configuration_borne

  local nom_jeu
  while IFS= read -r nom_jeu; do
    [[ -n "${nom_jeu}" ]] || continue
    executer_test_java_cible "${nom_jeu}"
  done < <(lister_jeux_java_selectionnes)

  if [[ -z "${JEU_CIBLE}" ]]; then
    journaliser "Tests jeux Java cibles: OK"
  fi
}

main "$@"
