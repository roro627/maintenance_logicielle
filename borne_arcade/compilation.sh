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
fi

CHEMIN_MG2D="${CHEMIN_MG2D:-${RACINE_PROJET}/MG2D}"

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
  javac -cp ".:${CHEMIN_MG2D}" "${fichiers_java[@]}"
}

#######################################
# Compile les jeux Java presents dans borne_arcade/projet.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
compiler_jeux_java() {
  local dossier_jeu
  for dossier_jeu in "${SCRIPT_DIR}/projet"/*; do
    [[ -d "${dossier_jeu}" ]] || continue

    local fichiers_java=()
    local fichier
    while IFS= read -r fichier; do
      fichiers_java+=("${fichier}")
    done < <(find "${dossier_jeu}" -maxdepth 1 -name '*.java' -print | sort)

    if [[ "${#fichiers_java[@]}" -eq 0 ]]; then
      echo "Jeu $(basename "${dossier_jeu}") sans sources Java: ignore"
      continue
    fi

    echo "Compilation du jeu $(basename "${dossier_jeu}")"
    javac -cp ".:${SCRIPT_DIR}:../..:${CHEMIN_MG2D}" "${fichiers_java[@]}"
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
  compiler_menu
  compiler_jeux_java
}

main "$@"
