#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/lib/outils_communs.sh
source "${SCRIPT_DIR}/scripts/lib/outils_communs.sh"

FICHIER_JOURNAL_BOOTSTRAP=""
FICHIER_VERROU_BOOTSTRAP=""
DOSSIER_ETAT_BOOTSTRAP=""
FICHIER_ETAT_INSTALLATION_BOOTSTRAP=""
ETAPE_BOOTSTRAP_COURANTE="initialisation"
VERROU_BOOTSTRAP_ACTIF=0
UTILISATEUR_APPELANT_BOOTSTRAP=""
GROUPE_APPELANT_BOOTSTRAP=""

#######################################
# Verifie que le bootstrap est execute
# avec des privileges root.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_execution_root_obligatoire() {
  if [[ "${BORNE_MODE_TEST:-0}" == "1" ]]; then
    return 0
  fi

  if [[ "$(id -u)" -eq 0 ]]; then
    return 0
  fi

  arreter_sur_erreur \
    "Le bootstrap doit etre lance avec sudo (root) pour garantir une installation complete." \
    "Relancez avec: sudo ./bootstrap_borne.sh"
}

#######################################
# Initialise l identite de l utilisateur
# ayant lance sudo pour les etapes
# non-systeme (build/lint/tests/docs).
# Arguments:
#   aucun
# Retour:
#   0
#######################################
initialiser_identite_appelant_bootstrap() {
  if [[ "$(id -u)" -eq 0 ]] && [[ -n "${SUDO_USER:-}" ]] && [[ "${SUDO_USER}" != "root" ]]; then
    if id "${SUDO_USER}" >/dev/null 2>&1; then
      UTILISATEUR_APPELANT_BOOTSTRAP="${SUDO_USER}"
      GROUPE_APPELANT_BOOTSTRAP="$(id -gn "${SUDO_USER}")"
      return 0
    fi
  fi

  UTILISATEUR_APPELANT_BOOTSTRAP="$(id -un)"
  GROUPE_APPELANT_BOOTSTRAP="$(id -gn)"
}

#######################################
# Execute une commande avec l utilisateur
# appelant quand le bootstrap tourne en
# root via sudo.
# Arguments:
#   $1...: commande a executer
# Retour:
#   0
#######################################
executer_comme_utilisateur_appelant() {
  if [[ "$(id -u)" -eq 0 ]] && [[ "${UTILISATEUR_APPELANT_BOOTSTRAP}" != "root" ]]; then
    sudo -u "${UTILISATEUR_APPELANT_BOOTSTRAP}" -H "$@"
    return 0
  fi
  "$@"
}

#######################################
# Indique si sudo peut etre utilise
# en mode non interactif.
# Arguments:
#   aucun
# Retour:
#   0 si sudo -n est disponible
#######################################
sudo_non_interactif_disponible() {
  command -v sudo >/dev/null 2>&1 && sudo -n true >/dev/null 2>&1
}

#######################################
# Active la journalisation du bootstrap
# vers un fichier horodate dedie.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
activer_journalisation_bootstrap() {
  local dossier_journaux="${RACINE_PROJET}/logs"
  mkdir -p "${dossier_journaux}"
  FICHIER_JOURNAL_BOOTSTRAP="${dossier_journaux}/bootstrap_borne_$(date '+%Y%m%d_%H%M%S').log"
  exec > >(tee -a "${FICHIER_JOURNAL_BOOTSTRAP}") 2>&1
  journaliser "Journal bootstrap: ${FICHIER_JOURNAL_BOOTSTRAP}"
}

#######################################
# Prepare les chemins d etat du bootstrap.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
preparer_etat_bootstrap() {
  DOSSIER_ETAT_BOOTSTRAP="${RACINE_PROJET}/.cache/bootstrap_borne"
  FICHIER_ETAT_INSTALLATION_BOOTSTRAP="${DOSSIER_ETAT_BOOTSTRAP}/installation_prete.etat"
  mkdir -p "${DOSSIER_ETAT_BOOTSTRAP}"
}

#######################################
# Verifie si l installation initiale est
# deja preparee pour un relancement rapide.
# Arguments:
#   aucun
# Retour:
#   0 si installation deja prete
#######################################
installation_initiale_deja_preparee() {
  [[ -f "${FICHIER_ETAT_INSTALLATION_BOOTSTRAP}" ]] \
    && [[ -x "${RACINE_PROJET}/.venv/bin/python" ]] \
    && "${RACINE_PROJET}/.venv/bin/python" -c 'import pygame, pytest, mkdocs, pylint' >/dev/null 2>&1 \
    && [[ -f "${HOME}/.config/autostart/borne.desktop" ]] \
    && [[ -f "${HOME}/.xkb/symbols/borne" ]]
}

