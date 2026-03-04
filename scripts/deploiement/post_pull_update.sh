#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

FICHIER_VERROU_POST_PULL=""
FICHIER_JOURNAL_PIPELINE=""
VERROU_FICHIER_ACTIF=0

#######################################
# Selectionne un dossier de journaux
# accessible en ecriture pour ce run.
# Arguments:
#   aucun
# Retour:
#   ecrit le chemin du dossier logs
#######################################
selectionner_dossier_journaux_accessible() {
  local dossier_projet="${RACINE_PROJET}/logs"
  local dossier_repli_home="${HOME}/.cache/maintenance_logicielle/logs"
  local dossier_repli_tmp="${TMPDIR:-/tmp}/maintenance_logicielle_logs"

  mkdir -p "${dossier_projet}" 2>/dev/null || true
  chmod a+rwx "${dossier_projet}" 2>/dev/null || true
  if [[ -d "${dossier_projet}" && -w "${dossier_projet}" ]]; then
    printf '%s\n' "${dossier_projet}"
    return 0
  fi

  mkdir -p "${dossier_repli_home}" 2>/dev/null || true
  chmod a+rwx "${dossier_repli_home}" 2>/dev/null || true
  if [[ -d "${dossier_repli_home}" && -w "${dossier_repli_home}" ]]; then
    printf '%s\n' "${dossier_repli_home}"
    return 0
  fi

  mkdir -p "${dossier_repli_tmp}" 2>/dev/null || true
  chmod a+rwx "${dossier_repli_tmp}" 2>/dev/null || true
  if [[ -d "${dossier_repli_tmp}" && -w "${dossier_repli_tmp}" ]]; then
    printf '%s\n' "${dossier_repli_tmp}"
    return 0
  fi

  arreter_sur_erreur \
    "Aucun dossier de journalisation accessible en ecriture." \
    "Corrigez les droits du projet puis relancez sudo ./bootstrap_borne.sh."
}

#######################################
# Active la journalisation du pipeline
# vers un fichier horodate dedie.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
activer_journalisation_pipeline() {
  local dossier_journaux
  dossier_journaux="$(selectionner_dossier_journaux_accessible)"
  FICHIER_JOURNAL_PIPELINE="${dossier_journaux}/post_pull_update_$(date '+%Y%m%d_%H%M%S').log"
  exec > >(tee -a "${FICHIER_JOURNAL_PIPELINE}") 2>&1
  if [[ "${dossier_journaux}" != "${RACINE_PROJET}/logs" ]]; then
    journaliser "ATTENTION: logs projet non accessibles, journal ecrit dans ${dossier_journaux}."
  fi
  journaliser "Journal pipeline: ${FICHIER_JOURNAL_PIPELINE}"
}

#######################################
# Acquiert un verrou pour eviter
# l execution concurrente du pipeline.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
acquerir_verrou_post_pull() {
  FICHIER_VERROU_POST_PULL="${RACINE_PROJET}/.post_pull.lock"

  if command -v flock >/dev/null 2>&1; then
    exec 9>"${FICHIER_VERROU_POST_PULL}"
    if ! flock -n 9; then
      arreter_sur_erreur \
        "Un autre pipeline post-pull est deja en cours." \
        "Attendez la fin du pipeline en cours puis relancez scripts/deploiement/post_pull_update.sh."
    fi
    VERROU_FICHIER_ACTIF=1
    return 0
  fi

  if [[ -f "${FICHIER_VERROU_POST_PULL}" ]]; then
    arreter_sur_erreur \
      "Verrou post-pull detecte mais flock est indisponible." \
      "Supprimez ${FICHIER_VERROU_POST_PULL} uniquement si aucun pipeline n est en cours."
  fi

  date '+%Y-%m-%d %H:%M:%S' > "${FICHIER_VERROU_POST_PULL}"
  VERROU_FICHIER_ACTIF=1
}

#######################################
# Libere le verrou du pipeline.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
liberer_verrou_post_pull() {
  if [[ "${VERROU_FICHIER_ACTIF}" -eq 1 ]] && [[ -n "${FICHIER_VERROU_POST_PULL}" ]]; then
    rm -f "${FICHIER_VERROU_POST_PULL}" || true
  fi
  flock -u 9 >/dev/null 2>&1 || true
  exec 9>&- || true
}

#######################################
# Affiche une erreur de pipeline claire
# puis termine avec le code d erreur.
# Arguments:
#   $1: code retour original
# Retour:
#   sort avec le code d erreur
#######################################
gerer_echec_pipeline() {
  local code_retour="${1:-1}"
  afficher_erreur_claire \
    "Echec du pipeline post-pull (code=${code_retour})." \
    "Consultez ${FICHIER_JOURNAL_PIPELINE}, corrigez l erreur puis relancez scripts/deploiement/post_pull_update.sh."
  exit "${code_retour}"
}

#######################################
# Execute la sequence de mise a jour post pull.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
executer_pipeline_post_pull() {
  journaliser "Pipeline post-pull: installation"
  INSTALLATION_SYSTEME_OPTIONNEL=1 "${RACINE_PROJET}/scripts/install/installer_borne.sh"

  journaliser "Pipeline post-pull: compilation"
  "${REPERTOIRE_BORNE}/compilation.sh"

  journaliser "Pipeline post-pull: lint"
  "${RACINE_PROJET}/scripts/lint/lancer_lint.sh"

  journaliser "Pipeline post-pull: tests"
  EVITER_TEST_DEPLOIEMENT=1 "${RACINE_PROJET}/scripts/tests/lancer_suite.sh"

  journaliser "Pipeline post-pull: documentation"
  "${RACINE_PROJET}/scripts/docs/generer_documentation.sh"

  date '+%Y-%m-%d %H:%M:%S' > "${RACINE_PROJET}/.etat_derniere_maj"
}

#######################################
# Point d entree du script post pull.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
main() {
  charger_configuration_borne
  activer_journalisation_pipeline
  trap 'gerer_echec_pipeline "$?"' ERR
  trap liberer_verrou_post_pull EXIT
  acquerir_verrou_post_pull
  executer_pipeline_post_pull
  trap - ERR
  journaliser "Mise a jour post-pull terminee"
}

main "$@"
