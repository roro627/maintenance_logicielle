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
  [[ -f "${RACINE_PROJET}/docs/cost.md" ]] \
    || arreter_sur_erreur "Fichier docs/cost.md manquant"
}

#######################################
# Verifie la structure minimale de
# docs/cost.md et la presence d un total.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_structure_docs_couts() {
  local fichier_couts="${RACINE_PROJET}/docs/cost.md"
  grep -Eq "^# Suivi des couts" "${fichier_couts}" \
    || arreter_sur_erreur "Titre principal manquant dans docs/cost.md"
  grep -Eq "^## Objectif" "${fichier_couts}" \
    || arreter_sur_erreur "Section Objectif manquante dans docs/cost.md"
  grep -Eq "^## Methode d estimation" "${fichier_couts}" \
    || arreter_sur_erreur "Section methode d estimation manquante dans docs/cost.md"
  grep -Eq "^## Hypotheses de calcul" "${fichier_couts}" \
    || arreter_sur_erreur "Section hypotheses de calcul manquante dans docs/cost.md"
  grep -Fxq "| Poste | Quantite | Cout unitaire EUR | Total EUR | Temps h | Commentaire |" "${fichier_couts}" \
    || arreter_sur_erreur "Tableau couts manquant ou invalide dans docs/cost.md"
  grep -Fq "| Total |" "${fichier_couts}" \
    || arreter_sur_erreur "Ligne Total manquante dans docs/cost.md"
  grep -Eq "^### Temps" "${fichier_couts}" \
    || arreter_sur_erreur "Section detail temps manquante dans docs/cost.md"
  grep -Eq "^### Materiel" "${fichier_couts}" \
    || arreter_sur_erreur "Section detail materiel manquante dans docs/cost.md"
  grep -Eq "^### Licences" "${fichier_couts}" \
    || arreter_sur_erreur "Section detail licences manquante dans docs/cost.md"
}

#######################################
# Verifie la coherence entre la page
# docs/cost.md et l exigence de suivi.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_coherence_docs_couts() {
  local fichier_docs="${RACINE_PROJET}/docs/cost.md"
  grep -Fq "Suivi des couts" "${fichier_docs}" \
    || arreter_sur_erreur "Theme de suivi des couts absent de docs/cost.md"
  grep -Fq "temps, materiel, licences" "${fichier_docs}" \
    || arreter_sur_erreur "Portee couts incomplete dans docs/cost.md (temps, materiel, licences)"
  grep -Fq "Cout financier estime" "${fichier_docs}" \
    || arreter_sur_erreur "Resume financier absent dans docs/cost.md"
  grep -Fq "Charge estimee" "${fichier_docs}" \
    || arreter_sur_erreur "Resume charge absent dans docs/cost.md"
  grep -Fq "Projection budget global" "${fichier_docs}" \
    || arreter_sur_erreur "Projection budget global absente dans docs/cost.md"
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
  verifier_structure_docs_couts
  verifier_coherence_docs_couts
  journaliser "Test couts: OK"
}

main "$@"
