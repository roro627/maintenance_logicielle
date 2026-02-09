#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

#######################################
# Verifie l existence des fichiers critiques d installation.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_fichiers_critiques() {
  local fichiers
  fichiers=(
    "${RACINE_PROJET}/scripts/install/installer_borne.sh"
    "${RACINE_PROJET}/scripts/deploiement/post_pull_update.sh"
    "${RACINE_PROJET}/scripts/docs/generer_documentation.sh"
    "${RACINE_PROJET}/scripts/lint/lancer_lint.sh"
    "${RACINE_PROJET}/.githooks/post-merge"
    "${REPERTOIRE_BORNE}/compilation.sh"
    "${REPERTOIRE_BORNE}/lancerBorne.sh"
    "${REPERTOIRE_BORNE}/config/borne.env"
  )

  local fichier
  for fichier in "${fichiers[@]}"; do
    [[ -f "${fichier}" ]] || arreter_sur_erreur "Fichier manquant: ${fichier}"
  done
}

#######################################
# Lance l installateur en mode test pour valider l idempotence.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
valider_installation_mode_test() {
  BORNE_MODE_TEST=1 "${RACINE_PROJET}/scripts/install/installer_borne.sh"
}

#######################################
# Point d entree du test installation.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
main() {
  charger_configuration_borne
  verifier_fichiers_critiques
  valider_installation_mode_test
  journaliser "Test installation: OK"
}

main "$@"
