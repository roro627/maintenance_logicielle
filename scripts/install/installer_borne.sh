#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

COMMANDE_PYTHON_VENV=""
PRIVILEGES_SYSTEME_ACTIFS=0
INSTALLATION_SYSTEME_OPTIONNEL="${INSTALLATION_SYSTEME_OPTIONNEL:-0}"
DOSSIER_INSTALLATION_ACT_SYSTEME="${DOSSIER_INSTALLATION_ACT_SYSTEME:-/usr/local/bin}"
GROUPE_DOCKER_UTILISATEUR_AJOUTE=0

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
# Retourne le prefixe d elevation a
# utiliser pour les operations systeme.
# Arguments:
#   aucun
# Retour:
#   ecrit le prefixe sur stdout
#######################################
obtenir_prefixe_elevation_systeme() {
  if [[ "$(id -u)" -eq 0 ]]; then
    printf '%s\n' ""
    return 0
  fi

  if [[ "${PRIVILEGES_SYSTEME_ACTIFS}" == "1" ]]; then
    printf '%s\n' "sudo"
    return 0
  fi

  arreter_sur_erreur \
    "Privileges systeme insuffisants pour executer les operations requises." \
    "Relancez avec sudo ./bootstrap_borne.sh pour autoriser l installation systeme."
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
  obtenir_prefixe_elevation_systeme
}

#######################################
# Indique si l execution courante tourne
# dans un environnement conteneurise.
# Arguments:
#   aucun
# Retour:
#   0 si conteneur detecte
#######################################
environnement_conteneurise() {
  [[ -f "/.dockerenv" ]] && return 0
  [[ -f "/run/.containerenv" ]] && return 0
  grep -qaE '(docker|containerd|kubepods|podman|lxc)' /proc/1/cgroup 2>/dev/null
}

#######################################
# Retourne le dossier home d un utilisateur.
# Arguments:
#   $1: nom utilisateur
# Retour:
#   ecrit le home sur stdout
#######################################
obtenir_dossier_home_utilisateur() {
  local utilisateur="$1"
  local entree_passwd=""

  if command -v getent >/dev/null 2>&1; then
    entree_passwd="$(getent passwd "${utilisateur}" || true)"
  else
    entree_passwd="$(grep "^${utilisateur}:" /etc/passwd | head -n 1 || true)"
  fi

  [[ -n "${entree_passwd}" ]] || return 1
  printf '%s\n' "${entree_passwd}" | cut -d: -f6
}

#######################################
# Retourne l utilisateur a configurer
# pour l utilisation locale de Docker/act.
# Arguments:
#   aucun
# Retour:
#   ecrit le nom utilisateur sur stdout
#######################################
obtenir_utilisateur_local_act() {
  if [[ -n "${SUDO_USER:-}" ]] && [[ "${SUDO_USER}" != "root" ]]; then
    printf '%s\n' "${SUDO_USER}"
    return 0
  fi

  id -un
}

#######################################
# Determine le suffixe architecture
# attendu par les releases act.
# Arguments:
#   aucun
# Retour:
#   ecrit le suffixe sur stdout
#######################################
obtenir_suffixe_archive_act() {
  case "$(uname -m)" in
    x86_64|amd64)
      printf '%s\n' "x86_64"
      ;;
    aarch64|arm64)
      printf '%s\n' "arm64"
      ;;
    armv7l|armv7)
      printf '%s\n' "armv7"
      ;;
    armv6l|armv6)
      printf '%s\n' "armv6"
      ;;
    i386|i686)
      printf '%s\n' "i386"
      ;;
    *)
      arreter_sur_erreur \
        "Architecture non supportee pour installer act automatiquement: $(uname -m)." \
        "Installez act manuellement depuis une release officielle puis relancez scripts/install/installer_borne.sh."
      ;;
  esac
}

#######################################
# Indique si Docker est deja operationnel.
# Arguments:
#   aucun
# Retour:
#   0 si Docker repond
#######################################
docker_operationnel() {
  command -v docker >/dev/null 2>&1 \
    && docker version >/dev/null 2>&1 \
    && docker info >/dev/null 2>&1
}

