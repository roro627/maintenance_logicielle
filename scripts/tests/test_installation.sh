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
    "${RACINE_PROJET}/bootstrap_borne.sh"
    "${RACINE_PROJET}/scripts/install/installer_borne.sh"
    "${RACINE_PROJET}/scripts/deploiement/post_pull_update.sh"
    "${RACINE_PROJET}/scripts/docs/generer_documentation.sh"
    "${RACINE_PROJET}/scripts/lint/lancer_lint.sh"
    "${RACINE_PROJET}/scripts/tests/test_smoke.sh"
    "${RACINE_PROJET}/.githooks/post-merge"
    "${RACINE_PROJET}/config/versions_minimales.env"
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
# Lance l installateur pour valider l idempotence.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
valider_installation() {
  if [[ "${TEST_INSTALLATION_SIMULATION:-0}" == "1" ]]; then
    BORNE_MODE_TEST=1 "${RACINE_PROJET}/scripts/install/installer_borne.sh"
    return 0
  fi
  "${RACINE_PROJET}/scripts/install/installer_borne.sh"
}

#######################################
# Verifie que l autostart utilisateur est bien prepare.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_autostart_utilisateur() {
  local fichier_autostart="${HOME}/.config/autostart/borne.desktop"
  [[ -f "${fichier_autostart}" ]] || arreter_sur_erreur "Autostart borne.desktop manquant: ${fichier_autostart}"
}

#######################################
# Verifie la presence de l environnement virtuel projet.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_venv_projet() {
  local python_venv="${RACINE_PROJET}/.venv/bin/python"
  [[ -x "${python_venv}" ]] || arreter_sur_erreur "Environnement virtuel projet absent: ${python_venv}"
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
  valider_installation
  verifier_venv_projet
  verifier_autostart_utilisateur
  journaliser "Test installation: OK"
}

main "$@"
