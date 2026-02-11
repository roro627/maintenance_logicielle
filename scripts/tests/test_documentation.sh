#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

#######################################
# Genere et verifie les artefacts documentaires.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_generation_documentation() {
  "${RACINE_PROJET}/scripts/docs/generer_documentation.sh"
  [[ -d "${RACINE_PROJET}/site" ]] || arreter_sur_erreur "Repertoire site absent"
  [[ -f "${RACINE_PROJET}/site/index.html" ]] || arreter_sur_erreur "Index HTML de documentation absent"
  [[ -f "${RACINE_PROJET}/site/architecture/index.html" ]] || arreter_sur_erreur "Guide architecture non genere"
  [[ -f "${RACINE_PROJET}/site/installation/index.html" ]] || arreter_sur_erreur "Guide installation non genere"
  [[ -f "${RACINE_PROJET}/site/deploiement/index.html" ]] || arreter_sur_erreur "Guide deploiement non genere"
  [[ -f "${RACINE_PROJET}/site/tests/index.html" ]] || arreter_sur_erreur "Guide tests non genere"
  [[ -f "${RACINE_PROJET}/site/ajout_jeu/index.html" ]] || arreter_sur_erreur "Guide ajout de jeu non genere"
  [[ -f "${RACINE_PROJET}/site/technique/index.html" ]] || arreter_sur_erreur "Documentation technique non generee"
  [[ -f "${RACINE_PROJET}/site/utilisateur/index.html" ]] || arreter_sur_erreur "Guide utilisateur non genere"
  [[ -f "${RACINE_PROJET}/site/validation_materielle/index.html" ]] || arreter_sur_erreur "Validation materielle non generee"
  [[ -f "${RACINE_PROJET}/site/compatibilite_dependances/index.html" ]] || arreter_sur_erreur "Guide compatibilite dependances non genere"
  [[ -f "${RACINE_PROJET}/site/couts/index.html" ]] || arreter_sur_erreur "Guide couts non genere"
  [[ -f "${RACINE_PROJET}/site/rendu/index.html" ]] || arreter_sur_erreur "Guide rendu final non genere"
}

#######################################
# Point d entree test documentation.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
main() {
  charger_configuration_borne
  verifier_generation_documentation
  journaliser "Test documentation: OK"
}

main "$@"