#######################################
# Indique si Docker repond avec un
# prefixe d elevation systeme au besoin.
# Arguments:
#   aucun
# Retour:
#   0 si Docker repond
#######################################
docker_operationnel_avec_elevation() {
  local prefixe_elevation=""

  if docker_operationnel; then
    return 0
  fi

  if [[ "$(id -u)" -eq 0 ]]; then
    return 1
  fi

  if [[ "${PRIVILEGES_SYSTEME_ACTIFS}" != "1" ]]; then
    return 1
  fi

  prefixe_elevation="$(obtenir_prefixe_elevation_systeme)"
  [[ -n "${prefixe_elevation}" ]] || return 1

  "${prefixe_elevation}" docker version >/dev/null 2>&1 \
    && "${prefixe_elevation}" docker info >/dev/null 2>&1
}

#######################################
# Attend quelques secondes que Docker
# demarre completement apres installation.
# Arguments:
#   aucun
# Retour:
#   0 si Docker repond avant timeout
#######################################
attendre_docker_operationnel() {
  local _

  for _ in 1 2 3 4 5; do
    if docker_operationnel_avec_elevation; then
      return 0
    fi
    sleep 2
  done

  return 1
}

#######################################
# Retourne la commande act resolue si
# elle est disponible sur la machine.
# Arguments:
#   aucun
# Retour:
#   ecrit le chemin de la commande sur stdout
#######################################
obtenir_commande_act() {
  if command -v act >/dev/null 2>&1; then
    command -v act
    return 0
  fi

  if [[ -x "${DOSSIER_INSTALLATION_ACT_SYSTEME}/act" ]]; then
    printf '%s\n' "${DOSSIER_INSTALLATION_ACT_SYSTEME}/act"
    return 0
  fi

  return 1
}

#######################################
# Indique si le bootstrap peut preparer
# l execution locale de act ici.
# Arguments:
#   aucun
# Retour:
#   0 si preparation a lancer
#######################################
installation_act_locale_requise() {
  if [[ "${BORNE_MODE_TEST:-0}" == "1" ]]; then
    journaliser "Mode test actif: preparation locale de act ignoree"
    return 1
  fi

  if environnement_conteneurise; then
    journaliser "Environnement conteneurise detecte: preparation locale de act ignoree."
    return 1
  fi

  return 0
}

#######################################
# Retourne la distribution officielle
# attendue par le depot Docker.
# Arguments:
#   aucun
# Retour:
#   ecrit l identifiant distribution sur stdout
#######################################
obtenir_distribution_docker() {
  local identifiant=""
  identifiant="$(. /etc/os-release && printf '%s' "${ID:-}")"

  case "${identifiant}" in
    debian|raspbian|ubuntu)
      printf '%s\n' "${identifiant}"
      ;;
    *)
      arreter_sur_erreur \
        "Distribution non supportee pour l installation automatique de Docker Engine: ${identifiant:-inconnue}." \
        "Installez Docker Engine selon la documentation officielle, puis relancez scripts/install/installer_borne.sh."
      ;;
  esac
}

