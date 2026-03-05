#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

#######################################
# Verifie la disponibilite de mkdocs.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_mkdocs_disponible() {
  "${COMMANDE_PYTHON}" -m mkdocs --version >/dev/null 2>&1 || arreter_sur_erreur "mkdocs introuvable"
}

#######################################
# Genere la documentation via mkdocs.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
generer_documentation() {
  rm -rf "${RACINE_PROJET}/site"
  "${COMMANDE_PYTHON}" -m mkdocs build -f "${RACINE_PROJET}/mkdocs.yml"
}

#######################################
# Point d entree du generateur de documentation.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
main() {
  charger_configuration_borne
  verifier_mkdocs_disponible
  generer_documentation
  journaliser "Documentation generee"
}

main "$@"
