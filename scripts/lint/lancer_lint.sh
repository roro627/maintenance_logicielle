#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

VERSION_SHELLCHECK_OUTIL="${VERSION_SHELLCHECK_OUTIL:-0.10.0}"
VERSION_CHECKSTYLE_OUTIL="${VERSION_CHECKSTYLE_OUTIL:-10.17.0}"
VERSION_PYLINT_OUTIL="${VERSION_PYLINT_OUTIL:-3.3.1}"
REPERTOIRE_OUTILS_LINT=""
COMMANDE_SHELLCHECK=()
COMMANDE_CHECKSTYLE=()
COMMANDE_PYLINT=()
REPERTOIRES_PYLINT=()

#######################################
# Telecharge un fichier avec curl ou wget.
# Arguments:
#   $1: URL source
#   $2: chemin destination
# Retour:
#   0 si succes, 1 sinon
#######################################
telecharger_fichier() {
  local url="$1"
  local destination="$2"

  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "${url}" -o "${destination}" && return 0
  fi

  if command -v wget >/dev/null 2>&1; then
    wget -q "${url}" -O "${destination}" && return 0
  fi

  return 1
}

#######################################
# Verifie qu'un outil de telechargement est disponible.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_outil_telechargement() {
  if ! command -v curl >/dev/null 2>&1 && ! command -v wget >/dev/null 2>&1; then
    arreter_sur_erreur "Ni curl ni wget disponible pour installer les outils de lint"
  fi
}

#######################################
# Prepare le repertoire local des outils de lint.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
preparer_repertoire_outils_lint() {
  REPERTOIRE_OUTILS_LINT="${RACINE_PROJET}/scripts/outils"
  mkdir -p "${REPERTOIRE_OUTILS_LINT}"
}

#######################################
# Assure la disponibilite de shellcheck.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
assurer_shellcheck() {
  if command -v shellcheck >/dev/null 2>&1; then
    COMMANDE_SHELLCHECK=(shellcheck)
    return 0
  fi

  local architecture
  local cible
  architecture="$(uname -m)"
  case "${architecture}" in
    x86_64) cible="linux.x86_64" ;;
    aarch64|arm64) cible="linux.aarch64" ;;
    *)
      arreter_sur_erreur "Architecture non supportee pour shellcheck auto: ${architecture}"
      ;;
  esac

  local dossier_shellcheck="${REPERTOIRE_OUTILS_LINT}/shellcheck"
  local archive_shellcheck="${dossier_shellcheck}/shellcheck-v${VERSION_SHELLCHECK_OUTIL}.${cible}.tar.xz"
  local dossier_extrait="${dossier_shellcheck}/shellcheck-v${VERSION_SHELLCHECK_OUTIL}"
  local binaire_shellcheck="${dossier_extrait}/shellcheck"
  local url_shellcheck="https://github.com/koalaman/shellcheck/releases/download/v${VERSION_SHELLCHECK_OUTIL}/shellcheck-v${VERSION_SHELLCHECK_OUTIL}.${cible}.tar.xz"

  mkdir -p "${dossier_shellcheck}"
  if [[ ! -f "${binaire_shellcheck}" ]]; then
    journaliser "Telechargement shellcheck ${VERSION_SHELLCHECK_OUTIL}"
    telecharger_fichier "${url_shellcheck}" "${archive_shellcheck}"
    tar -xJf "${archive_shellcheck}" -C "${dossier_shellcheck}"
    chmod +x "${binaire_shellcheck}"
  fi

  COMMANDE_SHELLCHECK=("${binaire_shellcheck}")
}

#######################################
# Assure la disponibilite de checkstyle.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
assurer_checkstyle() {
  if command -v checkstyle >/dev/null 2>&1; then
    COMMANDE_CHECKSTYLE=(checkstyle)
    return 0
  fi

  local dossier_checkstyle="${REPERTOIRE_OUTILS_LINT}/checkstyle"
  local version_candidate
  local -a versions_candidates=("${VERSION_CHECKSTYLE_OUTIL}" "10.16.0" "10.15.0")
  local jar_checkstyle=""
  local -a urls_checkstyle=()
  local url_checkstyle=""
  local archive_temporaire=""

  mkdir -p "${dossier_checkstyle}"

  for version_candidate in "${versions_candidates[@]}"; do
    jar_checkstyle="${dossier_checkstyle}/checkstyle-${version_candidate}-all.jar"
    if [[ -f "${jar_checkstyle}" ]]; then
      COMMANDE_CHECKSTYLE=(java -jar "${jar_checkstyle}")
      return 0
    fi

    urls_checkstyle=(
      "https://github.com/checkstyle/checkstyle/releases/download/checkstyle-${version_candidate}/checkstyle-${version_candidate}-all.jar"
      "https://repo1.maven.org/maven2/com/puppycrawl/tools/checkstyle/${version_candidate}/checkstyle-${version_candidate}-all.jar"
      "https://search.maven.org/remotecontent?filepath=com/puppycrawl/tools/checkstyle/${version_candidate}/checkstyle-${version_candidate}-all.jar"
    )

    archive_temporaire="${jar_checkstyle}.tmp"
    for url_checkstyle in "${urls_checkstyle[@]}"; do
      journaliser "Telechargement checkstyle ${version_candidate} depuis ${url_checkstyle}"
      if telecharger_fichier "${url_checkstyle}" "${archive_temporaire}"; then
        mv "${archive_temporaire}" "${jar_checkstyle}"
        COMMANDE_CHECKSTYLE=(java -jar "${jar_checkstyle}")
        return 0
      fi
      rm -f "${archive_temporaire}"
    done
  done

  arreter_sur_erreur "Impossible d'installer checkstyle (reseau ou depot indisponible)"
}

