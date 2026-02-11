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
  RESOLUTION_X=1280
  RESOLUTION_Y=1024
  DOSSIER_BUILD_RACINE="${RACINE_PROJET}/build"
fi

DOSSIER_BUILD_RACINE="${DOSSIER_BUILD_RACINE:-${RACINE_PROJET}/build}"
DOSSIER_BUILD_CLASSES_JEUX="${DOSSIER_BUILD_CLASSES_JEUX:-${DOSSIER_BUILD_RACINE}/classes/jeux}"

#######################################
# Retourne le classpath MG2D optimal
# (jar valide sinon cache compile).
# Arguments:
#   aucun
# Retour:
#   ecrit le classpath sur stdout
#######################################
obtenir_classpath_mg2d_lancement() {
  if declare -F obtenir_classpath_mg2d >/dev/null 2>&1; then
    obtenir_classpath_mg2d
    return 0
  fi
  echo "${CHEMIN_MG2D}"
}

#######################################
# Retourne le dossier de classes Java
# compilees du jeu cible.
# Arguments:
#   $1: nom du jeu
# Retour:
#   ecrit le chemin dossier classes
#######################################
obtenir_dossier_classes_jeu_lancement() {
  local nom_jeu="$1"
  if declare -F obtenir_dossier_classes_jeu >/dev/null 2>&1; then
    obtenir_dossier_classes_jeu "${nom_jeu}"
    return 0
  fi
  echo "${DOSSIER_BUILD_CLASSES_JEUX}/${nom_jeu}"
}

#######################################
# Lance un jeu Java de la borne.
# Arguments:
#   $1: nom du dossier jeu
#   $2: classe principale
#   $3..n: options java supplementaires
# Retour:
#   code du processus java
#######################################
main() {
  local nom_jeu="$1"
  local classe_principale="$2"
  shift 2
  local options_java=("$@")
  local mode_smoke_test="${BORNE_MODE_TEST_JEU:-0}"
  local classpath_mg2d
  local dossier_classes_jeu

  local resolution_x="${RESOLUTION_X:-1280}"
  local resolution_y="${RESOLUTION_Y:-1024}"
  dossier_classes_jeu="$(obtenir_dossier_classes_jeu_lancement "${nom_jeu}")"

  if [[ "${mode_smoke_test}" == "1" ]]; then
    [[ -d "${SCRIPT_DIR}/projet/${nom_jeu}" ]] || {
      echo "ERREUR: Dossier jeu introuvable: ${nom_jeu}" >&2
      echo "ACTION RECOMMANDEE: verifiez le nom du jeu et la presence du dossier borne_arcade/projet/${nom_jeu}." >&2
      return 1
    }
    if [[ ! -f "${SCRIPT_DIR}/projet/${nom_jeu}/${classe_principale}.java" ]] \
      && [[ ! -f "${dossier_classes_jeu}/${classe_principale}.class" ]]; then
      echo "ERREUR: Classe principale introuvable pour ${nom_jeu}: ${classe_principale}" >&2
      echo "ACTION RECOMMANDEE: verifiez la classe d entree et recompilez avec ./borne_arcade/compilation.sh." >&2
      return 1
    fi
    return 0
  fi

  if command -v xdotool >/dev/null 2>&1; then
    xdotool mousemove "${resolution_x}" "${resolution_y}" || true
  fi

  classpath_mg2d="$(obtenir_classpath_mg2d_lancement)"
  if [[ ! -f "${dossier_classes_jeu}/${classe_principale}.class" ]]; then
    echo "ERREUR: Classes Java non generees pour ${nom_jeu} (${classe_principale}.class manquant)." >&2
    echo "ACTION RECOMMANDEE: lancez ./borne_arcade/compilation.sh puis relancez ${nom_jeu}.sh." >&2
    return 1
  fi

  cd "${SCRIPT_DIR}/projet/${nom_jeu}"
  touch highscore
  java "${options_java[@]}" -cp ".:${dossier_classes_jeu}:../..:${classpath_mg2d}" "${classe_principale}"
}

main "$@"
