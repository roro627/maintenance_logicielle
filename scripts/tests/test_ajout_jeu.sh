#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

#######################################
# Verifie qu un dossier de jeu contient les fichiers minimaux.
# Arguments:
#   $1: chemin dossier jeu
# Retour:
#   0
#######################################
verifier_jeu() {
  local dossier_jeu="$1"
  local nom_jeu
  nom_jeu="$(basename "${dossier_jeu}")"

  [[ -f "${dossier_jeu}/description.txt" ]] || arreter_sur_erreur "description.txt manquant pour ${nom_jeu}"
  [[ -f "${dossier_jeu}/bouton.txt" ]] || arreter_sur_erreur "bouton.txt manquant pour ${nom_jeu}"
  [[ -f "${dossier_jeu}/highscore" ]] || arreter_sur_erreur "highscore manquant pour ${nom_jeu}"
  [[ -f "${REPERTOIRE_BORNE}/${nom_jeu}.sh" ]] || arreter_sur_erreur "Lanceur ${nom_jeu}.sh manquant"
}

#######################################
# Verifie la conformite de tous les jeux.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_catalogue_jeux() {
  local dossier_jeu
  for dossier_jeu in "${REPERTOIRE_BORNE}/projet"/*; do
    [[ -d "${dossier_jeu}" ]] || continue
    verifier_jeu "${dossier_jeu}"
  done
}

#######################################
# Point d entree test ajout jeu.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
main() {
  charger_configuration_borne
  verifier_catalogue_jeux
  journaliser "Test ajout de jeu: OK"
}

main "$@"
