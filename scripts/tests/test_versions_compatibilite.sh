#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

#######################################
# Verifie Java, Python et outils Python principaux.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_versions_noyau() {
  local version_java
  local version_python
  local version_pip
  local version_pytest
  local version_mkdocs

  version_java="$(java -version 2>&1 | head -n 1 | sed -E 's/.*"([0-9]+(\.[0-9]+){0,2}).*/\1/')"
  version_python="$("${COMMANDE_PYTHON}" -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')"
  version_pip="$("${COMMANDE_PYTHON}" -m pip --version | awk '{print $2}')"
  version_pytest="$("${COMMANDE_PYTHON}" -m pytest --version 2>/dev/null | awk '{print $2}')"
  version_mkdocs="$("${COMMANDE_PYTHON}" -m mkdocs --version 2>/dev/null | sed -E 's/.* ([0-9]+(\.[0-9]+)+).*/\1/')"

  verifier_version_minimale "Java" "${version_java}" "${JAVA_VERSION_MIN}"
  verifier_version_minimale "Python" "${version_python}" "${PYTHON_VERSION_MIN}"
  verifier_version_minimale "pip" "${version_pip}" "${PIP_VERSION_MIN}"
  verifier_version_minimale "pytest" "${version_pytest}" "${PYTEST_VERSION_MIN}"
  verifier_version_minimale "mkdocs" "${version_mkdocs}" "${MKDOCS_VERSION_MIN}"
}

#######################################
# Verifie la version pygame pour les jeux Python.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_version_pygame() {
  local version_pygame
  version_pygame="$("${COMMANDE_PYTHON}" -c 'import pygame; print(pygame.version.ver)' 2>/dev/null)" \
    || arreter_sur_erreur "pygame introuvable"
  verifier_version_minimale "pygame" "${version_pygame}" "${PYGAME_VERSION_MIN}"
}

#######################################
# Retourne la version Lua detectee en
# privilegiant les binaires versionnes.
# Arguments:
#   aucun
# Retour:
#   ecrit la version detectee sur stdout
#######################################
obtenir_version_lua_disponible() {
  local commande_lua
  local version_lua
  local commandes_lua=(
    "lua5.4"
    "lua5.3"
    "luac5.4"
    "luac5.3"
    "lua"
    "luac"
  )

  for commande_lua in "${commandes_lua[@]}"; do
    command -v "${commande_lua}" >/dev/null 2>&1 || continue
    version_lua="$("${commande_lua}" -v 2>&1 | sed -E 's/.* ([0-9]+(\.[0-9]+)+).*/\1/')"
    [[ -n "${version_lua}" ]] || continue
    printf '%s\n' "${version_lua}"
    return 0
  done

  return 1
}

#######################################
# Verifie les versions Lua/Love si des jeux Lua sont presents.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_versions_lua_love() {
  local jeu_lua_present=0
  local version_lua=""
  local version_love=""
  local source_lua_detectee=""

  source_lua_detectee="$(find "${REPERTOIRE_BORNE}/projet" -type f -name '*.lua' -print -quit)"
  if [[ -n "${source_lua_detectee}" ]]; then
    jeu_lua_present=1
  fi
  [[ "${jeu_lua_present}" -eq 1 ]] || return 0

  if ! version_lua="$(obtenir_version_lua_disponible)"; then
    journaliser "Lua introuvable: verification version Lua ignoree"
    return 0
  fi
  verifier_version_minimale "Lua" "${version_lua}" "${LUA_VERSION_MIN}"

  if ! command -v love >/dev/null 2>&1; then
    arreter_sur_erreur \
      "LÖVE introuvable alors qu un jeu Lua est present." \
      "Installez love puis relancez scripts/tests/test_versions_compatibilite.sh."
  fi
  version_love="$(love --version 2>&1 | sed -E 's/.* ([0-9]+(\.[0-9]+)+).*/\1/')"
  verifier_version_minimale "LÖVE" "${version_love}" "${LOVE_VERSION_MIN}"
}

#######################################
# Point d entree test de compatibilite versions.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
main() {
  charger_configuration_borne
  verifier_versions_noyau
  verifier_version_pygame
  verifier_versions_lua_love
  journaliser "Test compatibilite versions: OK"
}

main "$@"
