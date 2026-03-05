#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

JEU_CIBLE="${1:-}"
if [[ "${JEU_CIBLE:-}" == "--jeu" ]]; then
  JEU_CIBLE="${2:-}"
fi

#######################################
# Retourne la liste des jeux Lua avec
# tests cibles pour cette suite.
# Arguments:
#   aucun
# Retour:
#   ecrit la liste sur stdout
#######################################
lister_jeux_lua_cibles() {
  printf '%s\n' "CursedWare"
}

#######################################
# Filtre la liste cible selon --jeu.
# Arguments:
#   aucun
# Retour:
#   ecrit la liste sur stdout
#######################################
lister_jeux_lua_selectionnes() {
  if [[ -n "${JEU_CIBLE}" ]]; then
    printf '%s\n' "${JEU_CIBLE}"
    return 0
  fi
  lister_jeux_lua_cibles
}

#######################################
# Retourne un interpreteur Lua standard
# si disponible.
# Arguments:
#   aucun
# Retour:
#   ecrit la commande detectee
#######################################
trouver_interpreteur_lua() {
  if command -v lua5.4 >/dev/null 2>&1; then
    echo "lua5.4"
    return 0
  fi
  if command -v lua5.3 >/dev/null 2>&1; then
    echo "lua5.3"
    return 0
  fi
  if command -v lua >/dev/null 2>&1; then
    echo "lua"
    return 0
  fi
  return 1
}

#######################################
# Retourne un compilateur Lua standard
# si disponible.
# Arguments:
#   aucun
# Retour:
#   ecrit la commande detectee
#######################################
trouver_compilateur_lua_cible() {
  if command -v luac5.4 >/dev/null 2>&1; then
    echo "luac5.4"
    return 0
  fi
  if command -v luac5.3 >/dev/null 2>&1; then
    echo "luac5.3"
    return 0
  fi
  if command -v luac >/dev/null 2>&1; then
    echo "luac"
    return 0
  fi
  return 1
}

#######################################
# Execute le test cible Lua d un jeu.
# Arguments:
#   $1: nom du jeu
# Retour:
#   0
#######################################
executer_test_lua_cible() {
  local nom_jeu="$1"
  local dossier_jeu="${REPERTOIRE_BORNE}/projet/${nom_jeu}"
  local fichiers_lua=()
  local fichier
  local compilateur_lua=""
  local interpreteur_lua=""

  case "${nom_jeu}" in
    CursedWare)
      while IFS= read -r fichier; do
        fichiers_lua+=("${fichier}")
      done < <(find "${dossier_jeu}" -type f -name '*.lua' -print | sort)
      ;;
    *)
      arreter_sur_erreur "Jeu Lua cible inconnu: ${nom_jeu}" "Utilisez un jeu Lua reference dans config/matrice_tests_jeux.json."
      ;;
  esac

  if compilateur_lua="$(trouver_compilateur_lua_cible)"; then
    local fichier_lua
    for fichier_lua in "${fichiers_lua[@]}"; do
      "${compilateur_lua}" -p "${fichier_lua}"
    done
  fi

  if interpreteur_lua="$(trouver_interpreteur_lua)"; then
    (
      cd "${dossier_jeu}"
      "${interpreteur_lua}" "./tests/test_contrat_minijeux.lua" minigames/*/game.lua
    )
  else
    (
      cd "${RACINE_PROJET}"
      "${COMMANDE_PYTHON}" ./scripts/tests/test_cursedware_minijeux.py
    )
  fi

  printf 'OK %s : test cible\n' "${nom_jeu}"
}

#######################################
# Point d entree des tests Lua cibles.
# Arguments:
#   --jeu <nom> optionnel
# Retour:
#   0
#######################################
main() {
  charger_configuration_borne
  local nom_jeu
  while IFS= read -r nom_jeu; do
    [[ -n "${nom_jeu}" ]] || continue
    executer_test_lua_cible "${nom_jeu}"
  done < <(lister_jeux_lua_selectionnes)

  if [[ -z "${JEU_CIBLE}" ]]; then
    journaliser "Tests jeux Lua cibles: OK"
  fi
}

main "$@"