#######################################
# Retourne le code de version de la
# distribution pour le depot Docker.
# Arguments:
#   aucun
# Retour:
#   ecrit le codename sur stdout
#######################################
obtenir_codename_distribution() {
  local codename=""
  codename="$(. /etc/os-release && printf '%s' "${VERSION_CODENAME:-${UBUNTU_CODENAME:-}}")"

  [[ -n "${codename}" ]] \
    || arreter_sur_erreur \
      "Impossible de determiner le codename de la distribution pour Docker Engine." \
      "Verifiez /etc/os-release puis relancez scripts/install/installer_borne.sh."

  printf '%s\n' "${codename}"
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
  paquets_obligatoires=(ca-certificates git curl nodejs npm openjdk-17-jdk python3 python3-venv python3-pip checkstyle pylint shellcheck xdotool lua5.4 libsndfile1 love)

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
# Supprime les paquets Docker en conflit
# avant installation du depot officiel.
# Arguments:
#   $1...: commande apt complete
# Retour:
#   0
#######################################
supprimer_paquets_docker_conflits() {
  local -a commande_apt=("$@")
  local paquets_conflits=(
    docker.io
    docker-doc
    docker-compose
    podman-docker
    containerd
    runc
  )
  local paquets_presents=()
  local paquet

  for paquet in "${paquets_conflits[@]}"; do
    if paquet_systeme_installe "${paquet}"; then
      paquets_presents+=("${paquet}")
    fi
  done

  if [[ "${#paquets_presents[@]}" -eq 0 ]]; then
    return 0
  fi

  journaliser "Suppression paquets Docker en conflit: ${paquets_presents[*]}"
  "${commande_apt[@]}" remove -y "${paquets_presents[@]}"
}

#######################################
# Installe Docker Engine depuis le depot
# officiel Docker.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
installer_docker_engine() {
  local prefixe_elevation=""
  local distribution_docker=""
  local codename_distribution=""
  local architecture_dpkg=""
  local -a commande_apt=()
  local -a prefixe_systeme=()

  if docker_operationnel; then
    journaliser "Docker Engine deja operationnel"
    return 0
  fi

  if [[ "${PRIVILEGES_SYSTEME_ACTIFS}" != "1" ]]; then
    if [[ "${INSTALLATION_SYSTEME_OPTIONNEL}" == "1" ]]; then
      journaliser "ATTENTION: Docker Engine non disponible sans privileges systeme, etape ignoree (mode optionnel)."
      return 0
    fi

    arreter_sur_erreur \
      "Docker Engine est requis pour executer act localement." \
      "Relancez sudo ./bootstrap_borne.sh pour installer Docker Engine automatiquement."
  fi

  prefixe_elevation="$(obtenir_prefixe_elevation_apt)"
  if [[ -n "${prefixe_elevation}" ]]; then
    commande_apt=("${prefixe_elevation}" apt-get)
    prefixe_systeme=("${prefixe_elevation}")
  else
    commande_apt=(apt-get)
  fi

  distribution_docker="$(obtenir_distribution_docker)"
  codename_distribution="$(obtenir_codename_distribution)"
  architecture_dpkg="$(dpkg --print-architecture)"

  supprimer_paquets_docker_conflits "${commande_apt[@]}"

  journaliser "Preparation depot officiel Docker (${distribution_docker} ${codename_distribution})"
  "${commande_apt[@]}" update
  "${commande_apt[@]}" install -y ca-certificates curl

  "${prefixe_systeme[@]}" install -m 0755 -d /etc/apt/keyrings
  "${prefixe_systeme[@]}" curl -fsSL "https://download.docker.com/linux/${distribution_docker}/gpg" \
    -o /etc/apt/keyrings/docker.asc
  "${prefixe_systeme[@]}" chmod a+r /etc/apt/keyrings/docker.asc

  printf 'deb [arch=%s signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/%s %s stable\n' \
    "${architecture_dpkg}" "${distribution_docker}" "${codename_distribution}" \
    | "${prefixe_systeme[@]}" tee /etc/apt/sources.list.d/docker.list >/dev/null

  "${commande_apt[@]}" update
  journaliser "Installation Docker Engine"
  "${commande_apt[@]}" install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

  if command -v systemctl >/dev/null 2>&1; then
    "${prefixe_systeme[@]}" systemctl enable --now docker >/dev/null 2>&1 || true
  elif command -v service >/dev/null 2>&1; then
    "${prefixe_systeme[@]}" service docker start >/dev/null 2>&1 || true
  fi
}

#######################################
# Ajoute l utilisateur local au groupe
# docker pour lancer act sans sudo.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
configurer_groupe_docker_utilisateur_local() {
  local utilisateur_local=""
  local prefixe_elevation=""
  local -a prefixe_systeme=()

  utilisateur_local="$(obtenir_utilisateur_local_act)"
  [[ "${utilisateur_local}" != "root" ]] || return 0

  prefixe_elevation="$(obtenir_prefixe_elevation_systeme)"
  if [[ -n "${prefixe_elevation}" ]]; then
    prefixe_systeme=("${prefixe_elevation}")
  fi

  if ! getent group docker >/dev/null 2>&1; then
    "${prefixe_systeme[@]}" groupadd docker
  fi

  if id -nG "${utilisateur_local}" | tr ' ' '\n' | grep -qx "docker"; then
    journaliser "Utilisateur ${utilisateur_local} deja membre du groupe docker"
    return 0
  fi

  "${prefixe_systeme[@]}" usermod -aG docker "${utilisateur_local}"
  GROUPE_DOCKER_UTILISATEUR_AJOUTE=1
  journaliser "Utilisateur ${utilisateur_local} ajoute au groupe docker (deconnexion/reconnexion recommandee)."
}

#######################################
# Installe act depuis la release officielle
# GitHub dans un dossier systeme partage.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
installer_commande_act() {
  local commande_act_existante=""
  local suffixe_archive=""
  local dossier_temporaire=""
  local archive_act=""
  local url_archive_act=""
  local -a prefixe_systeme=()
  local prefixe_elevation=""

  if commande_act_existante="$(obtenir_commande_act 2>/dev/null)"; then
    journaliser "Commande act deja presente: ${commande_act_existante}"
    return 0
  fi

  if [[ "${PRIVILEGES_SYSTEME_ACTIFS}" != "1" ]]; then
    if [[ "${INSTALLATION_SYSTEME_OPTIONNEL}" == "1" ]]; then
      journaliser "ATTENTION: act absent sans privileges systeme, etape ignoree (mode optionnel)."
      return 0
    fi

    arreter_sur_erreur \
      "La commande act est requise pour lancer les workflows localement." \
      "Relancez sudo ./bootstrap_borne.sh pour installer act automatiquement."
  fi

  suffixe_archive="$(obtenir_suffixe_archive_act)"
  prefixe_elevation="$(obtenir_prefixe_elevation_systeme)"
  if [[ -n "${prefixe_elevation}" ]]; then
    prefixe_systeme=("${prefixe_elevation}")
  fi

  dossier_temporaire="$(mktemp -d)"
  archive_act="${dossier_temporaire}/act.tar.gz"
  url_archive_act="https://github.com/nektos/act/releases/download/v${VERSION_ACT_OUTIL}/act_Linux_${suffixe_archive}.tar.gz"

  journaliser "Telechargement act v${VERSION_ACT_OUTIL} (${suffixe_archive})"
  curl -fsSL "${url_archive_act}" -o "${archive_act}" \
    || arreter_sur_erreur \
      "Impossible de telecharger act depuis la release officielle." \
      "Verifiez la connectivite reseau puis relancez scripts/install/installer_borne.sh."

  tar -xzf "${archive_act}" -C "${dossier_temporaire}" \
    || arreter_sur_erreur \
      "Archive act invalide ou extraction impossible." \
      "Supprimez ${archive_act} puis relancez scripts/install/installer_borne.sh."

  [[ -x "${dossier_temporaire}/act" ]] \
    || arreter_sur_erreur \
      "Binaire act absent de l archive officielle." \
      "Verifiez la release GitHub ciblee puis relancez scripts/install/installer_borne.sh."

  "${prefixe_systeme[@]}" install -m 0755 -d "${DOSSIER_INSTALLATION_ACT_SYSTEME}"
  "${prefixe_systeme[@]}" install -m 0755 "${dossier_temporaire}/act" "${DOSSIER_INSTALLATION_ACT_SYSTEME}/act"
  rm -rf "${dossier_temporaire}"
}

#######################################
# Cree un point d entree utilisateur
# stable vers act dans ~/.local/bin.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
configurer_lanceur_act_utilisateur_local() {
  local utilisateur_local=""
  local dossier_home_utilisateur=""
  local commande_act=""
  local dossier_bin_local=""
  local lien_act_local=""
  local groupe_utilisateur=""

  commande_act="$(obtenir_commande_act)" || return 0
  utilisateur_local="$(obtenir_utilisateur_local_act)"
  dossier_home_utilisateur="$(obtenir_dossier_home_utilisateur "${utilisateur_local}" || true)"
  [[ -n "${dossier_home_utilisateur}" ]] || return 0

  dossier_bin_local="${dossier_home_utilisateur}/.local/bin"
  lien_act_local="${dossier_bin_local}/act"

  mkdir -p "${dossier_bin_local}"
  ln -sfn "${commande_act}" "${lien_act_local}"

  if [[ "$(id -u)" -eq 0 ]]; then
    groupe_utilisateur="$(id -gn "${utilisateur_local}")"
    chown "${utilisateur_local}:${groupe_utilisateur}" "${dossier_home_utilisateur}/.local" "${dossier_bin_local}" 2>/dev/null || true
    chown -h "${utilisateur_local}:${groupe_utilisateur}" "${lien_act_local}" 2>/dev/null || true
  fi
}

#######################################
# Retourne la commande `codex` resolue
# si elle est disponible sur la machine.
# Arguments:
#   aucun
# Retour:
#   ecrit le chemin sur stdout
#######################################
obtenir_commande_codex() {
  if command -v codex >/dev/null 2>&1; then
    command -v codex
    return 0
  fi

  if [[ -x "/usr/local/bin/codex" ]]; then
    printf '%s\n' "/usr/local/bin/codex"
    return 0
  fi

  return 1
}

#######################################
# Retourne la version Node.js detectee
# sans le prefixe `v`.
# Arguments:
#   aucun
# Retour:
#   ecrit la version sur stdout
#######################################
obtenir_version_node() {
  local version_node=""

  command -v node >/dev/null 2>&1 || return 1
  version_node="$(node --version 2>/dev/null | sed -E 's/^v([0-9]+(\.[0-9]+){0,2}).*/\1/')"
  [[ -n "${version_node}" ]] || return 1
  printf '%s\n' "${version_node}"
}

#######################################
# Indique si la version Node.js fournie
# est compatible avec Codex CLI.
# Arguments:
#   $1: version Node.js detectee
# Retour:
#   0 si compatible, 1 sinon
#######################################
nodejs_compatible_codex() {
  local version_node="$1"
  [[ -n "${version_node}" ]] || return 1
  version_minimale_respectee "${version_node}" "${NODE_VERSION_MIN_CODEX}"
}

#######################################
# Installe automatiquement une version
# Node.js compatible avec Codex via
# le depot officiel NodeSource.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
garantir_nodejs_compatible_codex() {
  local version_node=""
  local prefixe_elevation=""
  local -a commande_apt=()
  local -a prefixe_systeme=()
  local script_setup_nodesource=""
  local url_setup_nodesource="https://deb.nodesource.com/setup_${VERSION_NODE_SOURCE_MAJEURE}.x"

  if version_node="$(obtenir_version_node 2>/dev/null)" && nodejs_compatible_codex "${version_node}"; then
    journaliser "Node.js compatible pour Codex detecte: v${version_node}"
    return 0
  fi

  if [[ -n "${version_node}" ]]; then
    journaliser "Node.js trop ancien pour Codex detecte: v${version_node} (minimum ${NODE_VERSION_MIN_CODEX})"
  else
    journaliser "Node.js absent: installation d une version compatible Codex requise"
  fi

  if [[ "${PRIVILEGES_SYSTEME_ACTIFS}" != "1" ]]; then
    if [[ "${INSTALLATION_SYSTEME_OPTIONNEL}" == "1" ]]; then
      journaliser "ATTENTION: Node.js/Codex absents ou obsoletes sans privileges systeme, etape ignoree (mode optionnel)."
      return 0
    fi
    arreter_sur_erreur \
      "Node.js ${NODE_VERSION_MIN_CODEX}+ est requis pour executer Codex CLI." \
      "Relancez sudo ./bootstrap_borne.sh pour installer automatiquement Node.js ${VERSION_NODE_SOURCE_MAJEURE}.x."
  fi

  if ! command -v apt-get >/dev/null 2>&1; then
    arreter_sur_erreur \
      "Impossible d installer automatiquement Node.js compatible sans apt-get." \
      "Installez manuellement Node.js ${NODE_VERSION_MIN_CODEX}+ puis relancez scripts/install/installer_borne.sh."
  fi

  prefixe_elevation="$(obtenir_prefixe_elevation_apt)"
  if [[ -n "${prefixe_elevation}" ]]; then
    commande_apt=("${prefixe_elevation}" apt-get)
    prefixe_systeme=("${prefixe_elevation}")
  else
    commande_apt=(apt-get)
  fi

  journaliser "Installation Node.js ${VERSION_NODE_SOURCE_MAJEURE}.x via NodeSource pour compatibilite Codex"
  "${commande_apt[@]}" update
  "${commande_apt[@]}" install -y ca-certificates curl gnupg

  script_setup_nodesource="$(mktemp)"
  curl -fsSL "${url_setup_nodesource}" -o "${script_setup_nodesource}" \
    || arreter_sur_erreur \
      "Impossible de telecharger le script officiel NodeSource." \
      "Verifiez la connectivite reseau puis relancez scripts/install/installer_borne.sh."

  if ! "${prefixe_systeme[@]}" bash "${script_setup_nodesource}"; then
    rm -f "${script_setup_nodesource}"
    arreter_sur_erreur \
      "Impossible de configurer le depot NodeSource." \
      "Verifiez la distribution cible et relancez scripts/install/installer_borne.sh."
  fi
  rm -f "${script_setup_nodesource}"

  "${commande_apt[@]}" install -y nodejs \
    || arreter_sur_erreur \
      "Impossible d installer Node.js ${VERSION_NODE_SOURCE_MAJEURE}.x depuis NodeSource." \
      "Verifiez le depot NodeSource puis relancez scripts/install/installer_borne.sh."

  version_node="$(obtenir_version_node 2>/dev/null || true)"
  if [[ -z "${version_node}" ]] || ! nodejs_compatible_codex "${version_node}"; then
    arreter_sur_erreur \
      "Node.js reste incompatible pour Codex apres installation automatique (detecte=${version_node:-absent}, minimum=${NODE_VERSION_MIN_CODEX})." \
      "Installez manuellement Node.js ${NODE_VERSION_MIN_CODEX}+ puis relancez scripts/install/installer_borne.sh."
  fi

  command -v npm >/dev/null 2>&1 \
    || arreter_sur_erreur \
      "npm reste indisponible apres installation de Node.js compatible." \
      "Verifiez le depot NodeSource puis relancez scripts/install/installer_borne.sh."

  journaliser "Node.js compatible pour Codex pret: v${version_node}"
}

#######################################
# Installe Codex CLI globalement via npm.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
installer_commande_codex() {
  local commande_codex_existante=""
  local prefixe_elevation=""
  local -a prefixe_systeme=()
  local prefixe_npm=""
  local binaire_codex_attendu=""

  if [[ "${BORNE_MODE_TEST:-0}" == "1" ]]; then
    journaliser "Mode test actif: installation Codex CLI ignoree"
    return 0
  fi

  if commande_codex_existante="$(obtenir_commande_codex 2>/dev/null)"; then
    if "${commande_codex_existante}" --version >/dev/null 2>&1; then
      journaliser "Commande codex deja presente: ${commande_codex_existante}"
      return 0
    fi
  fi

  garantir_nodejs_compatible_codex

  if ! command -v npm >/dev/null 2>&1; then
    arreter_sur_erreur \
      "npm est requis pour installer Codex CLI automatiquement." \
      "Installez nodejs/npm puis relancez sudo ./bootstrap_borne.sh."
  fi

  if [[ "${PRIVILEGES_SYSTEME_ACTIFS}" != "1" ]]; then
    if [[ "${INSTALLATION_SYSTEME_OPTIONNEL}" == "1" ]]; then
      journaliser "ATTENTION: codex absent sans privileges systeme, etape ignoree (mode optionnel)."
      return 0
    fi

    arreter_sur_erreur \
      "La commande codex est requise pour le workflow de migration assistee." \
      "Relancez sudo ./bootstrap_borne.sh pour installer Codex CLI automatiquement."
  fi

  prefixe_elevation="$(obtenir_prefixe_elevation_systeme)"
  if [[ -n "${prefixe_elevation}" ]]; then
    prefixe_systeme=("${prefixe_elevation}")
  fi

  prefixe_npm="$("${prefixe_systeme[@]}" npm prefix -g 2>/dev/null || printf '%s\n' '/usr/local')"
  binaire_codex_attendu="${prefixe_npm}/bin/codex"

  journaliser "Installation Codex CLI via npm global (@openai/codex)"
  "${prefixe_systeme[@]}" env npm_config_prefix="${prefixe_npm}" npm install -g @openai/codex \
    || arreter_sur_erreur \
      "Impossible d installer Codex CLI via npm." \
      "Verifiez nodejs/npm, la connectivite reseau, puis relancez sudo ./bootstrap_borne.sh."

  if ! obtenir_commande_codex >/dev/null 2>&1 && [[ -x "${binaire_codex_attendu}" ]]; then
    "${prefixe_systeme[@]}" install -m 0755 -d /usr/local/bin
    "${prefixe_systeme[@]}" ln -sfn "${binaire_codex_attendu}" /usr/local/bin/codex
  fi
}

#######################################
# Cree un point d entree utilisateur
# stable vers codex dans ~/.local/bin.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
configurer_lanceur_codex_utilisateur_local() {
  local utilisateur_local=""
  local dossier_home_utilisateur=""
  local commande_codex=""
  local dossier_bin_local=""
  local lien_codex_local=""
  local groupe_utilisateur=""

  commande_codex="$(obtenir_commande_codex)" || return 0
  utilisateur_local="$(obtenir_utilisateur_local_act)"
  dossier_home_utilisateur="$(obtenir_dossier_home_utilisateur "${utilisateur_local}" || true)"
  [[ -n "${dossier_home_utilisateur}" ]] || return 0

  dossier_bin_local="${dossier_home_utilisateur}/.local/bin"
  lien_codex_local="${dossier_bin_local}/codex"

  mkdir -p "${dossier_bin_local}"
  ln -sfn "${commande_codex}" "${lien_codex_local}"

  if [[ "$(id -u)" -eq 0 ]]; then
    groupe_utilisateur="$(id -gn "${utilisateur_local}")"
    chown "${utilisateur_local}:${groupe_utilisateur}" "${dossier_home_utilisateur}/.local" "${dossier_bin_local}" 2>/dev/null || true
    chown -h "${utilisateur_local}:${groupe_utilisateur}" "${lien_codex_local}" 2>/dev/null || true
  fi
}

#######################################
# Verifie que Codex CLI peut demarrer.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_fonctionnement_codex() {
  local commande_codex=""

  if [[ "${BORNE_MODE_TEST:-0}" == "1" ]]; then
    journaliser "Mode test actif: verification Codex CLI ignoree"
    return 0
  fi

  commande_codex="$(obtenir_commande_codex)" \
    || arreter_sur_erreur \
      "La commande codex reste indisponible apres installation." \
      "Verifiez l installation npm globale puis relancez scripts/install/installer_borne.sh."

  "${commande_codex}" --version >/dev/null 2>&1 \
    || arreter_sur_erreur \
      "La commande codex ne demarre pas correctement." \
      "Reinstallez Codex CLI via sudo ./bootstrap_borne.sh puis relancez le bootstrap."
}

