#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

ERREURS_DETECTEES=()

#######################################
# Ajoute une erreur a la liste.
# Arguments:
#   $1: message erreur
# Retour:
#   0
#######################################
ajouter_erreur() {
  local message="$1"
  ERREURS_DETECTEES+=("${message}")
}

#######################################
# Verifie que AGENTS.md reference bien
# la source canonique MG2D.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_regle_mg2d_agents() {
  local fichier_agents="${RACINE_PROJET}/AGENTS.md"

  [[ -f "${fichier_agents}" ]] || {
    ajouter_erreur "AGENTS.md introuvable"
    return 0
  }

  rg -q "https://github.com/synave/MG2D" "${fichier_agents}" \
    || ajouter_erreur "Source canonique MG2D absente de AGENTS.md"
  rg -Fq "Do NOT modify any file under \`MG2D/\`" "${fichier_agents}" \
    || ajouter_erreur "Regle d integrite MG2D absente de AGENTS.md"
}

#######################################
# Verifie qu'aucun .class n est present
# dans MG2D pour garantir la lecture seule.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_absence_classes_mg2d() {
  local classes_detectees
  classes_detectees="$(find "${RACINE_PROJET}/MG2D" -type f -name '*.class' | head -n 1 || true)"
  [[ -z "${classes_detectees}" ]] \
    || ajouter_erreur "Classe compilee detectee dans MG2D: ${classes_detectees}"
}

#######################################
# Verifie la presence des artefacts
# essentiels de la bibliotheque MG2D.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_artefacts_mg2d() {
  local fichiers_requis=(
    "${RACINE_PROJET}/MG2D/README.md"
    "${RACINE_PROJET}/MG2D/MG2D"
    "${RACINE_PROJET}/MG2D/Demos"
    "${RACINE_PROJET}/MG2D/TP_Prise_en_main"
    "${RACINE_PROJET}/MG2D/COPYING"
  )

  local element
  for element in "${fichiers_requis[@]}"; do
    [[ -e "${element}" ]] || ajouter_erreur "Artefact MG2D manquant: ${element}"
  done
}

#######################################
# Termine le test en erreur si des
# anomalies ont ete collecte.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
echouer_si_erreurs_detectees() {
  local message
  if [[ "${#ERREURS_DETECTEES[@]}" -eq 0 ]]; then
    return 0
  fi

  for message in "${ERREURS_DETECTEES[@]}"; do
    journaliser "ERREUR: ${message}"
  done
  arreter_sur_erreur "${#ERREURS_DETECTEES[@]} erreur(s) detectee(s) sur MG2D"
}

#######################################
# Point d entree du test integrite MG2D.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
main() {
  charger_configuration_borne
  verifier_regle_mg2d_agents
  verifier_absence_classes_mg2d
  verifier_artefacts_mg2d
  echouer_si_erreurs_detectees
  journaliser "Test integrite MG2D: OK"
}

main "$@"
