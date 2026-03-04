#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

JEU_CIBLE="${1:-}"
if [[ "${JEU_CIBLE:-}" == "--jeu" ]]; then
  JEU_CIBLE="${2:-}"
fi

#######################################
# Retourne la liste des jeux Python avec
# tests cibles pour cette suite.
# Arguments:
#   aucun
# Retour:
#   ecrit la liste sur stdout
#######################################
lister_jeux_python_cibles() {
  printf '%s\n' "MaintenanceMode" "NeonSumo" "OsuTile" "PianoTile" "TronGame" "ball-blast"
}

#######################################
# Filtre la liste cible selon --jeu.
# Arguments:
#   aucun
# Retour:
#   ecrit la liste sur stdout
#######################################
lister_jeux_python_selectionnes() {
  if [[ -n "${JEU_CIBLE}" ]]; then
    printf '%s\n' "${JEU_CIBLE}"
    return 0
  fi
  lister_jeux_python_cibles
}

#######################################
# Execute le test cible d un jeu Python.
# Arguments:
#   $1: nom du jeu
# Retour:
#   0
#######################################
executer_test_python_cible() {
  local nom_jeu="$1"
  local commande=()
  case "${nom_jeu}" in
    MaintenanceMode)
      commande=("${COMMANDE_PYTHON}" -m unittest discover -s borne_arcade/projet/MaintenanceMode/tests -p 'test_*.py') ;;
    NeonSumo)
      commande=("${COMMANDE_PYTHON}" -m unittest discover -s borne_arcade/projet/NeonSumo/tests -p 'test_*.py') ;;
    OsuTile)
      commande=("${COMMANDE_PYTHON}" -m unittest discover -s borne_arcade/projet/OsuTile/tests -p 'test_*.py') ;;
    PianoTile)
      commande=("${COMMANDE_PYTHON}" -m unittest discover -s borne_arcade/projet/PianoTile/tests -p 'test_*.py') ;;
    TronGame)
      commande=("${COMMANDE_PYTHON}" -m unittest discover -s borne_arcade/projet/TronGame/tests -p 'test_*.py') ;;
    ball-blast)
      commande=("${COMMANDE_PYTHON}" -m unittest discover -s borne_arcade/projet/ball-blast/tests -p 'test_*.py') ;;
    *)
      arreter_sur_erreur "Jeu Python cible inconnu: ${nom_jeu}" "Utilisez un jeu Python reference dans config/matrice_tests_jeux.json." ;;
  esac

  (
    cd "${RACINE_PROJET}"
    "${commande[@]}"
  )
  printf 'OK %s : test cible\n' "${nom_jeu}"
}

#######################################
# Point d entree des tests Python cibles.
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
    executer_test_python_cible "${nom_jeu}"
  done < <(lister_jeux_python_selectionnes)

  if [[ -z "${JEU_CIBLE}" ]]; then
    journaliser "Tests jeux Python cibles: OK"
  fi
}

main "$@"
