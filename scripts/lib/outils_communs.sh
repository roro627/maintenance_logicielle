#!/usr/bin/env bash
set -euo pipefail

#######################################
# Retourne le chemin absolu de la racine du projet.
# Arguments:
#   aucun
# Retour:
#   ecrit la racine sur stdout
#######################################
obtenir_racine_projet() {
  local repertoire_script
  repertoire_script="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  cd "${repertoire_script}/../.." && pwd
}

#######################################
# Affiche un message horodate.
# Arguments:
#   $1: message
# Retour:
#   0
#######################################
journaliser() {
  local message="$1"
  printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "${message}"
}

#######################################
# Charge la configuration de la borne avec valeurs par defaut.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
charger_configuration_borne() {
  RACINE_PROJET="$(obtenir_racine_projet)"
  REPERTOIRE_BORNE="${RACINE_PROJET}/borne_arcade"
  FICHIER_CONFIG_BORNE="${REPERTOIRE_BORNE}/config/borne.env"
  FICHIER_VERSIONS_MINIMALES="${RACINE_PROJET}/config/versions_minimales.env"

  if [[ -f "${FICHIER_CONFIG_BORNE}" ]]; then
    # shellcheck source=/dev/null
    source "${FICHIER_CONFIG_BORNE}"
  fi
  if [[ -f "${FICHIER_VERSIONS_MINIMALES}" ]]; then
    # shellcheck source=/dev/null
    source "${FICHIER_VERSIONS_MINIMALES}"
  fi

  CHEMIN_MG2D="${CHEMIN_MG2D:-${RACINE_PROJET}/MG2D}"
  DOSSIER_CACHE_MG2D_CLASSES="${DOSSIER_CACHE_MG2D_CLASSES:-${RACINE_PROJET}/.cache/mg2d_classes}"
  COMMANDE_PYTHON="${COMMANDE_PYTHON:-python3}"
  UTILISER_VENV_PROJET="${UTILISER_VENV_PROJET:-1}"
  DELAI_EXTINCTION_SECONDES="${DELAI_EXTINCTION_SECONDES:-30}"
  CLAVIER_BORNE="${CLAVIER_BORNE:-borne}"
  JEU_REFERENCE_TEST="${JEU_REFERENCE_TEST:-NeonSumo}"
  RESOLUTION_X="${RESOLUTION_X:-1280}"
  RESOLUTION_Y="${RESOLUTION_Y:-1024}"
  JAVA_VERSION_MIN="${JAVA_VERSION_MIN:-17}"
  PYTHON_VERSION_MIN="${PYTHON_VERSION_MIN:-3.10}"
  PIP_VERSION_MIN="${PIP_VERSION_MIN:-24.0}"
  PYTEST_VERSION_MIN="${PYTEST_VERSION_MIN:-8.0}"
  MKDOCS_VERSION_MIN="${MKDOCS_VERSION_MIN:-1.5}"
  PYGAME_VERSION_MIN="${PYGAME_VERSION_MIN:-2.5}"
  LUA_VERSION_MIN="${LUA_VERSION_MIN:-5.3}"
  LOVE_VERSION_MIN="${LOVE_VERSION_MIN:-11.0}"
  VERSION_SHELLCHECK_OUTIL="${VERSION_SHELLCHECK_OUTIL:-0.10.0}"
  VERSION_CHECKSTYLE_OUTIL="${VERSION_CHECKSTYLE_OUTIL:-10.17.0}"
  VERSION_PYLINT_OUTIL="${VERSION_PYLINT_OUTIL:-3.3.1}"

  if [[ "${UTILISER_VENV_PROJET}" == "1" ]] && [[ -x "${RACINE_PROJET}/.venv/bin/python" ]]; then
    COMMANDE_PYTHON="${RACINE_PROJET}/.venv/bin/python"
  fi

  export RACINE_PROJET REPERTOIRE_BORNE FICHIER_CONFIG_BORNE FICHIER_VERSIONS_MINIMALES
  export CHEMIN_MG2D DOSSIER_CACHE_MG2D_CLASSES COMMANDE_PYTHON DELAI_EXTINCTION_SECONDES CLAVIER_BORNE JEU_REFERENCE_TEST
  export RESOLUTION_X RESOLUTION_Y
  export UTILISER_VENV_PROJET
  export JAVA_VERSION_MIN PYTHON_VERSION_MIN PIP_VERSION_MIN PYTEST_VERSION_MIN
  export MKDOCS_VERSION_MIN PYGAME_VERSION_MIN LUA_VERSION_MIN LOVE_VERSION_MIN
  export VERSION_SHELLCHECK_OUTIL VERSION_CHECKSTYLE_OUTIL VERSION_PYLINT_OUTIL
}

#######################################
# Termine le script avec un message d erreur.
# Arguments:
#   $1: message erreur
# Retour:
#   sort avec code 1
#######################################
arreter_sur_erreur() {
  local message="$1"
  journaliser "ERREUR: ${message}"
  exit 1
}

#######################################
# Compile les sources MG2D vers un cache
# pour eviter de modifier MG2D/.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
preparer_classes_mg2d_cache() {
  local repertoire_sources_mg2d="${CHEMIN_MG2D}/MG2D"
  local sources_mg2d=()
  local fichier

  [[ -d "${repertoire_sources_mg2d}" ]] \
    || arreter_sur_erreur "Repertoire MG2D introuvable: ${repertoire_sources_mg2d}"

  while IFS= read -r fichier; do
    sources_mg2d+=("${fichier}")
  done < <(find "${repertoire_sources_mg2d}" -type f -name '*.java' -print | sort)

  [[ "${#sources_mg2d[@]}" -gt 0 ]] \
    || arreter_sur_erreur "Aucune source Java MG2D detectee dans ${repertoire_sources_mg2d}"

  mkdir -p "${DOSSIER_CACHE_MG2D_CLASSES}"
  find "${DOSSIER_CACHE_MG2D_CLASSES}" -type f -name '*.class' -delete
  javac -d "${DOSSIER_CACHE_MG2D_CLASSES}" "${sources_mg2d[@]}"
}
