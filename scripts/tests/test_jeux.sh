#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

#######################################
# Lance la compilation Java de la borne.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
compiler_borne() {
  "${REPERTOIRE_BORNE}/compilation.sh"
}

#######################################
# Verifie qu un script de lancement existe pour chaque jeu.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_lanceurs() {
  local dossier_jeu
  local nom_jeu
  for dossier_jeu in "${REPERTOIRE_BORNE}/projet"/*; do
    [[ -d "${dossier_jeu}" ]] || continue
    nom_jeu="$(basename "${dossier_jeu}")"
    [[ -x "${REPERTOIRE_BORNE}/${nom_jeu}.sh" ]] || arreter_sur_erreur "Lanceur non executable: ${nom_jeu}.sh"
  done
}

#######################################
# Lance un jeu avec un mode smoke-test non interactif.
# Arguments:
#   $1: nom du jeu
# Retour:
#   0
#######################################
tester_lancement_jeu_smoke() {
  local nom_jeu="$1"
  local chemin_lanceur="${REPERTOIRE_BORNE}/${nom_jeu}.sh"
  local fichier_log="/tmp/${nom_jeu}_test.log"

  [[ -x "${chemin_lanceur}" ]] || arreter_sur_erreur "Jeu introuvable ou non executable: ${nom_jeu}.sh"

  (
    cd "${REPERTOIRE_BORNE}"
    BORNE_MODE_TEST_JEU=1 "./${nom_jeu}.sh" >"${fichier_log}" 2>&1
  )
}

#######################################
# Verifie le lancement smoke de tous les jeux du catalogue.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
tester_lancement_tous_les_jeux() {
  local dossier_jeu
  local nom_jeu
  for dossier_jeu in "${REPERTOIRE_BORNE}/projet"/*; do
    [[ -d "${dossier_jeu}" ]] || continue
    nom_jeu="$(basename "${dossier_jeu}")"
    tester_lancement_jeu_smoke "${nom_jeu}"
  done
}

#######################################
# Execute les tests unitaires Python de Neon Sumo.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
tester_unitaire_neon_sumo() {
  (
    cd "${RACINE_PROJET}"
    "${COMMANDE_PYTHON}" -m unittest borne_arcade/projet/NeonSumo/tests/test_logique.py
  )
}

#######################################
# Execute les tests unitaires Python du
# mode maintenance.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
tester_unitaire_maintenance_mode() {
  (
    cd "${RACINE_PROJET}"
    "${COMMANDE_PYTHON}" -m unittest discover -s borne_arcade/projet/MaintenanceMode/tests -p "test_*.py"
  )
}

#######################################
# Execute les tests unitaires Python de
# PianoTile.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
tester_unitaire_pianotile() {
  (
    cd "${RACINE_PROJET}"
    "${COMMANDE_PYTHON}" -m unittest discover -s borne_arcade/projet/PianoTile/tests -p "test_*.py"
  )
}

#######################################
# Point d entree test jeux.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
main() {
  charger_configuration_borne
  compiler_borne
  verifier_lanceurs
  tester_unitaire_neon_sumo
  tester_unitaire_maintenance_mode
  tester_unitaire_pianotile
  tester_lancement_tous_les_jeux
  journaliser "Test jeux: OK"
}

main "$@"
