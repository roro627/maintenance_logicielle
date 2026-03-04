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
  DOSSIER_ARCHIVES="${DOSSIER_ARCHIVES:-${RACINE_PROJET}/archives}"
  DOSSIER_BUILD_RACINE="${DOSSIER_BUILD_RACINE:-${RACINE_PROJET}/build}"
  DOSSIER_BUILD_CLASSES_MENU="${DOSSIER_BUILD_CLASSES_MENU:-${DOSSIER_BUILD_RACINE}/classes/menu}"
  DOSSIER_BUILD_CLASSES_JEUX="${DOSSIER_BUILD_CLASSES_JEUX:-${DOSSIER_BUILD_RACINE}/classes/jeux}"
  DOSSIER_BUILD_CLASSES_TESTS="${DOSSIER_BUILD_CLASSES_TESTS:-${DOSSIER_BUILD_RACINE}/classes/tests}"
  DOSSIER_CACHE_MG2D_CLASSES="${DOSSIER_CACHE_MG2D_CLASSES:-${RACINE_PROJET}/.cache/mg2d_classes}"
  COMMANDE_PYTHON="${COMMANDE_PYTHON:-python3}"
  ENCODAGE_SOURCES_JAVA="${ENCODAGE_SOURCES_JAVA:-UTF-8}"
  UTILISER_VENV_PROJET="${UTILISER_VENV_PROJET:-1}"
  DELAI_EXTINCTION_SECONDES="${DELAI_EXTINCTION_SECONDES:-30}"
  CLAVIER_BORNE="${CLAVIER_BORNE:-borne}"
  JEU_REFERENCE_TEST="${JEU_REFERENCE_TEST:-NeonSumo}"
  RESOLUTION_X="${RESOLUTION_X:-1280}"
  RESOLUTION_Y="${RESOLUTION_Y:-1024}"
  MODE_AFFICHAGE_BORNE="${MODE_AFFICHAGE_BORNE:-fenetre_sans_bordure}"
  POSITION_FENETRE_X="${POSITION_FENETRE_X:-0}"
  POSITION_FENETRE_Y="${POSITION_FENETRE_Y:-0}"
  JAVA_VERSION_MIN="${JAVA_VERSION_MIN:-17}"
  PYTHON_VERSION_MIN="${PYTHON_VERSION_MIN:-3.10}"
  PIP_VERSION_MIN="${PIP_VERSION_MIN:-24.0}"
  PYTEST_VERSION_MIN="${PYTEST_VERSION_MIN:-8.0}"
  MKDOCS_VERSION_MIN="${MKDOCS_VERSION_MIN:-1.5}"
  PYGAME_VERSION_MIN="${PYGAME_VERSION_MIN:-2.5}"
  LUA_VERSION_MIN="${LUA_VERSION_MIN:-5.3}"
  LOVE_VERSION_MIN="${LOVE_VERSION_MIN:-11.0}"
  NODE_VERSION_MIN_CODEX="${NODE_VERSION_MIN_CODEX:-16.0}"
  VERSION_SHELLCHECK_OUTIL="${VERSION_SHELLCHECK_OUTIL:-0.10.0}"
  VERSION_CHECKSTYLE_OUTIL="${VERSION_CHECKSTYLE_OUTIL:-10.17.0}"
  VERSION_PYLINT_OUTIL="${VERSION_PYLINT_OUTIL:-3.3.1}"
  VERSION_ACT_OUTIL="${VERSION_ACT_OUTIL:-0.2.84}"
  VERSION_NODE_SOURCE_MAJEURE="${VERSION_NODE_SOURCE_MAJEURE:-22}"

  if [[ "${UTILISER_VENV_PROJET}" == "1" ]] && [[ -x "${RACINE_PROJET}/.venv/bin/python" ]]; then
    COMMANDE_PYTHON="${RACINE_PROJET}/.venv/bin/python"
  fi

  export RACINE_PROJET REPERTOIRE_BORNE FICHIER_CONFIG_BORNE FICHIER_VERSIONS_MINIMALES
  export CHEMIN_MG2D CHEMIN_JAR_MG2D DOSSIER_ARCHIVES DOSSIER_BUILD_RACINE
  export DOSSIER_BUILD_CLASSES_MENU DOSSIER_BUILD_CLASSES_JEUX DOSSIER_BUILD_CLASSES_TESTS
  export DOSSIER_CACHE_MG2D_CLASSES COMMANDE_PYTHON ENCODAGE_SOURCES_JAVA DELAI_EXTINCTION_SECONDES CLAVIER_BORNE JEU_REFERENCE_TEST
  export RESOLUTION_X RESOLUTION_Y
  export MODE_AFFICHAGE_BORNE POSITION_FENETRE_X POSITION_FENETRE_Y
  export UTILISER_VENV_PROJET
  export JAVA_VERSION_MIN PYTHON_VERSION_MIN PIP_VERSION_MIN PYTEST_VERSION_MIN
  export MKDOCS_VERSION_MIN PYGAME_VERSION_MIN LUA_VERSION_MIN LOVE_VERSION_MIN NODE_VERSION_MIN_CODEX
  export VERSION_SHELLCHECK_OUTIL VERSION_CHECKSTYLE_OUTIL VERSION_PYLINT_OUTIL VERSION_ACT_OUTIL VERSION_NODE_SOURCE_MAJEURE
}

