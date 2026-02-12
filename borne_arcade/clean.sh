#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RACINE_PROJET="$(cd "${SCRIPT_DIR}/.." && pwd)"
DOSSIER_BUILD_RACINE="${DOSSIER_BUILD_RACINE:-${RACINE_PROJET}/build}"

#######################################
# Verifie l acces en ecriture au dossier
# build avant nettoyage.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_acces_ecriture_build_clean() {
  local sous_dossier_non_ecrivable=""

  if [[ -f "${RACINE_PROJET}/scripts/lib/outils_communs.sh" ]]; then
    # shellcheck source=/dev/null
    source "${RACINE_PROJET}/scripts/lib/outils_communs.sh"
    charger_configuration_borne
    verifier_acces_ecriture_build
    return 0
  fi

  if [[ -d "${DOSSIER_BUILD_RACINE}" ]] && [[ ! -w "${DOSSIER_BUILD_RACINE}" ]]; then
    echo "ERREUR: Dossier build non accessible en ecriture: ${DOSSIER_BUILD_RACINE}" >&2
    echo "ACTION RECOMMANDEE: sudo chown -R \"${USER}:${USER}\" \"${DOSSIER_BUILD_RACINE}\" puis relancez ./borne_arcade/clean.sh." >&2
    return 1
  fi

  if [[ -d "${DOSSIER_BUILD_RACINE}" ]]; then
    sous_dossier_non_ecrivable="$(find "${DOSSIER_BUILD_RACINE}" -type d ! -w -print -quit 2>/dev/null || true)"
    if [[ -n "${sous_dossier_non_ecrivable}" ]]; then
      echo "ERREUR: Sous-dossier build non accessible en ecriture: ${sous_dossier_non_ecrivable}" >&2
      echo "ACTION RECOMMANDEE: sudo chown -R \"${USER}:${USER}\" \"${DOSSIER_BUILD_RACINE}\" puis relancez ./borne_arcade/clean.sh." >&2
      return 1
    fi
  fi
}

#######################################
# Nettoie les classes Java construites
# dans le dossier de build du projet.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
nettoyer_build_java() {
  rm -rf "${DOSSIER_BUILD_RACINE}/classes"
}

#######################################
# Supprime les fichiers de compilation et temporaires.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
nettoyer_classes_et_temporaires() {
  # Nettoyage de compatibilite des anciens artefacts in-place.
  find "${SCRIPT_DIR}" -type f \( -name '*.class' -o -name '*~' \) -delete
}

#######################################
# Point d entree du nettoyage.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
main() {
  verifier_acces_ecriture_build_clean
  nettoyer_build_java
  nettoyer_classes_et_temporaires
}

main "$@"
