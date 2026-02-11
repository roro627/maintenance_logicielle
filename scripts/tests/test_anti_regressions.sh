#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

#######################################
# Verifie l absence de chemins absolus Raspberry figes.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_absence_chemins_figes() {
  if grep -RsnE --include='*.java' --include='*.sh' "/home/pi/git/borne_arcade|/home/pi/git/MG2D|/home/\\\$USER/git/MG2D" "${REPERTOIRE_BORNE}" >/dev/null; then
    arreter_sur_erreur "Chemin absolu fige detecte dans borne_arcade"
  fi
}

#######################################
# Verifie l absence de constructeurs wrappers depricies.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_absence_wrappers_depricies() {
  if grep -RsnE --include='*.java' 'new Integer\(|new Long\(' "${REPERTOIRE_BORNE}" >/dev/null; then
    arreter_sur_erreur "Constructeur wrapper deprecie detecte"
  fi
}

#######################################
# Verifie la protection contre l absence de musiques de fond.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_garde_musiques_fond() {
  if ! grep -Fq "Files.isDirectory(cheminMusiques)" "${REPERTOIRE_BORNE}/Graphique.java"; then
    arreter_sur_erreur "Garde de repertoire sound/bg manquante dans Graphique.java"
  fi
}

#######################################
# Point d entree du test anti regressions.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
main() {
  charger_configuration_borne
  verifier_absence_chemins_figes
  verifier_absence_wrappers_depricies
  verifier_garde_musiques_fond
  journaliser "Test anti regressions: OK"
}

main "$@"