#######################################
# Prepare les variables d affichage
# partagees pour les jeux SDL/pygame.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
preparer_environnement_affichage_sdl() {
  export BORNE_RESOLUTION_X="${RESOLUTION_X:-1280}"
  export BORNE_RESOLUTION_Y="${RESOLUTION_Y:-1024}"
  export BORNE_MODE_AFFICHAGE="${MODE_AFFICHAGE_BORNE:-fenetre_sans_bordure}"
  export BORNE_POSITION_FENETRE_X="${POSITION_FENETRE_X:-0}"
  export BORNE_POSITION_FENETRE_Y="${POSITION_FENETRE_Y:-0}"
  export SDL_VIDEO_WINDOW_POS="${BORNE_POSITION_FENETRE_X},${BORNE_POSITION_FENETRE_Y}"
  export SDL_VIDEO_CENTERED=0
}

#######################################
# Retourne le dossier de classes Java
# compilees pour un jeu donne.
# Arguments:
#   $1: nom du jeu
# Retour:
#   ecrit le chemin du dossier classes
#######################################
obtenir_dossier_classes_jeu() {
  local nom_jeu="$1"
  echo "${DOSSIER_BUILD_CLASSES_JEUX}/${nom_jeu}"
}

#######################################
# Affiche une erreur claire et actionnable.
# Arguments:
#   $1: message erreur
#   $2: action recommandee (optionnel)
# Retour:
#   0
#######################################
afficher_erreur_claire() {
  local message="$1"
  local action="${2:-Corrigez la cause indiquee puis relancez la commande: ${0##*/}}"
  journaliser "ERREUR: ${message}"
  journaliser "ACTION RECOMMANDEE: ${action}"
}

#######################################
# Termine le script avec une erreur claire.
# Arguments:
#   $1: message erreur
#   $2: action recommandee (optionnel)
# Retour:
#   sort avec code 1
#######################################
arreter_sur_erreur() {
  local message="$1"
  local action="${2:-}"
  afficher_erreur_claire "${message}" "${action}"
  exit 1
}

#######################################
# Execute un script shell meme sans
# bit executable versionne dans Git.
# Arguments:
#   $1: chemin du script shell
#   $2...: arguments du script
# Retour:
#   code retour du script
#######################################
executer_script_shell() {
  local chemin_script="$1"
  shift || true

  [[ -f "${chemin_script}" ]] \
    || arreter_sur_erreur "Script shell introuvable: ${chemin_script}"

  bash "${chemin_script}" "$@"
}

#######################################
# Applique un chmod sur une liste de
# cibles sans echouer si un element
# est non modifiable.
# Arguments:
#   $1: mode chmod
#   $2..n: chemins cibles
# Retour:
#   0
#######################################
appliquer_chmod_si_possible() {
  local mode="$1"
  shift
  local cible
  for cible in "$@"; do
    [[ -e "${cible}" ]] || continue
    [[ -L "${cible}" ]] && continue
    if ! chmod "${mode}" "${cible}" 2>/dev/null; then
      journaliser "ATTENTION: impossible d appliquer chmod ${mode} sur ${cible}."
    fi
  done
}

#######################################
# Liste les chemins du projet qui
# peuvent etre normalises sans toucher
# au depot Git ni au miroir MG2D.
# Arguments:
#   $1...: predicats find supplementaires
# Retour:
#   ecrit les chemins sur stdout
#######################################
lister_chemins_normalisables_borne() {
  find "${RACINE_PROJET}" \
    \( -path "${RACINE_PROJET}/.git" -o -path "${CHEMIN_MG2D}" \) -prune -o \
    "$@"
}