#######################################
# Enregistre l etat d installation initiale.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
marquer_installation_initiale_prete() {
  {
    printf 'version=1\n'
    printf 'date=%s\n' "$(date '+%Y-%m-%d %H:%M:%S')"
    printf 'hote=%s\n' "$(hostname)"
  } > "${FICHIER_ETAT_INSTALLATION_BOOTSTRAP}"
}

#######################################
# Acquiert un verrou pour eviter les
# executions concurrentes du bootstrap.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
acquerir_verrou_bootstrap() {
  FICHIER_VERROU_BOOTSTRAP="${RACINE_PROJET}/.bootstrap_borne.lock"

  if command -v flock >/dev/null 2>&1; then
    exec 9>"${FICHIER_VERROU_BOOTSTRAP}"
    if ! flock -n 9; then
      arreter_sur_erreur \
        "Un autre bootstrap est deja en cours." \
        "Attendez la fin du bootstrap en cours puis relancez ./bootstrap_borne.sh."
    fi
    VERROU_BOOTSTRAP_ACTIF=1
    return 0
  fi

  if [[ -f "${FICHIER_VERROU_BOOTSTRAP}" ]]; then
    arreter_sur_erreur \
      "Verrou bootstrap detecte mais flock est indisponible." \
      "Supprimez ${FICHIER_VERROU_BOOTSTRAP} uniquement si aucun bootstrap n est en cours."
  fi

  date '+%Y-%m-%d %H:%M:%S' > "${FICHIER_VERROU_BOOTSTRAP}"
  VERROU_BOOTSTRAP_ACTIF=1
}

#######################################
# Libere le verrou bootstrap.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
liberer_verrou_bootstrap() {
  if [[ "${VERROU_BOOTSTRAP_ACTIF}" -eq 1 ]] && [[ -n "${FICHIER_VERROU_BOOTSTRAP}" ]]; then
    rm -f "${FICHIER_VERROU_BOOTSTRAP}" || true
  fi
  flock -u 9 >/dev/null 2>&1 || true
  exec 9>&- || true
}

#######################################
# Gestions des erreurs globales du bootstrap.
# Arguments:
#   $1: code retour original
# Retour:
#   sort avec le code d erreur
#######################################
gerer_echec_bootstrap() {
  local code_retour="${1:-1}"
  afficher_erreur_claire \
    "Echec du bootstrap a l etape '${ETAPE_BOOTSTRAP_COURANTE}' (code=${code_retour})." \
    "Consultez ${FICHIER_JOURNAL_BOOTSTRAP}, corrigez l erreur puis relancez ./bootstrap_borne.sh."
  exit "${code_retour}"
}

#######################################
# Verifie la presence des scripts
# utilises par le bootstrap.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_scripts_bootstrap() {
  local scripts_requis=(
    "${RACINE_PROJET}/scripts/install/installer_borne.sh"
    "${REPERTOIRE_BORNE}/compilation.sh"
    "${RACINE_PROJET}/scripts/lint/lancer_lint.sh"
    "${RACINE_PROJET}/scripts/tests/test_smoke.sh"
    "${RACINE_PROJET}/scripts/docs/generer_documentation.sh"
  )
  local script_requis
  for script_requis in "${scripts_requis[@]}"; do
    [[ -x "${script_requis}" ]] \
      || arreter_sur_erreur "Script requis absent ou non executable: ${script_requis}"
  done
}

#######################################
# Verifie si l installation non interactive
# est possible avant le premier setup.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_installation_non_interactive_possible() {
  local forcer_installation="${BOOTSTRAP_FORCER_INSTALLATION:-0}"

  if [[ "${forcer_installation}" != "1" ]] && installation_initiale_deja_preparee; then
    return 0
  fi

  if [[ "${BORNE_MODE_TEST:-0}" == "1" ]]; then
    return 0
  fi

  if ! command -v apt-get >/dev/null 2>&1; then
    return 0
  fi

  if [[ "$(id -u)" -eq 0 ]] || sudo_non_interactif_disponible; then
    return 0
  fi

  if command -v sudo >/dev/null 2>&1 && [[ -t 0 ]]; then
    journaliser "Privilege systeme requis: validation sudo demandee avant l installation."
    sudo -v \
      || arreter_sur_erreur \
        "Impossible de valider sudo pour l installation systeme." \
        "Utilisez un compte membre sudo, lancez d abord 'sudo -v', puis relancez ./bootstrap_borne.sh."
    return 0
  fi

  arreter_sur_erreur \
    "Privileges systeme indisponibles pour l installation initiale." \
    "Lancez avec un compte root ou un compte sudo valide, puis relancez ./bootstrap_borne.sh."
}

