#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

COMMANDE_PYTHON_VENV=""

#######################################
# Verifie que les privileges systeme
# necessaires sont disponibles.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_privileges_systeme() {
  if [[ "${BORNE_MODE_TEST:-0}" == "1" ]]; then
    return 0
  fi

  if [[ "$(id -u)" -eq 0 ]]; then
    return 0
  fi

  command -v sudo >/dev/null 2>&1 \
    || arreter_sur_erreur \
      "sudo introuvable pour executer les etapes systeme obligatoires." \
      "Installez sudo ou lancez ce script en root."

  if sudo_non_interactif_disponible; then
    return 0
  fi

  if [[ -t 0 ]]; then
    journaliser "Privilege root requis: demande d authentification sudo"
    sudo -v \
      || arreter_sur_erreur \
        "Impossible de valider sudo pour l installation systeme." \
        "Utilisez un compte membre sudo, ou executez ce script en root."
    return 0
  fi

  arreter_sur_erreur \
    "Privileges systeme insuffisants pour l installation." \
    "Relancez avec un compte root ou un compte sudo valide."
}

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
# Indique si un paquet systeme est deja
# installe via dpkg.
# Arguments:
#   $1: nom du paquet
# Retour:
#   0 si installe, 1 sinon
#######################################
paquet_systeme_installe() {
  local nom_paquet="$1"
  if ! command -v dpkg-query >/dev/null 2>&1; then
    return 1
  fi
  dpkg-query -W -f='${Status}' "${nom_paquet}" 2>/dev/null \
    | grep -q "install ok installed"
}

#######################################
# Determine le prefixe d elevation a
# utiliser pour apt-get.
# Arguments:
#   aucun
# Retour:
#   ecrit le prefixe sur stdout
#######################################
obtenir_prefixe_elevation_apt() {
  if [[ "$(id -u)" -eq 0 ]]; then
    printf '%s\n' ""
    return 0
  fi

  if sudo_non_interactif_disponible; then
    printf '%s\n' "sudo"
    return 0
  fi

  if command -v sudo >/dev/null 2>&1 && [[ -t 0 ]]; then
    journaliser "Privilege root requis: demande d authentification sudo"
    sudo -v \
      || arreter_sur_erreur \
        "Impossible d obtenir les privileges sudo pour installer les dependances systeme ciblees." \
        "Relancez avec un compte autorise sudo, ou executez ce script en root."
    printf '%s\n' "sudo"
    return 0
  fi

  arreter_sur_erreur \
    "Privileges systeme insuffisants pour apt-get." \
    "Relancez avec un compte root ou un compte sudo valide."
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
  local paquets_manquants=()
  local prefixe_elevation=""
  local -a commande_apt=()
  local paquet
  paquets=(git openjdk-17-jdk python3 python3-venv python3-pip checkstyle pylint shellcheck xdotool love lua5.4 libsndfile1)

  for paquet in "${paquets[@]}"; do
    if paquet_systeme_installe "${paquet}"; then
      journaliser "Dependance systeme deja presente: ${paquet}"
    else
      journaliser "Dependance systeme manquante: ${paquet}"
      paquets_manquants+=("${paquet}")
    fi
  done

  if [[ "${#paquets_manquants[@]}" -eq 0 ]]; then
    journaliser "Toutes les dependances systeme ciblees sont deja installees"
    return 0
  fi

  prefixe_elevation="$(obtenir_prefixe_elevation_apt)"

  if [[ -n "${prefixe_elevation}" ]]; then
    commande_apt=("${prefixe_elevation}" apt-get)
  else
    commande_apt=(apt-get)
  fi

  journaliser "Installation des dependances systeme manquantes: ${paquets_manquants[*]}"

  journaliser "Mise a jour index apt"
  "${commande_apt[@]}" update
  journaliser "Installation dependances systeme manquantes"
  "${commande_apt[@]}" install -y "${paquets_manquants[@]}"
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
  chmod +x "${RACINE_PROJET}/bootstrap_borne.sh"
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
    elif [[ -t 0 ]]; then
      journaliser "Privilege root requis: demande d authentification sudo"
      sudo -v \
        || arreter_sur_erreur \
          "Impossible de valider sudo pour installer le layout systeme." \
          "Utilisez un compte membre sudo, ou executez ce script en root."
      prefixe_commande=(sudo)
    else
      arreter_sur_erreur \
        "Privileges systeme insuffisants pour copier le layout clavier." \
        "Relancez avec un compte root ou un compte sudo valide."
    fi
  fi

  if [[ -w "/usr/share/X11/xkb/symbols" || "${#prefixe_commande[@]}" -gt 0 || "$(id -u)" -eq 0 ]]; then
    "${prefixe_commande[@]}" cp "${source_layout}" "${destination_systeme}" \
      || arreter_sur_erreur \
        "Echec de copie du layout clavier dans ${destination_systeme}." \
        "Verifiez les droits sudo/root et relancez scripts/install/installer_borne.sh."
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
  verifier_privileges_systeme
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