#######################################
# Normalise les permissions partagees
# et d execution des chemins utiles
# a l exploitation de la borne.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
normaliser_permissions_exploitation_borne() {
  local chemins_partages=(
    "${RACINE_PROJET}"
    "${RACINE_PROJET}/logs"
    "${RACINE_PROJET}/build"
    "${RACINE_PROJET}/.cache"
    "${RACINE_PROJET}/.venv"
    "${RACINE_PROJET}/site"
    "${RACINE_PROJET}/scripts"
    "${RACINE_PROJET}/.githooks"
    "${RACINE_PROJET}/config"
    "${RACINE_PROJET}/docs"
    "${RACINE_PROJET}/.github"
    "${REPERTOIRE_BORNE}"
    "${REPERTOIRE_BORNE}/projet"
  )
  local chemin
  local script

  journaliser "Configuration des permissions partagees sur tout le depot exploitable"
  mkdir -p "${RACINE_PROJET}/logs" "${RACINE_PROJET}/build" "${RACINE_PROJET}/.cache"

  for chemin in "${chemins_partages[@]}"; do
    [[ -d "${chemin}" ]] || continue
    appliquer_chmod_si_possible a+rwx "${chemin}"
  done

  while IFS= read -r chemin; do
    appliquer_chmod_si_possible a+rwX "${chemin}"
  done < <(lister_chemins_normalisables_borne -mindepth 1 -print 2>/dev/null | sort)

  while IFS= read -r script; do
    appliquer_chmod_si_possible a+rwx "${script}"
  done < <(lister_chemins_normalisables_borne -type f -name '*.sh' -print 2>/dev/null | sort)
}

#######################################
# Compare deux versions numeriques.
# Arguments:
#   $1: version detectee
#   $2: version minimale
# Retour:
#   0 si $1 >= $2, 1 sinon
#######################################
version_minimale_respectee() {
  local version_detectee="$1"
  local version_minimale="$2"
  local commande_python_versions="${COMMANDE_PYTHON:-python3}"

  "${commande_python_versions}" - "${version_detectee}" "${version_minimale}" <<'PY'
import re
import sys


def parser(version):
    """Retourne les composantes numeriques d une version."""
    valeurs = [int(x) for x in re.findall(r"\d+", version)]
    return tuple(valeurs)


version_detectee = parser(sys.argv[1])
version_minimale = parser(sys.argv[2])
taille = max(len(version_detectee), len(version_minimale))
version_detectee += (0,) * (taille - len(version_detectee))
version_minimale += (0,) * (taille - len(version_minimale))
sys.exit(0 if version_detectee >= version_minimale else 1)
PY
}

#######################################
# Verifie une version detectee contre
# une version minimale.
# Arguments:
#   $1: libelle
#   $2: version detectee
#   $3: version minimale
# Retour:
#   0
#######################################
verifier_version_minimale() {
  local libelle="$1"
  local version_detectee="$2"
  local version_minimale="$3"

  version_minimale_respectee "${version_detectee}" "${version_minimale}" \
    || arreter_sur_erreur "Version ${libelle} incompatible: detectee=${version_detectee}, minimum=${version_minimale}"
}

#######################################
# Verifie que le dossier build est
# accessible en ecriture par l utilisateur
# courant, puis le cree si necessaire.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_acces_ecriture_build() {
  local dossier_build="${DOSSIER_BUILD_RACINE:-${RACINE_PROJET}/build}"
  local dossier_parent_build=""
  local sous_dossier_non_ecrivable=""

  if [[ -d "${dossier_build}" ]]; then
    [[ -w "${dossier_build}" ]] \
      || arreter_sur_erreur \
        "Dossier build non accessible en ecriture: ${dossier_build}" \
        "Recuperez les droits avec: sudo chown -R \"${USER}:${USER}\" \"${dossier_build}\" puis relancez la commande."

    sous_dossier_non_ecrivable="$(find "${dossier_build}" -type d ! -w -print -quit 2>/dev/null || true)"
    if [[ -n "${sous_dossier_non_ecrivable}" ]]; then
      arreter_sur_erreur \
        "Sous-dossier build non accessible en ecriture: ${sous_dossier_non_ecrivable}" \
        "Recuperez les droits avec: sudo chown -R \"${USER}:${USER}\" \"${dossier_build}\" puis relancez la commande."
    fi
    return 0
  fi

  dossier_parent_build="$(dirname "${dossier_build}")"
  [[ -w "${dossier_parent_build}" ]] \
    || arreter_sur_erreur \
      "Impossible de creer ${dossier_build}: dossier parent non accessible en ecriture (${dossier_parent_build})." \
      "Installez le projet dans un dossier utilisateur (ex: ${HOME}/git/maintenance_logicielle) ou corrigez les droits."

  mkdir -p "${dossier_build}"
}

