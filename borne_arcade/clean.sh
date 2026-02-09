#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

#######################################
# Supprime les fichiers de compilation et temporaires.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
nettoyer_classes_et_temporaires() {
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
  nettoyer_classes_et_temporaires
}

main "$@"
