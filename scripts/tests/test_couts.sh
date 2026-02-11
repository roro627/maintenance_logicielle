#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

#######################################
# Verifie l existence des fichiers
# de suivi des couts.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_fichiers_couts() {
  [[ -f "${RACINE_PROJET}/cost.md" ]] \
    || arreter_sur_erreur "Fichier cost.md manquant a la racine"
  [[ -f "${RACINE_PROJET}/docs/couts.md" ]] \
    || arreter_sur_erreur "Fichier docs/couts.md manquant"
}

#######################################
# Verifie la structure minimale de
# cost.md et la presence d un total.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_structure_cost_md() {
  local fichier_cost="${RACINE_PROJET}/cost.md"
  rg -q "^# Suivi des couts" "${fichier_cost}" \
    || arreter_sur_erreur "Titre principal manquant dans cost.md"
  rg -q "^## Methode d estimation" "${fichier_cost}" \
    || arreter_sur_erreur "Section methode d estimation manquante dans cost.md"
  rg -q "^## Hypotheses de calcul" "${fichier_cost}" \
    || arreter_sur_erreur "Section hypotheses de calcul manquante dans cost.md"
  rg -q "^\| Poste \| Quantite \| Cout unitaire EUR \| Total EUR \| Temps h \| Commentaire \|$" "${fichier_cost}" \
    || arreter_sur_erreur "Tableau couts manquant ou invalide dans cost.md"
  rg -q "^\| Total \|" "${fichier_cost}" \
    || arreter_sur_erreur "Ligne Total manquante dans cost.md"
  rg -q "^### Temps" "${fichier_cost}" \
    || arreter_sur_erreur "Section detail temps manquante dans cost.md"
  rg -q "^### Materiel" "${fichier_cost}" \
    || arreter_sur_erreur "Section detail materiel manquante dans cost.md"
  rg -q "^### Licences" "${fichier_cost}" \
    || arreter_sur_erreur "Section detail licences manquante dans cost.md"
}

#######################################
# Verifie la coherence entre la page
# docs/couts.md et la source cost.md.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_coherence_docs_couts() {
  local fichier_docs="${RACINE_PROJET}/docs/couts.md"
  rg -q "cost.md" "${fichier_docs}" \
    || arreter_sur_erreur "docs/couts.md ne reference pas cost.md"
  rg -q "Cout financier estime" "${fichier_docs}" \
    || arreter_sur_erreur "Resume financier absent dans docs/couts.md"
  rg -q "Charge estimee" "${fichier_docs}" \
    || arreter_sur_erreur "Resume charge absent dans docs/couts.md"
  rg -q "Projection budget global" "${fichier_docs}" \
    || arreter_sur_erreur "Projection budget global absente dans docs/couts.md"
}

#######################################
# Point d entree test couts.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
main() {
  charger_configuration_borne
  verifier_fichiers_couts
  verifier_structure_cost_md
  verifier_coherence_docs_couts
  journaliser "Test couts: OK"
}

main "$@"
