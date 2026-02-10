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
# Verifie les fichiers obligatoires d un jeu.
# Arguments:
#   $1: dossier du jeu
# Retour:
#   0
#######################################
verifier_fichiers_obligatoires_jeu() {
  local dossier_jeu="$1"
  local nom_jeu
  nom_jeu="$(basename "${dossier_jeu}")"

  [[ -f "${dossier_jeu}/description.txt" ]] \
    || ajouter_erreur "description.txt manquant pour ${nom_jeu}"
  [[ -f "${dossier_jeu}/bouton.txt" ]] \
    || ajouter_erreur "bouton.txt manquant pour ${nom_jeu}"
  [[ -f "${dossier_jeu}/highscore" ]] \
    || ajouter_erreur "highscore manquant pour ${nom_jeu}"
  [[ -f "${dossier_jeu}/photo_small.png" ]] \
    || ajouter_erreur "photo_small.png manquant pour ${nom_jeu}"
  [[ -x "${REPERTOIRE_BORNE}/${nom_jeu}.sh" ]] \
    || ajouter_erreur "Lanceur non executable: ${nom_jeu}.sh"
}

#######################################
# Verifie la presence de contenu utile
# dans les fichiers de configuration.
# Arguments:
#   $1: dossier du jeu
# Retour:
#   0
#######################################
verifier_configuration_jeu_non_vide() {
  local dossier_jeu="$1"
  local nom_jeu
  nom_jeu="$(basename "${dossier_jeu}")"

  [[ -s "${dossier_jeu}/description.txt" ]] \
    || ajouter_erreur "description.txt vide pour ${nom_jeu}"
  [[ -s "${dossier_jeu}/bouton.txt" ]] \
    || ajouter_erreur "bouton.txt vide pour ${nom_jeu}"
  [[ -w "${dossier_jeu}/highscore" ]] \
    || ajouter_erreur "highscore non modifiable pour ${nom_jeu}"
}

#######################################
# Verifie qu un jeu contient au moins
# un fichier source (Java/Python/Lua).
# Arguments:
#   $1: dossier du jeu
# Retour:
#   0
#######################################
verifier_presence_sources_jeu() {
  local dossier_jeu="$1"
  local nom_jeu
  local source_detectee
  nom_jeu="$(basename "${dossier_jeu}")"

  source_detectee="$(find "${dossier_jeu}" -type f \( -name '*.java' -o -name '*.py' -o -name '*.lua' \) | head -n 1 || true)"
  [[ -n "${source_detectee}" ]] \
    || ajouter_erreur "Aucune source detectee pour ${nom_jeu}"
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
  arreter_sur_erreur "${#ERREURS_DETECTEES[@]} erreur(s) detectee(s) dans le catalogue jeux"
}

#######################################
# Verifie la conformite de tous les jeux.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_catalogue_complet() {
  local dossier_jeu
  for dossier_jeu in "${REPERTOIRE_BORNE}/projet"/*; do
    [[ -d "${dossier_jeu}" ]] || continue
    verifier_fichiers_obligatoires_jeu "${dossier_jeu}"
    verifier_configuration_jeu_non_vide "${dossier_jeu}"
    verifier_presence_sources_jeu "${dossier_jeu}"
  done
}

#######################################
# Point d entree du test catalogue jeux.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
main() {
  charger_configuration_borne
  verifier_catalogue_complet
  echouer_si_erreurs_detectees
  journaliser "Test catalogue jeux complet: OK"
}

main "$@"