#######################################
# Verifie que Docker et act peuvent etre
# utilises pour lancer les workflows locaux.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_fonctionnement_act_local() {
  local commande_act=""

  if ! attendre_docker_operationnel; then
    arreter_sur_erreur \
      "Docker Engine est installe mais ne repond pas correctement." \
      "Verifiez le service docker, reconnectez l utilisateur si besoin, puis relancez sudo ./bootstrap_borne.sh."
  fi

  if [[ "${GROUPE_DOCKER_UTILISATEUR_AJOUTE}" == "1" ]] && ! docker_operationnel; then
    journaliser \
      "ATTENTION: Docker a ete verifie avec elevation systeme; reconnectez l utilisateur pour activer le groupe docker en session courante."
  fi

  commande_act="$(obtenir_commande_act)" \
    || arreter_sur_erreur \
      "La commande act reste indisponible apres installation." \
      "Verifiez ${DOSSIER_INSTALLATION_ACT_SYSTEME}/act puis relancez scripts/install/installer_borne.sh."

  "${commande_act}" --version >/dev/null 2>&1 \
    || arreter_sur_erreur \
      "La commande act ne demarre pas correctement." \
      "Reinstallez act via sudo ./bootstrap_borne.sh puis relancez les workflows."

  "${commande_act}" -W "${RACINE_PROJET}/.github/workflows" -l >/dev/null 2>&1 \
    || arreter_sur_erreur \
      "La commande act n arrive pas a lire les workflows du projet." \
      "Verifiez les fichiers .github/workflows puis relancez scripts/install/installer_borne.sh."
}

