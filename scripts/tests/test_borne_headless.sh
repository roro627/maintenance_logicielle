#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

DOSSIER_CLASSES_BORNE_HEADLESS=""

#######################################
# Compile les classes Java headless du
# catalogue borne et leur test unitaire.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
compiler_tests_borne_headless() {
  local classpath_mg2d
  classpath_mg2d="$(obtenir_classpath_mg2d)"
  DOSSIER_CLASSES_BORNE_HEADLESS="${DOSSIER_BUILD_CLASSES_TESTS}/borne_headless"
  local fichiers_menu=()
  local fichier

  while IFS= read -r fichier; do
    fichiers_menu+=("${fichier}")
  done < <(find "${REPERTOIRE_BORNE}" -maxdepth 1 -name '*.java' -print | sort)

  (
    cd "${REPERTOIRE_BORNE}"
    rm -rf "${DOSSIER_CLASSES_BORNE_HEADLESS}"
    mkdir -p "${DOSSIER_CLASSES_BORNE_HEADLESS}"
    javac -d "${DOSSIER_CLASSES_BORNE_HEADLESS}" -cp ".:${classpath_mg2d}" \
      "${fichiers_menu[@]}" \
      tests/unit/TestUnitaireCatalogueJeux.java \
      tests/unit/TestContratControleurMenuBorne.java
  )
}

#######################################
# Execute le test Java headless du menu.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
executer_test_java_borne_headless() {
  local classpath_mg2d
  classpath_mg2d="$(obtenir_classpath_mg2d)"
  (
    cd "${REPERTOIRE_BORNE}"
    java -cp ".:${DOSSIER_CLASSES_BORNE_HEADLESS}:${classpath_mg2d}" TestUnitaireCatalogueJeux
    java -cp ".:${DOSSIER_CLASSES_BORNE_HEADLESS}:${classpath_mg2d}" TestContratControleurMenuBorne
  )
}

#######################################
# Verifie la coherence matrice/disque.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_coherence_matrice_borne() {
  (
    cd "${RACINE_PROJET}"
    "${COMMANDE_PYTHON}" - <<'PYCODE'
import json
from pathlib import Path

racine = Path.cwd()
dossier_jeux = racine / "borne_arcade" / "projet"
chemin_matrice = racine / "config" / "matrice_tests_jeux.json"

jeux_disque = sorted(path.name for path in dossier_jeux.iterdir() if path.is_dir())
matrice = json.loads(chemin_matrice.read_text(encoding="utf-8"))
jeux_matrice = sorted(entree["nom"] for entree in matrice["jeux"])

if jeux_disque != jeux_matrice:
    raise SystemExit(
        "ERREUR: Incoherence entre la matrice de tests et le catalogue disque. "
        "ACTION RECOMMANDEE: synchronisez config/matrice_tests_jeux.json avec borne_arcade/projet/."
    )
PYCODE
  )
}

#######################################
# Point d entree du test borne headless.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
main() {
  charger_configuration_borne
  compiler_tests_borne_headless
  executer_test_java_borne_headless
  verifier_coherence_matrice_borne
  journaliser "Test borne headless: OK"
}

main "$@"