#######################################
# Execute une etape avec journalisation
# homogene avant/apres.
# Arguments:
#   $1: nom etape
#   $2...: commande/fonction
# Retour:
#   0
#######################################
executer_etape_bootstrap() {
  local nom_etape="$1"
  shift

  ETAPE_BOOTSTRAP_COURANTE="${nom_etape}"
  journaliser "Bootstrap: ${nom_etape}"
  "$@"
  journaliser "Bootstrap: ${nom_etape}: OK"
}

#######################################
# Lance l installation initiale idempotente:
# dependances systeme detectees automatiquement, venv, dependances,
# permissions et autostart.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
executer_installation_initiale() {
  local forcer_installation="${BOOTSTRAP_FORCER_INSTALLATION:-0}"

  if [[ "${forcer_installation}" != "1" ]] && installation_initiale_deja_preparee; then
    journaliser "Installation initiale deja prete: etape ignoree (utilisez BOOTSTRAP_FORCER_INSTALLATION=1 pour forcer)."
    return 0
  fi

  DEBIAN_FRONTEND=noninteractive \
  APT_LISTCHANGES_FRONTEND=none \
  "${RACINE_PROJET}/scripts/install/installer_borne.sh"

  if [[ "${BORNE_MODE_TEST:-0}" != "1" ]]; then
    marquer_installation_initiale_prete
  fi
}

#######################################
# Lance la compilation globale de la borne.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
executer_compilation_globale() {
  executer_comme_utilisateur_appelant "${REPERTOIRE_BORNE}/compilation.sh"
}

#######################################
# Lance la suite lint.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
executer_lint_global() {
  executer_comme_utilisateur_appelant "${RACINE_PROJET}/scripts/lint/lancer_lint.sh"
}

#######################################
# Lance la suite smoke de verification.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
executer_tests_smoke() {
  executer_comme_utilisateur_appelant "${RACINE_PROJET}/scripts/tests/test_smoke.sh"
}

#######################################
# Genere la documentation du projet.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
executer_generation_documentation() {
  executer_comme_utilisateur_appelant "${RACINE_PROJET}/scripts/docs/generer_documentation.sh"
}

#######################################
# Normalise ownership/permissions apres
# bootstrap pour eviter les artefacts
# root non utilisables en session normale.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
normaliser_permissions_post_bootstrap() {
  local chemins_cibles=(
    "${RACINE_PROJET}/build"
    "${RACINE_PROJET}/logs"
    "${RACINE_PROJET}/.cache"
    "${RACINE_PROJET}/.venv"
    "${RACINE_PROJET}/site"
  )
  local chemin

  journaliser "Bootstrap: normalisation permissions finales"
  for chemin in "${chemins_cibles[@]}"; do
    [[ -e "${chemin}" ]] || continue

    if ! chmod -R a+rwX "${chemin}" 2>/dev/null; then
      journaliser "ATTENTION: impossible d appliquer chmod a+rwX sur ${chemin}."
    fi

    if [[ "$(id -u)" -eq 0 ]] && [[ "${UTILISATEUR_APPELANT_BOOTSTRAP}" != "root" ]]; then
      if ! chown -R "${UTILISATEUR_APPELANT_BOOTSTRAP}:${GROUPE_APPELANT_BOOTSTRAP}" "${chemin}" 2>/dev/null; then
        journaliser "ATTENTION: impossible d appliquer chown ${UTILISATEUR_APPELANT_BOOTSTRAP}:${GROUPE_APPELANT_BOOTSTRAP} sur ${chemin}."
      fi
    fi
  done
  journaliser "Bootstrap: normalisation permissions finales: OK"
}

#######################################
# Affiche un resume de fin de bootstrap.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
afficher_resume_bootstrap() {
  journaliser "Bootstrap termine avec succes."
  journaliser "Resume: dependances systeme+installation, compilation, lint, tests smoke, documentation."
  journaliser "Journal detaille: ${FICHIER_JOURNAL_BOOTSTRAP}"
}

#######################################
# Point d entree du bootstrap initial.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
main() {
  charger_configuration_borne
  verifier_execution_root_obligatoire
  initialiser_identite_appelant_bootstrap
  preparer_etat_bootstrap
  activer_journalisation_bootstrap
  trap 'gerer_echec_bootstrap "$?"' ERR
  trap liberer_verrou_bootstrap EXIT
  acquerir_verrou_bootstrap
  verifier_scripts_bootstrap
  verifier_installation_non_interactive_possible
  executer_etape_bootstrap "installation initiale" executer_installation_initiale
  executer_etape_bootstrap "compilation globale" executer_compilation_globale
  executer_etape_bootstrap "lint global" executer_lint_global
  executer_etape_bootstrap "tests smoke" executer_tests_smoke
  executer_etape_bootstrap "generation documentation" executer_generation_documentation
  normaliser_permissions_post_bootstrap
  trap - ERR
  afficher_resume_bootstrap
}

main "$@"
