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
# Lance un jeu de reference pour valider le retour processus.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
tester_lancement_jeu_reference() {
  (
    cd "${REPERTOIRE_BORNE}"
    ./ReflexeFlash.sh >/tmp/reflexeflash_test.log 2>&1
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
  tester_lancement_jeu_reference
  journaliser "Test jeux: OK"
}

main "$@"