#######################################
# Assure la disponibilite de pylint via python -m.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
assurer_pylint() {
  if ! "${COMMANDE_PYTHON}" -c "import pylint" >/dev/null 2>&1; then
    journaliser "Installation pylint ${VERSION_PYLINT_OUTIL}"
    "${COMMANDE_PYTHON}" -m pip install "pylint==${VERSION_PYLINT_OUTIL}"
  fi

  "${COMMANDE_PYTHON}" -c "import pylint" >/dev/null 2>&1 \
    || arreter_sur_erreur "pylint indisponible apres installation"
  COMMANDE_PYLINT=("${COMMANDE_PYTHON}" -m pylint)
}

#######################################
# Charge les repertoires python a analyser.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
charger_repertoires_pylint() {
  local fichier_repertoires="${RACINE_PROJET}/config/pylint_repertoires.txt"
  local ligne=""
  local chemin_absolu=""

  REPERTOIRES_PYLINT=()
  if [[ ! -f "${fichier_repertoires}" ]]; then
    REPERTOIRES_PYLINT=(
      "${RACINE_PROJET}/scripts"
      "${REPERTOIRE_BORNE}/projet/NeonSumo"
    )
    return 0
  fi

  while IFS= read -r ligne || [[ -n "${ligne}" ]]; do
    ligne="${ligne#"${ligne%%[![:space:]]*}"}"
    ligne="${ligne%"${ligne##*[![:space:]]}"}"
    [[ -z "${ligne}" || "${ligne}" == \#* ]] && continue
    chemin_absolu="${RACINE_PROJET}/${ligne}"
    if [[ -d "${chemin_absolu}" ]]; then
      REPERTOIRES_PYLINT+=("${chemin_absolu}")
    else
      journaliser "Repertoire pylint ignore (introuvable): ${ligne}"
    fi
  done < "${fichier_repertoires}"

  if [[ "${#REPERTOIRES_PYLINT[@]}" -eq 0 ]]; then
    arreter_sur_erreur "Aucun repertoire python valide dans ${fichier_repertoires}"
  fi
}

#######################################
# Execute shellcheck sur les scripts maintenus.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
executer_shellcheck() {
  local fichiers
  mapfile -t fichiers < <(
    {
      find "${RACINE_PROJET}/scripts" -type f -name '*.sh'
      find "${REPERTOIRE_BORNE}" -maxdepth 1 -type f -name '*.sh'
      printf '%s\n' \
        "${RACINE_PROJET}/.githooks/post-merge"
    } | sort -u
  )

  if [[ "${#fichiers[@]}" -eq 0 ]]; then
    journaliser "Aucun script shell a verifier"
    return 0
  fi

  journaliser "Execution shellcheck"
  # Les scripts sourcent dynamiquement outils_communs.sh via SCRIPT_DIR.
  # Shellcheck ne peut pas toujours resoudre ce chemin de maniere statique.
  "${COMMANDE_SHELLCHECK[@]}" -x -e SC1091 "${fichiers[@]}"
}

#######################################
# Execute checkstyle sur les classes Java maintenues.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
executer_checkstyle() {
  local fichiers_java
  mapfile -t fichiers_java < <(
    {
      printf '%s\n' \
        "${REPERTOIRE_BORNE}/Main.java" \
        "${REPERTOIRE_BORNE}/ConstantesMenu.java" \
        "${REPERTOIRE_BORNE}/AnalyseurConfigJeu.java" \
        "${REPERTOIRE_BORNE}/Graphique.java" \
        "${REPERTOIRE_BORNE}/Bouton.java" \
        "${REPERTOIRE_BORNE}/Pointeur.java" \
        "${REPERTOIRE_BORNE}/BoiteDescription.java"
      find "${REPERTOIRE_BORNE}/tests/unit" -maxdepth 1 -type f -name '*.java'
    } | while IFS= read -r fichier; do
      [[ -f "${fichier}" ]] && printf '%s\n' "${fichier}"
    done | sort -u
  )

  if [[ "${#fichiers_java[@]}" -eq 0 ]]; then
    journaliser "Aucun fichier java cible pour checkstyle"
    return 0
  fi

  journaliser "Execution checkstyle"
  "${COMMANDE_CHECKSTYLE[@]}" -c "${RACINE_PROJET}/config/checkstyle.xml" "${fichiers_java[@]}"
}

#######################################
# Execute pylint sur les scripts python maintenus.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
executer_pylint() {
  charger_repertoires_pylint
  local fichiers_py
  local repertoire=""
  local -a fichiers_collectes=()
  for repertoire in "${REPERTOIRES_PYLINT[@]}"; do
    if [[ -d "${repertoire}" ]]; then
      while IFS= read -r fichier; do
        fichiers_collectes+=("${fichier}")
      done < <(find "${repertoire}" -type f -name '*.py')
    fi
  done
  mapfile -t fichiers_py < <(printf '%s\n' "${fichiers_collectes[@]}" | sort -u)

  if [[ "${#fichiers_py[@]}" -eq 0 ]]; then
    journaliser "Aucun fichier python cible pour pylint"
    return 0
  fi

  journaliser "Execution pylint"
  "${COMMANDE_PYLINT[@]}" --rcfile="${RACINE_PROJET}/.pylintrc" \
    --errors-only \
    --disable=no-member \
    "${fichiers_py[@]}"
}

#######################################
# Point d entree lint.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
main() {
  charger_configuration_borne
  preparer_repertoire_outils_lint
  verifier_outil_telechargement
  assurer_shellcheck
  assurer_checkstyle
  assurer_pylint
  executer_shellcheck
  executer_checkstyle
  executer_pylint
  journaliser "Lint termine"
}

main "$@"
