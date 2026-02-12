#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

#######################################
# Verifie le pipeline post pull en mode test.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_pipeline_post_pull() {
  if [[ "${TEST_DEPLOIEMENT_SIMULATION:-0}" == "1" ]]; then
    BORNE_MODE_TEST=1 EVITER_TEST_DEPLOIEMENT=1 "${RACINE_PROJET}/scripts/deploiement/post_pull_update.sh"
  else
    EVITER_TEST_DEPLOIEMENT=1 "${RACINE_PROJET}/scripts/deploiement/post_pull_update.sh"
  fi
  [[ -f "${RACINE_PROJET}/.etat_derniere_maj" ]] || arreter_sur_erreur "Marqueur .etat_derniere_maj absent"
  [[ ! -f "${RACINE_PROJET}/.post_pull.lock" ]] || arreter_sur_erreur "Verrou .post_pull.lock non libere apres pipeline"
  find "${RACINE_PROJET}/logs" -maxdepth 1 -type f -name 'post_pull_update_*.log' | grep -q . \
    || arreter_sur_erreur "Journal post-pull absent dans logs/"
}

#######################################
# Verifie que les dossiers partages
# restent accessibles en ecriture.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_permissions_partagees() {
  local dossiers_partages=(
    "${RACINE_PROJET}/logs"
    "${RACINE_PROJET}/build"
    "${RACINE_PROJET}/.cache"
    "${RACINE_PROJET}/.venv"
    "${REPERTOIRE_BORNE}/projet"
  )
  local dossier
  for dossier in "${dossiers_partages[@]}"; do
    [[ -d "${dossier}" ]] || arreter_sur_erreur "Dossier partage manquant: ${dossier}"
    [[ -w "${dossier}" ]] \
      || arreter_sur_erreur \
        "Dossier non accessible en ecriture: ${dossier}" \
        "Relancez sudo ./bootstrap_borne.sh pour reappliquer les droits partages."
  done

  local sous_dossier_build_non_ecrivable=""
  sous_dossier_build_non_ecrivable="$(find "${RACINE_PROJET}/build" -type d ! -w -print -quit 2>/dev/null || true)"
  [[ -z "${sous_dossier_build_non_ecrivable}" ]] \
    || arreter_sur_erreur \
      "Sous-dossier build non accessible en ecriture: ${sous_dossier_build_non_ecrivable}" \
      "Relancez sudo ./bootstrap_borne.sh pour corriger ownership/permissions puis relancez le test."

  local scripts_critiques=(
    "${RACINE_PROJET}/bootstrap_borne.sh"
    "${RACINE_PROJET}/scripts/deploiement/post_pull_update.sh"
    "${RACINE_PROJET}/.githooks/post-merge"
    "${REPERTOIRE_BORNE}/lancerBorne.sh"
  )
  local script
  for script in "${scripts_critiques[@]}"; do
    [[ -x "${script}" ]] \
      || arreter_sur_erreur \
        "Script critique non executable: ${script}" \
        "Relancez sudo ./bootstrap_borne.sh pour restaurer les permissions d execution."
  done
}

#######################################
# Point d entree test deploiement.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
main() {
  charger_configuration_borne
  verifier_pipeline_post_pull
  verifier_permissions_partagees
  journaliser "Test deploiement: OK"
}

main "$@"
