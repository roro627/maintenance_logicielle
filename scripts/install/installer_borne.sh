#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

COMMANDE_PYTHON_VENV=""

#######################################
# Indique si sudo peut etre utilise en mode non interactif.
# Arguments:
#   aucun
# Retour:
#   0 si sudo -n est disponible, 1 sinon
#######################################
sudo_non_interactif_disponible() {
  command -v sudo >/dev/null 2>&1 && sudo -n true >/dev/null 2>&1
}

#######################################
# Prepare un environnement virtuel Python dedie au projet.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
preparer_venv_python_projet() {
  local dossier_venv="${RACINE_PROJET}/.venv"
  local python_hote="${COMMANDE_PYTHON}"

  if [[ ! -x "${dossier_venv}/bin/python" ]]; then
    journaliser "Creation environnement virtuel Python: ${dossier_venv}"
    "${python_hote}" -m venv "${dossier_venv}"
  fi

  COMMANDE_PYTHON_VENV="${dossier_venv}/bin/python"
  [[ -x "${COMMANDE_PYTHON_VENV}" ]] || arreter_sur_erreur "Python venv introuvable: ${COMMANDE_PYTHON_VENV}"
}

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
  paquets=(git openjdk-17-jdk python3 python3-venv python3-pip checkstyle pylint shellcheck xdotool love lua5.4)
  local prefixe_commande=()
  if [[ "$(id -u)" -ne 0 ]]; then
    if sudo_non_interactif_disponible; then
      prefixe_commande=(sudo)
    else
      journaliser "Privileges insuffisants pour apt-get: installation systeme ignoree"
      return 0
    fi
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

  preparer_venv_python_projet

  if [[ "${BORNE_MODE_TEST:-0}" == "1" ]]; then
    journaliser "Mode test actif: creation venv conservee, installation pip ignoree"
    return 0
  fi

  journaliser "Installation outils python globaux"
  "${COMMANDE_PYTHON_VENV}" -m pip install --upgrade pip mkdocs pytest pylint

  local requirements
  while IFS= read -r requirements; do
    journaliser "Installation dependances python depuis ${requirements}"
    "${COMMANDE_PYTHON_VENV}" -m pip install -r "${requirements}"
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
# Installe le layout clavier borne au niveau utilisateur
# et tente une installation systeme si possible.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
installer_layout_clavier_borne() {
  local source_layout="${REPERTOIRE_BORNE}/borne"
  local destination_locale="${HOME}/.xkb/symbols/borne"
  local destination_systeme="/usr/share/X11/xkb/symbols/borne"
  local prefixe_commande=()

  if [[ ! -f "${source_layout}" ]]; then
    journaliser "Layout clavier borne absent, etape ignoree"
    return 0
  fi

  mkdir -p "$(dirname "${destination_locale}")"
  cp "${source_layout}" "${destination_locale}"

  if [[ "${BORNE_MODE_TEST:-0}" == "1" ]]; then
    journaliser "Mode test actif: installation systeme du layout ignoree"
    return 0
  fi

  if [[ "$(id -u)" -ne 0 ]]; then
    if sudo_non_interactif_disponible; then
      prefixe_commande=(sudo)
    else
      journaliser "Privileges insuffisants pour copier le layout systeme"
      return 0
    fi
  fi

  if [[ -w "/usr/share/X11/xkb/symbols" || "${#prefixe_commande[@]}" -gt 0 || "$(id -u)" -eq 0 ]]; then
    "${prefixe_commande[@]}" cp "${source_layout}" "${destination_systeme}" || true
  fi
}

#######################################
# Installe l autostart utilisateur de la borne.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
installer_autostart_borne() {
  local source_desktop="${REPERTOIRE_BORNE}/borne.desktop"
  local dossier_autostart="${HOME}/.config/autostart"
  local destination_desktop="${dossier_autostart}/borne.desktop"

  if [[ ! -f "${source_desktop}" ]]; then
    journaliser "Fichier borne.desktop absent: autostart ignore"
    return 0
  fi

  mkdir -p "${dossier_autostart}"
  cp "${source_desktop}" "${destination_desktop}"
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
# Prepare les dossiers d organisation
# et de sortie du projet.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
preparer_dossiers_organisation() {
  mkdir -p "${RACINE_PROJET}/build"
  mkdir -p "${RACINE_PROJET}/logs"
  mkdir -p "${RACINE_PROJET}/archives"
  mkdir -p "${RACINE_PROJET}/src"
  mkdir -p "${RACINE_PROJET}/tests"
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
  installer_layout_clavier_borne
  installer_autostart_borne
  configurer_permissions_scripts
  configurer_hook_git
  initialiser_fichiers_highscore
  preparer_dossiers_organisation
  journaliser "Installation terminee"
}

main "$@"
