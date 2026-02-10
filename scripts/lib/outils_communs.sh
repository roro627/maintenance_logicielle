#!/usr/bin/env bash
set -euo pipefail

CLASSPATH_MG2D_RESOLU=""

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
  CHEMIN_JAR_MG2D="${CHEMIN_JAR_MG2D:-${CHEMIN_MG2D}/MG2D.jar}"
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
  export CHEMIN_MG2D CHEMIN_JAR_MG2D DOSSIER_CACHE_MG2D_CLASSES COMMANDE_PYTHON DELAI_EXTINCTION_SECONDES CLAVIER_BORNE JEU_REFERENCE_TEST
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
  local fichier_temoin_cache="${DOSSIER_CACHE_MG2D_CLASSES}/.cache_mg2d_ok"
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
  if cache_mg2d_valide; then
    return 0
  fi

  rm -f "${fichier_temoin_cache}"
  find "${DOSSIER_CACHE_MG2D_CLASSES}" -type f -name '*.class' -delete
  javac -d "${DOSSIER_CACHE_MG2D_CLASSES}" "${sources_mg2d[@]}"
  touch "${fichier_temoin_cache}"
}

#######################################
# Verifie que le jar MG2D contient les
# classes minimales requises.
# Arguments:
#   aucun
# Retour:
#   0 si le jar est valide, 1 sinon
#######################################
jar_mg2d_valide() {
  local classes_requises=(
    "MG2D/Fenetre.class"
    "MG2D/Clavier.class"
    "MG2D/geometrie/Dessin.class"
    "MG2D/geometrie/Point.class"
  )
  local index_jar
  local classe

  [[ -f "${CHEMIN_JAR_MG2D}" ]] || return 1
  command -v jar >/dev/null 2>&1 || return 1

  index_jar="$(jar tf "${CHEMIN_JAR_MG2D}" 2>/dev/null)" || return 1
  for classe in "${classes_requises[@]}"; do
    printf '%s\n' "${index_jar}" | grep -Fxq "${classe}" || return 1
  done

  return 0
}

#######################################
# Verifie que le cache MG2D contient les
# classes requises et qu il est a jour.
# Arguments:
#   aucun
# Retour:
#   0 si le cache est valide, 1 sinon
#######################################
cache_mg2d_valide() {
  local repertoire_sources_mg2d="${CHEMIN_MG2D}/MG2D"
  local fichier_temoin_cache="${DOSSIER_CACHE_MG2D_CLASSES}/.cache_mg2d_ok"
  local classes_requises=(
    "MG2D/Fenetre.class"
    "MG2D/Clavier.class"
    "MG2D/geometrie/Dessin.class"
    "MG2D/geometrie/Point.class"
  )
  local classe
  local source_plus_recente

  [[ -d "${DOSSIER_CACHE_MG2D_CLASSES}" ]] || return 1
  [[ -f "${fichier_temoin_cache}" ]] || return 1
  [[ -d "${repertoire_sources_mg2d}" ]] || return 1

  for classe in "${classes_requises[@]}"; do
    [[ -f "${DOSSIER_CACHE_MG2D_CLASSES}/${classe}" ]] || return 1
  done

  source_plus_recente="$(find "${repertoire_sources_mg2d}" -type f -name '*.java' -newer "${fichier_temoin_cache}" -print -quit)"
  [[ -z "${source_plus_recente}" ]] || return 1

  return 0
}

#######################################
# Retourne le classpath MG2D a utiliser:
# jar valide en priorite, sinon cache.
# Arguments:
#   aucun
# Retour:
#   ecrit le classpath MG2D sur stdout
#######################################
obtenir_classpath_mg2d() {
  if [[ -n "${CLASSPATH_MG2D_RESOLU}" ]]; then
    echo "${CLASSPATH_MG2D_RESOLU}"
    return 0
  fi

  if jar_mg2d_valide; then
    CLASSPATH_MG2D_RESOLU="${CHEMIN_JAR_MG2D}"
    echo "${CLASSPATH_MG2D_RESOLU}"
    return 0
  fi

  preparer_classes_mg2d_cache
  CLASSPATH_MG2D_RESOLU="${DOSSIER_CACHE_MG2D_CLASSES}"
  echo "${CLASSPATH_MG2D_RESOLU}"
}
