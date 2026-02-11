#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RACINE_PROJET="$(cd "${SCRIPT_DIR}/.." && pwd)"
DOSSIER_BUILD_RACINE="${DOSSIER_BUILD_RACINE:-${RACINE_PROJET}/build}"

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
  nettoyer_build_java
  nettoyer_classes_et_temporaires
}

main "$@"
