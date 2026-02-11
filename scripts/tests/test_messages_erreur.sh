#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

#######################################
# Verifie qu une sortie d erreur contient
# un message clair et une action.
# Arguments:
#   $1: sortie texte
#   $2: contexte de verification
# Retour:
#   0
#######################################
verifier_structure_message_erreur() {
  local sortie="$1"
  local contexte="$2"

  [[ "${sortie}" == *"ERREUR:"* ]] \
    || arreter_sur_erreur "Message ERREUR absent pour ${contexte}" \
      "Ajoutez un message de type 'ERREUR: ...' dans ${contexte}."

  [[ "${sortie}" == *"ACTION RECOMMANDEE:"* ]] \
    || arreter_sur_erreur "Action recommandee absente pour ${contexte}" \
      "Ajoutez une ligne 'ACTION RECOMMANDEE: ...' explicite dans ${contexte}."
}

#######################################
# Execute une commande attendue en echec
# et retourne sa sortie combinee.
# Arguments:
#   $1..n: commande a executer
# Retour:
#   ecrit la sortie sur stdout
#######################################
executer_commande_en_echec() {
  local sortie
  local code_retour

  set +e
  sortie="$("$@" 2>&1)"
  code_retour=$?
  set -e

  [[ "${code_retour}" -ne 0 ]] \
    || arreter_sur_erreur "La commande de test devait echouer mais a reussi: $*" \
      "Ajustez le scenario de test pour declencher un chemin d erreur reel."

  printf '%s\n' "${sortie}"
}

#######################################
# Verifie la clarte de arreter_sur_erreur.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_arreter_sur_erreur() {
  local script_temporaire
  local sortie

  script_temporaire="$(mktemp)"
  cat > "${script_temporaire}" <<'SCRIPT'
#!/usr/bin/env bash
set -euo pipefail
RACINE_TEST="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "__CHEMIN_OUTILS_COMMUNS__"
arreter_sur_erreur "Echec intentionnel de test"
SCRIPT

  sed -i "s|__CHEMIN_OUTILS_COMMUNS__|${SCRIPT_DIR}/../lib/outils_communs.sh|g" "${script_temporaire}"
  chmod +x "${script_temporaire}"

  sortie="$(executer_commande_en_echec "${script_temporaire}")"
  verifier_structure_message_erreur "${sortie}" "arreter_sur_erreur"

  rm -f "${script_temporaire}"
}

#######################################
# Verifie la clarte des erreurs du
# lanceur Java en smoke test.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_lanceur_java() {
  local sortie
  sortie="$(executer_commande_en_echec env BORNE_MODE_TEST_JEU=1 "${REPERTOIRE_BORNE}/lancer_jeu_java.sh" "JeuInexistant" "Main")"
  verifier_structure_message_erreur "${sortie}" "lancer_jeu_java.sh"
}

#######################################
# Verifie la clarte des erreurs du
# lanceur Python en smoke test.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_lanceur_python() {
  local sortie
  sortie="$(executer_commande_en_echec env BORNE_MODE_TEST_JEU=1 "${REPERTOIRE_BORNE}/lancer_jeu_python.sh" "JeuInexistant" "main.py")"
  verifier_structure_message_erreur "${sortie}" "lancer_jeu_python.sh"
}

#######################################
# Verifie la clarte des erreurs du
# lanceur LOVE en smoke test.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_lanceur_love() {
  local sortie
  sortie="$(executer_commande_en_echec env BORNE_MODE_TEST_JEU=1 "${REPERTOIRE_BORNE}/lancer_jeu_love.sh" "JeuInexistant")"
  verifier_structure_message_erreur "${sortie}" "lancer_jeu_love.sh"
}

#######################################
# Point d entree du test messages erreur.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
main() {
  charger_configuration_borne
  verifier_arreter_sur_erreur
  verifier_lanceur_java
  verifier_lanceur_python
  verifier_lanceur_love
  journaliser "Test messages erreur: OK"
}

main "$@"