#######################################
# Prepare l execution locale des workflows
# GitHub via Docker Engine et act.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
preparer_execution_locale_act() {
  if ! installation_act_locale_requise; then
    return 0
  fi

  if [[ "${PRIVILEGES_SYSTEME_ACTIFS}" != "1" ]] && [[ "${INSTALLATION_SYSTEME_OPTIONNEL}" == "1" ]]; then
    if ! docker_operationnel || ! obtenir_commande_act >/dev/null 2>&1; then
      journaliser "ATTENTION: preparation locale de act ignoree (mode optionnel sans privileges systeme)."
      return 0
    fi
  fi

  installer_docker_engine

  if [[ "${PRIVILEGES_SYSTEME_ACTIFS}" == "1" ]]; then
    configurer_groupe_docker_utilisateur_local
  fi

  installer_commande_act
  configurer_lanceur_act_utilisateur_local
  verifier_fonctionnement_act_local
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
  if ! command -v git >/dev/null 2>&1; then
    journaliser \
      "ATTENTION: git introuvable, configuration hook reportee. Action recommandee: relancez sudo ./bootstrap_borne.sh."
    return 0
  fi

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
  preparer_execution_locale_act
  installer_commande_codex
  configurer_lanceur_codex_utilisateur_local
  verifier_fonctionnement_codex
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
