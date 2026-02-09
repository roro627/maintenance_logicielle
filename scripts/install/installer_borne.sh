#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

#######################################
# Installe les dependances apt necessaires.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
installer_dependances_systeme() {
  if [[ "${BORNE_MODE_TEST:-0}" == "1" ]]; then
    journaliser "Mode test actif: installation apt ignoree"
    return 0
  fi

  if ! command -v apt-get >/dev/null 2>&1; then
    journaliser "apt-get indisponible: installation systeme ignoree"
    return 0
  fi

  local paquets
  paquets=(git openjdk-17-jdk python3 python3-venv python3-pip checkstyle pylint shellcheck xdotool love)
  local prefixe_commande=()
  if command -v sudo >/dev/null 2>&1 && [[ "$(id -u)" -ne 0 ]]; then
    prefixe_commande=(sudo)
  fi

  journaliser "Mise a jour index apt"
  "${prefixe_commande[@]}" apt-get update
  journaliser "Installation dependances systeme"
  "${prefixe_commande[@]}" apt-get install -y "${paquets[@]}"
}

#######################################
# Installe les dependances python des jeux.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
installer_dependances_python() {
  if ! command -v "${COMMANDE_PYTHON}" >/dev/null 2>&1; then
    arreter_sur_erreur "${COMMANDE_PYTHON} introuvable"
  fi

  if [[ "${BORNE_MODE_TEST:-0}" == "1" ]]; then
    journaliser "Mode test actif: installation pip ignoree"
    return 0
  fi

  journaliser "Installation outils python globaux"
  "${COMMANDE_PYTHON}" -m pip install --upgrade pip mkdocs pytest

  local requirements
  while IFS= read -r requirements; do
    journaliser "Installation dependances python depuis ${requirements}"
    "${COMMANDE_PYTHON}" -m pip install -r "${requirements}"
  done < <(find "${REPERTOIRE_BORNE}/projet" -maxdepth 2 -name requirements.txt | sort)
}

#######################################
# Configure les permissions d execution des scripts.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
configurer_permissions_scripts() {
  journaliser "Configuration des permissions scripts"
  chmod +x "${RACINE_PROJET}/scripts/deploiement/post_pull_update.sh"
  chmod +x "${RACINE_PROJET}/scripts/docs/generer_documentation.sh"
  chmod +x "${RACINE_PROJET}/scripts/lint/lancer_lint.sh"
  chmod +x "${RACINE_PROJET}/scripts/tests"/*.sh
  chmod +x "${RACINE_PROJET}/.githooks/post-merge"
  chmod +x "${REPERTOIRE_BORNE}"/*.sh
  chmod +x "${REPERTOIRE_BORNE}"/projet/*/*.sh 2>/dev/null || true
}

#######################################
# Configure le hook git post-merge si le depot git existe.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
configurer_hook_git() {
  if git -C "${RACINE_PROJET}" rev-parse --git-dir >/dev/null 2>&1; then
    journaliser "Activation core.hooksPath=.githooks"
    git -C "${RACINE_PROJET}" config core.hooksPath .githooks
  else
    journaliser "Depot git absent: configuration hook reportee"
  fi
}

#######################################
# Cree les fichiers highscore manquants pour chaque jeu.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
initialiser_fichiers_highscore() {
  local dossier_jeu
  for dossier_jeu in "${REPERTOIRE_BORNE}"/projet/*; do
    [[ -d "${dossier_jeu}" ]] || continue
    if [[ ! -f "${dossier_jeu}/highscore" ]]; then
      journaliser "Creation fichier highscore: ${dossier_jeu}/highscore"
      touch "${dossier_jeu}/highscore"
    fi
  done
}

#######################################
# Point d entree de l installation.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
main() {
  charger_configuration_borne
  journaliser "Debut installation borne"
  installer_dependances_systeme
  installer_dependances_python
  configurer_permissions_scripts
  configurer_hook_git
  initialiser_fichiers_highscore
  journaliser "Installation terminee"
}

main "$@"
