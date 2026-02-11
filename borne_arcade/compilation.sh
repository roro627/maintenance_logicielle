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
  COMMANDE_PYTHON="python3"
fi

CHEMIN_MG2D="${CHEMIN_MG2D:-${RACINE_PROJET}/MG2D}"
COMMANDE_PYTHON="${COMMANDE_PYTHON:-python3}"
CLASSPATH_MG2D="${CHEMIN_MG2D}"
DOSSIER_BUILD_RACINE="${DOSSIER_BUILD_RACINE:-${RACINE_PROJET}/build}"
DOSSIER_BUILD_CLASSES_MENU="${DOSSIER_BUILD_CLASSES_MENU:-${DOSSIER_BUILD_RACINE}/classes/menu}"
DOSSIER_BUILD_CLASSES_JEUX="${DOSSIER_BUILD_CLASSES_JEUX:-${DOSSIER_BUILD_RACINE}/classes/jeux}"

#######################################
# Retourne le dossier de classes Java
# cible pour un jeu donne.
# Arguments:
#   $1: nom du jeu
# Retour:
#   ecrit le chemin du dossier classes
#######################################
obtenir_dossier_classes_jeu_compilation() {
  local nom_jeu="$1"
  if declare -F obtenir_dossier_classes_jeu >/dev/null 2>&1; then
    obtenir_dossier_classes_jeu "${nom_jeu}"
    return 0
  fi
  echo "${DOSSIER_BUILD_CLASSES_JEUX}/${nom_jeu}"
}

#######################################
# Prepare les dossiers de build Java.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
preparer_dossiers_build_java() {
  mkdir -p "${DOSSIER_BUILD_CLASSES_MENU}" "${DOSSIER_BUILD_CLASSES_JEUX}"
}

#######################################
# Trouve le compilateur Lua disponible.
# Arguments:
#   aucun
# Retour:
#   ecrit la commande detectee sur stdout
#######################################
trouver_compilateur_lua() {
  if command -v luac >/dev/null 2>&1; then
    echo "luac"
    return 0
  fi
  if command -v luac5.4 >/dev/null 2>&1; then
    echo "luac5.4"
    return 0
  fi
  if command -v luac5.3 >/dev/null 2>&1; then
    echo "luac5.3"
    return 0
  fi
  if command -v luac5.2 >/dev/null 2>&1; then
    echo "luac5.2"
    return 0
  fi
  return 1
}

#######################################
# Affiche un message clair quand aucun
# compilateur Lua n est detecte.
# Arguments:
#   $1: nom du jeu
# Retour:
#   0
#######################################
afficher_message_lua_indisponible() {
  local nom_jeu="$1"
  echo "ATTENTION: Aucun compilateur Lua detecte (luac, luac5.4, luac5.3, luac5.2)."
  echo "Verification Lua ignoree pour le jeu ${nom_jeu}."
  echo "Action recommandee: installez Lua 5.4 (ex: sudo apt install -y lua5.4)."
}

#######################################
# Prepare le classpath MG2D: jar valide
# prioritaire, sinon classes en cache.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
preparer_classpath_mg2d() {
  if declare -F obtenir_classpath_mg2d >/dev/null 2>&1; then
    CLASSPATH_MG2D="$(obtenir_classpath_mg2d)"
    return 0
  fi

  CLASSPATH_MG2D="${CHEMIN_MG2D}"
}

#######################################
# Compile les classes Java du menu principal.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
compiler_menu() {
  local fichiers_java=()
  local fichier
  while IFS= read -r fichier; do
    fichiers_java+=("${fichier}")
  done < <(find "${SCRIPT_DIR}" -maxdepth 1 -name '*.java' -print | sort)

  if [[ "${#fichiers_java[@]}" -eq 0 ]]; then
    echo "Aucun fichier Java a compiler dans le menu"
    return 0
  fi

  echo "Compilation du menu de la borne d arcade"
  rm -rf "${DOSSIER_BUILD_CLASSES_MENU}"
  mkdir -p "${DOSSIER_BUILD_CLASSES_MENU}"
  javac -d "${DOSSIER_BUILD_CLASSES_MENU}" -cp ".:${CLASSPATH_MG2D}" "${fichiers_java[@]}"
}

