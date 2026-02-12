#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

COMMANDE_PYTHON_VENV=""
PRIVILEGES_SYSTEME_ACTIFS=0
INSTALLATION_SYSTEME_OPTIONNEL="${INSTALLATION_SYSTEME_OPTIONNEL:-0}"

#######################################
# Initialise la strategie de privileges
# systeme pour l installation.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_privileges_systeme() {
  if [[ "${BORNE_MODE_TEST:-0}" == "1" ]]; then
    PRIVILEGES_SYSTEME_ACTIFS=1
    return 0
  fi

  if [[ "$(id -u)" -eq 0 ]]; then
    PRIVILEGES_SYSTEME_ACTIFS=1
    return 0
  fi

  if ! command -v sudo >/dev/null 2>&1; then
    if [[ "${INSTALLATION_SYSTEME_OPTIONNEL}" == "1" ]]; then
      PRIVILEGES_SYSTEME_ACTIFS=0
      journaliser "ATTENTION: sudo introuvable, les etapes systeme seront ignorees (mode optionnel)."
      return 0
    fi
    arreter_sur_erreur \
      "sudo introuvable pour executer les etapes systeme obligatoires." \
      "Installez sudo ou lancez ce script en root."
  fi

  if sudo_non_interactif_disponible; then
    PRIVILEGES_SYSTEME_ACTIFS=1
    return 0
  fi

  if [[ -t 0 ]]; then
    journaliser "Privilege root requis: demande d authentification sudo"
    if sudo -v; then
      PRIVILEGES_SYSTEME_ACTIFS=1
      return 0
    fi
    if [[ "${INSTALLATION_SYSTEME_OPTIONNEL}" == "1" ]]; then
      PRIVILEGES_SYSTEME_ACTIFS=0
      journaliser "ATTENTION: sudo refuse, les etapes systeme seront ignorees (mode optionnel)."
      return 0
    fi
    arreter_sur_erreur \
      "Impossible de valider sudo pour l installation systeme." \
      "Utilisez un compte membre sudo, ou executez ce script en root."
  fi

  if [[ "${INSTALLATION_SYSTEME_OPTIONNEL}" == "1" ]]; then
    PRIVILEGES_SYSTEME_ACTIFS=0
    journaliser "ATTENTION: session non interactive sans sudo, etapes systeme ignorees (mode optionnel)."
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

  if [[ "${PRIVILEGES_SYSTEME_ACTIFS}" == "1" ]]; then
    printf '%s\n' "sudo"
    return 0
  fi

  arreter_sur_erreur \
    "Privileges systeme insuffisants pour apt-get." \
    "Relancez avec sudo ./bootstrap_borne.sh pour autoriser l installation systeme."
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
# Applique un contournement de
# post-installation du paquet love.
# Arguments:
#   $1...: commande apt complete
# Retour:
#   0 si contournement applique, 1 sinon
#######################################
appliquer_contournement_postinstall_love() {
  local -a commande_apt=("$@")
  local fichier_postinst_love="/var/lib/dpkg/info/love.postinst"
  local fichier_manquant_love=""

  if dpkg-query -W -f='${Status}' love 2>/dev/null | grep -q "install ok installed"; then
    return 0
  fi

  if ! dpkg -s love >/dev/null 2>&1; then
    return 1
  fi

  if [[ -f "${fichier_postinst_love}" ]]; then
    fichier_manquant_love="$(sed -n 's/.*\(\/usr\/share\/man\/man6\/love-[0-9.]*\.gz\).*/\1/p' "${fichier_postinst_love}" | head -n 1)"
  fi

  if [[ -z "${fichier_manquant_love}" ]]; then
    fichier_manquant_love="/usr/share/man/man6/love.6.gz"
  fi

  journaliser "Contournement love: creation de ${fichier_manquant_love}"
  mkdir -p "$(dirname "${fichier_manquant_love}")"
  if [[ ! -f "${fichier_manquant_love}" ]]; then
    : > "${fichier_manquant_love}"
  fi

  if "${commande_apt[@]}" -f install -y; then
    return 0
  fi

  return 1
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

  local paquets_obligatoires
  local paquets_obligatoires_manquants=()
  local prefixe_elevation=""
  local -a commande_apt=()
  local paquet
  paquets_obligatoires=(git curl openjdk-17-jdk python3 python3-venv python3-pip checkstyle pylint shellcheck xdotool lua5.4 libsndfile1 love)

  for paquet in "${paquets_obligatoires[@]}"; do
    if paquet_systeme_installe "${paquet}"; then
      journaliser "Dependance systeme deja presente: ${paquet}"
    else
      journaliser "Dependance systeme manquante: ${paquet}"
      paquets_obligatoires_manquants+=("${paquet}")
    fi
  done

  if [[ "${#paquets_obligatoires_manquants[@]}" -eq 0 ]]; then
    journaliser "Toutes les dependances systeme ciblees sont deja installees"
    return 0
  fi

  if [[ "${PRIVILEGES_SYSTEME_ACTIFS}" != "1" ]]; then
    arreter_sur_erreur \
      "Dependances systeme manquantes sans privileges root/sudo: ${paquets_obligatoires_manquants[*]}" \
      "Relancez sudo ./bootstrap_borne.sh pour installer automatiquement ces dependances."
  fi

  prefixe_elevation="$(obtenir_prefixe_elevation_apt)"

  if [[ -n "${prefixe_elevation}" ]]; then
    commande_apt=("${prefixe_elevation}" apt-get)
  else
    commande_apt=(apt-get)
  fi

  journaliser "Mise a jour index apt"
  "${commande_apt[@]}" update

  journaliser "Installation dependances systeme obligatoires: ${paquets_obligatoires_manquants[*]}"
  if ! "${commande_apt[@]}" install -y "${paquets_obligatoires_manquants[@]}"; then
    if printf '%s\n' "${paquets_obligatoires_manquants[@]}" | grep -qx "love"; then
      journaliser "Echec installation love detecte: tentative de contournement automatique."
      appliquer_contournement_postinstall_love "${commande_apt[@]}" \
        || arreter_sur_erreur \
          "Echec installation obligatoire de love, meme apres contournement automatique." \
          "Verifiez la connectivite apt, puis relancez scripts/install/installer_borne.sh."
    else
      arreter_sur_erreur \
        "Echec installation des dependances systeme obligatoires." \
        "Verifiez la connectivite apt et les droits root, puis relancez scripts/install/installer_borne.sh."
    fi
  fi

  paquet_systeme_installe love \
    || arreter_sur_erreur \
      "Le paquet love reste indisponible alors qu il est obligatoire." \
      "Corrigez l etat apt/dpkg, puis relancez scripts/install/installer_borne.sh."
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
# Applique un chmod sur une liste de
# cibles sans echouer si un element
# est non modifiable.
# Arguments:
#   $1: mode chmod
#   $2..n: chemins cibles
# Retour:
#   0
#######################################
appliquer_chmod_si_possible() {
  local mode="$1"
  shift
  local cible
  for cible in "$@"; do
    [[ -e "${cible}" ]] || continue
    [[ -L "${cible}" ]] && continue
    if ! chmod "${mode}" "${cible}" 2>/dev/null; then
      journaliser "ATTENTION: impossible d appliquer chmod ${mode} sur ${cible}."
    fi
  done
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
  appliquer_chmod_si_possible a+rwx \
    "${RACINE_PROJET}/bootstrap_borne.sh" \
    "${RACINE_PROJET}/scripts/deploiement/post_pull_update.sh" \
    "${RACINE_PROJET}/scripts/docs/generer_documentation.sh" \
    "${RACINE_PROJET}/scripts/lint/lancer_lint.sh" \
    "${RACINE_PROJET}/.githooks/post-merge"

  local script
  while IFS= read -r script; do
    appliquer_chmod_si_possible a+rwx "${script}"
  done < <(find "${RACINE_PROJET}/scripts" "${REPERTOIRE_BORNE}" -type f -name '*.sh' | sort)
}

#######################################
# Applique des droits partages pour
# eviter les blocages multi-utilisateurs.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
configurer_permissions_partagees() {
  journaliser "Configuration des droits partages (tout utilisateur)"
  mkdir -p "${RACINE_PROJET}/logs" "${RACINE_PROJET}/build" "${RACINE_PROJET}/.cache"

  appliquer_chmod_si_possible a+rwx \
    "${RACINE_PROJET}/logs" \
    "${RACINE_PROJET}/build" \
    "${RACINE_PROJET}/.cache" \
    "${RACINE_PROJET}/.venv" \
    "${RACINE_PROJET}/site" \
    "${REPERTOIRE_BORNE}" \
    "${REPERTOIRE_BORNE}/projet"

  local chemin
  local cibles_partagees=(
    "${RACINE_PROJET}/logs"
    "${RACINE_PROJET}/build"
    "${RACINE_PROJET}/.cache"
    "${RACINE_PROJET}/.venv"
    "${RACINE_PROJET}/site"
    "${REPERTOIRE_BORNE}/projet"
  )

  for chemin in "${cibles_partagees[@]}"; do
    [[ -e "${chemin}" ]] || continue
    appliquer_chmod_si_possible a+rwX "${chemin}"
  done

  while IFS= read -r chemin; do
    appliquer_chmod_si_possible a+rwX "${chemin}"
  done < <(find "${RACINE_PROJET}/logs" "${RACINE_PROJET}/build" "${RACINE_PROJET}/.cache" \
    "${RACINE_PROJET}/.venv" "${RACINE_PROJET}/site" "${REPERTOIRE_BORNE}/projet" \
    -mindepth 1 -print 2>/dev/null | sort)

  while IFS= read -r chemin; do
    appliquer_chmod_si_possible a+rw "${chemin}"
  done < <(find "${REPERTOIRE_BORNE}/projet" -type f \( -name 'highscore' -o -name 'bouton.txt' -o -name 'description.txt' \) | sort)
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
    if [[ "${PRIVILEGES_SYSTEME_ACTIFS}" == "1" ]]; then
      prefixe_commande=(sudo)
    elif [[ "${INSTALLATION_SYSTEME_OPTIONNEL}" == "1" ]]; then
      journaliser "ATTENTION: copie systeme du layout ignoree (absence de privileges root/sudo)."
      return 0
    else
      arreter_sur_erreur \
        "Privileges systeme insuffisants pour copier le layout clavier." \
        "Relancez sudo ./bootstrap_borne.sh pour appliquer le layout systeme."
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
  preparer_dossiers_organisation
  installer_dependances_systeme
  installer_dependances_python
  installer_layout_clavier_borne
  installer_autostart_borne
  initialiser_fichiers_highscore
  configurer_permissions_scripts
  configurer_permissions_partagees
  configurer_hook_git
  journaliser "Installation terminee"
}

main "$@"
