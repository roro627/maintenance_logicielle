#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

ERREURS_ARCHITECTURE=()

#######################################
# Ajoute une erreur d architecture.
# Arguments:
#   $1: message erreur
# Retour:
#   0
#######################################
ajouter_erreur_architecture() {
  local message="$1"
  ERREURS_ARCHITECTURE+=("${message}")
}

#######################################
# Verifie les dossiers structurants.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_dossiers_structurants() {
  local dossiers_attendus=(
    "${RACINE_PROJET}/src"
    "${RACINE_PROJET}/docs"
    "${RACINE_PROJET}/scripts"
    "${RACINE_PROJET}/config"
    "${RACINE_PROJET}/tests"
    "${RACINE_PROJET}/archives"
    "${RACINE_PROJET}/build"
  )
  local dossier
  for dossier in "${dossiers_attendus[@]}"; do
    [[ -d "${dossier}" ]] || ajouter_erreur_architecture "Dossier structurant manquant: ${dossier}"
  done
}

#######################################
# Verifie l absence de fichiers legacy
# hors du dossier d archives.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_absence_legacy_hors_archives() {
  local legacy_java2
  legacy_java2="$(find "${RACINE_PROJET}" -type f -name '*.java2' ! -path "${RACINE_PROJET}/archives/*" -print -quit)"
  [[ -z "${legacy_java2}" ]] || ajouter_erreur_architecture "Fichier legacy hors archives: ${legacy_java2}"

  if [[ -f "${REPERTOIRE_BORNE}/clean" ]]; then
    ajouter_erreur_architecture "Ancien script non archive detecte: ${REPERTOIRE_BORNE}/clean"
  fi
}

#######################################
# Verifie que la compilation Java cible
# explicitement le dossier build.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_compilation_orientee_build() {
  local script_compilation="${REPERTOIRE_BORNE}/compilation.sh"
  rg -q "DOSSIER_BUILD_CLASSES_MENU" "${script_compilation}" \
    || ajouter_erreur_architecture "Compilation menu non orientee build dans ${script_compilation}"
  rg -q "DOSSIER_BUILD_CLASSES_JEUX" "${script_compilation}" \
    || ajouter_erreur_architecture "Compilation jeux non orientee build dans ${script_compilation}"
  rg -q "javac -d" "${script_compilation}" \
    || ajouter_erreur_architecture "Option -d absente des compilations Java dans ${script_compilation}"
}

#######################################
# Verifie l absence de .class hors des
# dossiers de sortie autorises.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_classes_hors_zones_autorisees() {
  local classe_intruse
  classe_intruse="$(find "${RACINE_PROJET}" -type f -name '*.class' \
    ! -path "${RACINE_PROJET}/build/*" \
    ! -path "${RACINE_PROJET}/.cache/*" \
    ! -path "${RACINE_PROJET}/archives/*" \
    ! -path "${RACINE_PROJET}/MG2D/*" \
    -print -quit)"
  [[ -z "${classe_intruse}" ]] || ajouter_erreur_architecture "Classe compilee hors build/.cache: ${classe_intruse}"
}

#######################################
# Termine le test en erreur si des
# anomalies ont ete collecte.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
echouer_si_erreurs_architecture() {
  local message
  if [[ "${#ERREURS_ARCHITECTURE[@]}" -eq 0 ]]; then
    return 0
  fi

  for message in "${ERREURS_ARCHITECTURE[@]}"; do
    journaliser "ERREUR: ${message}"
  done
  arreter_sur_erreur \
    "${#ERREURS_ARCHITECTURE[@]} erreur(s) d architecture detectee(s)." \
    "Consultez ARCHITECTURE.md, deplacez les legacy vers archives/ et gardez les artefacts dans build/.cache."
}

#######################################
# Point d entree test architecture.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
main() {
  charger_configuration_borne
  verifier_dossiers_structurants
  verifier_absence_legacy_hors_archives
  verifier_compilation_orientee_build
  verifier_classes_hors_zones_autorisees
  echouer_si_erreurs_architecture
  journaliser "Test architecture: OK"
}

main "$@"