#######################################
# Compile les jeux Java et verifie la syntaxe Python/Lua
# presents dans borne_arcade/projet.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
compiler_jeux_java() {
  local dossier_jeu
  for dossier_jeu in "${SCRIPT_DIR}/projet"/*; do
    [[ -d "${dossier_jeu}" ]] || continue

    local nom_jeu
    nom_jeu="$(basename "${dossier_jeu}")"
    local dossier_classes_jeu=""
    dossier_classes_jeu="$(obtenir_dossier_classes_jeu_compilation "${nom_jeu}")"
    local fichiers_java=()
    local fichiers_python=()
    local fichiers_lua=()
    local a_valider=0
    local fichier
    while IFS= read -r fichier; do
      fichiers_java+=("${fichier}")
    done < <(find "${dossier_jeu}" -maxdepth 1 -name '*.java' -print | sort)
    while IFS= read -r fichier; do
      fichiers_python+=("${fichier}")
    done < <(find "${dossier_jeu}" -type f -name '*.py' -print | sort)
    while IFS= read -r fichier; do
      fichiers_lua+=("${fichier}")
    done < <(find "${dossier_jeu}" -type f -name '*.lua' -print | sort)

    if [[ "${#fichiers_java[@]}" -gt 0 ]]; then
      a_valider=1
      echo "Compilation Java du jeu ${nom_jeu}"
      rm -rf "${dossier_classes_jeu}"
      mkdir -p "${dossier_classes_jeu}"
      javac -d "${dossier_classes_jeu}" -cp ".:${SCRIPT_DIR}:../..:${CLASSPATH_MG2D}" "${fichiers_java[@]}"
    fi

    if [[ "${#fichiers_python[@]}" -gt 0 ]]; then
      a_valider=1
      echo "Verification Python du jeu ${nom_jeu}"
      "${COMMANDE_PYTHON}" - "${fichiers_python[@]}" <<'PYCODE'
import pathlib
import sys
import tokenize

def verifier_syntaxe_python(chemin_fichier):
    """Valide la syntaxe Python d un fichier sans generer de bytecode."""
    with tokenize.open(chemin_fichier) as flux:
        source = flux.read()
    compile(source, chemin_fichier, "exec")

def main():
    """Point d entree de la verification syntaxique."""
    for chemin in sys.argv[1:]:
        chemin_normalise = str(pathlib.Path(chemin))
        verifier_syntaxe_python(chemin_normalise)

if __name__ == "__main__":
    main()
PYCODE
    fi

    if [[ "${#fichiers_lua[@]}" -gt 0 ]]; then
      a_valider=1
      echo "Verification Lua du jeu ${nom_jeu}"
      local compilateur_lua
      if compilateur_lua="$(trouver_compilateur_lua)"; then
        local fichier_lua
        for fichier_lua in "${fichiers_lua[@]}"; do
          if ! "${compilateur_lua}" -p "${fichier_lua}"; then
            echo "ERREUR: Echec de verification Lua dans ${fichier_lua} avec ${compilateur_lua}." >&2
            echo "Corrigez la syntaxe du fichier puis relancez ./borne_arcade/compilation.sh." >&2
            return 1
          fi
        done
      else
        afficher_message_lua_indisponible "${nom_jeu}"
      fi
    fi

    if [[ "${a_valider}" -eq 0 ]]; then
      echo "Jeu ${nom_jeu} sans source Java/Python/Lua detectee: ignore"
    fi
  done
}

#######################################
# Point d entree de compilation.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
main() {
  preparer_classpath_mg2d
  preparer_dossiers_build_java
  compiler_menu
  compiler_jeux_java
}

main "$@"
