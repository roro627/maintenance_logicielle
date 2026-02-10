#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RACINE_PROJET="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [[ -f "${RACINE_PROJET}/scripts/lib/outils_communs.sh" ]]; then
  # shellcheck source=/dev/null
  source "${RACINE_PROJET}/scripts/lib/outils_communs.sh"
  charger_configuration_borne
else
  CHEMIN_MG2D="${RACINE_PROJET}/MG2D"
  DELAI_EXTINCTION_SECONDES=30
  CLAVIER_BORNE=borne
  EXTINCTION_AUTO=0
fi

CHEMIN_MG2D="${CHEMIN_MG2D:-${RACINE_PROJET}/MG2D}"
DELAI_EXTINCTION_SECONDES="${DELAI_EXTINCTION_SECONDES:-30}"
CLAVIER_BORNE="${CLAVIER_BORNE:-borne}"
EXTINCTION_AUTO="${EXTINCTION_AUTO:-0}"
CLASSPATH_MG2D=""

#######################################
# Prepare le classpath MG2D optimal
# (jar valide sinon cache compile).
# Arguments:
#   aucun
# Retour:
#   0
#######################################
preparer_classpath_mg2d_menu() {
  if declare -F obtenir_classpath_mg2d >/dev/null 2>&1; then
    CLASSPATH_MG2D="$(obtenir_classpath_mg2d)"
    return 0
  fi
  CLASSPATH_MG2D="${CHEMIN_MG2D}"
}

#######################################
# Applique le mapping clavier borne si disponible.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
appliquer_clavier_borne() {
  local chemin_layout_local="${HOME}/.xkb/symbols/${CLAVIER_BORNE}"

  if [[ -f "${SCRIPT_DIR}/${CLAVIER_BORNE}" && ! -f "${chemin_layout_local}" ]]; then
    mkdir -p "${HOME}/.xkb/symbols"
    cp "${SCRIPT_DIR}/${CLAVIER_BORNE}" "${chemin_layout_local}"
  fi

  if command -v setxkbmap >/dev/null 2>&1; then
    if [[ -f "${chemin_layout_local}" ]]; then
      setxkbmap -I"${HOME}/.xkb" "${CLAVIER_BORNE}" >/dev/null 2>&1 || true
    else
      setxkbmap "${CLAVIER_BORNE}" >/dev/null 2>&1 || true
    fi
  fi
}

#######################################
# Compile puis lance le menu principal.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
lancer_menu() {
  cd "${SCRIPT_DIR}"
  ./clean.sh
  ./compilation.sh
  preparer_classpath_mg2d_menu
  java -cp ".:${CLASSPATH_MG2D}" Main
}

#######################################
# Eteint la borne avec compte a rebours si active.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
compte_a_rebours_extinction() {
  local i
  for ((i=DELAI_EXTINCTION_SECONDES; i>=1; i--)); do
    echo "Extinction de la borne dans ${i} secondes"
    sleep 1
  done
  sudo halt
}

#######################################
# Point d entree du lanceur borne.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
main() {
  appliquer_clavier_borne
  lancer_menu
  ./clean.sh

  if [[ "${EXTINCTION_AUTO}" == "1" ]]; then
    compte_a_rebours_extinction
  fi
}

main "$@"