#######################################
# Execute javac avec un encodage source
# explicite pour eviter les echecs lies
# a la locale du systeme hote.
# Arguments:
#   $1...: options et sources pour javac
# Retour:
#   code retour javac
#######################################
executer_javac() {
  javac -encoding "${ENCODAGE_SOURCES_JAVA}" "$@"
}

#######################################
# Retourne la version majeure de classe
# supportee par le javac courant.
# Arguments:
#   aucun
# Retour:
#   ecrit la version majeure sur stdout
#######################################
obtenir_version_majeure_javac_courant() {
  local version_javac=""
  local version_java_majeure=""

  version_javac="$(javac -version 2>&1 | awk '{print $2}')"
  [[ -n "${version_javac}" ]] || return 1

  if [[ "${version_javac}" == 1.* ]]; then
    version_java_majeure="${version_javac#1.}"
    version_java_majeure="${version_java_majeure%%.*}"
  else
    version_java_majeure="${version_javac%%.*}"
  fi

  [[ "${version_java_majeure}" =~ ^[0-9]+$ ]] || return 1
  printf '%s\n' "$((version_java_majeure + 44))"
}

#######################################
# Retourne la version majeure bytecode
# d un fichier .class Java.
# Arguments:
#   $1: chemin du fichier .class
# Retour:
#   ecrit la version majeure sur stdout
#######################################
obtenir_version_majeure_classfile() {
  local fichier_classe="$1"

  "${COMMANDE_PYTHON:-python3}" - "${fichier_classe}" <<'PY'
from pathlib import Path
import sys

chemin = Path(sys.argv[1])
donnees = chemin.read_bytes()
if len(donnees) < 8 or donnees[:4] != b"\xca\xfe\xba\xbe":
    raise SystemExit(1)
print(int.from_bytes(donnees[6:8], "big"))
PY
}

#######################################
# Indique si un fichier .class est
# compatible avec le javac courant.
# Arguments:
#   $1: chemin du fichier .class
# Retour:
#   0 si compatible, 1 sinon
#######################################
classfile_compatible_avec_javac_courant() {
  local fichier_classe="$1"
  local version_classe=""
  local version_supportee=""

  version_classe="$(obtenir_version_majeure_classfile "${fichier_classe}")" || return 1
  version_supportee="$(obtenir_version_majeure_javac_courant)" || return 1
  [[ "${version_classe}" -le "${version_supportee}" ]]
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
  executer_javac -d "${DOSSIER_CACHE_MG2D_CLASSES}" "${sources_mg2d[@]}"
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
  local elements_requis=(
    "MG2D/Fenetre.class"
    "MG2D/Clavier.class"
    "MG2D/geometrie/Dessin.class"
    "MG2D/geometrie/Point.class"
    "MG2D/audio/decoder/sfd.ser"
    "MG2D/audio/decoder/l3reorder.ser"
  )
  local index_jar
  local element
  local repertoire_temporaire=""
  local classe_reference="MG2D/Fenetre.class"

  [[ -f "${CHEMIN_JAR_MG2D}" ]] || return 1
  command -v jar >/dev/null 2>&1 || return 1

  index_jar="$(jar tf "${CHEMIN_JAR_MG2D}" 2>/dev/null)" || return 1
  for element in "${elements_requis[@]}"; do
    printf '%s\n' "${index_jar}" | grep -Fxq "${element}" || return 1
  done

  repertoire_temporaire="$(mktemp -d)"
  (
    cd "${repertoire_temporaire}"
    jar xf "${CHEMIN_JAR_MG2D}" "${classe_reference}"
  ) >/dev/null 2>&1 || {
    rm -rf "${repertoire_temporaire}"
    return 1
  }
  if ! classfile_compatible_avec_javac_courant "${repertoire_temporaire}/${classe_reference}"; then
    rm -rf "${repertoire_temporaire}"
    return 1
  fi
  rm -rf "${repertoire_temporaire}"

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
    classfile_compatible_avec_javac_courant "${DOSSIER_CACHE_MG2D_CLASSES}/${classe}" || return 1
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
  # Le cache contient les .class MG2D, le dossier MG2D fournit les ressources
  # binaires requises par le decodeur audio (ex: sfd.ser).
  CLASSPATH_MG2D_RESOLU="${DOSSIER_CACHE_MG2D_CLASSES}:${CHEMIN_MG2D}"
  echo "${CLASSPATH_MG2D_RESOLU}"
}
