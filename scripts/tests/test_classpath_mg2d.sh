#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

ERREURS_DETECTEES=()

#######################################
# Ajoute une erreur a la liste.
# Arguments:
#   $1: message erreur
# Retour:
#   0
#######################################
ajouter_erreur() {
  local message="$1"
  ERREURS_DETECTEES+=("${message}")
}

#######################################
# Verifie que le classpath MG2D expose
# les classes minimales indispensables.
# Arguments:
#   $1: classpath MG2D resolu
# Retour:
#   0
#######################################
verifier_classes_requises() {
  local classpath_mg2d="$1"
  local classes_requises=(
    "MG2D/Fenetre.class"
    "MG2D/Clavier.class"
    "MG2D/geometrie/Dessin.class"
    "MG2D/geometrie/Point.class"
  )
  local classe

  if [[ "${classpath_mg2d}" == "${CHEMIN_JAR_MG2D}" ]]; then
    jar_mg2d_valide || ajouter_erreur "Jar MG2D selectionne mais incomplet: ${CHEMIN_JAR_MG2D}"
    return 0
  fi

  for classe in "${classes_requises[@]}"; do
    [[ -f "${classpath_mg2d}/${classe}" ]] \
      || ajouter_erreur "Classe manquante dans le cache MG2D: ${classe}"
  done
}

#######################################
# Verifie qu une petite classe Java
# peut importer MG2D.geometrie.Dessin.
# Arguments:
#   $1: classpath MG2D resolu
# Retour:
#   0
#######################################
verifier_import_dessin() {
  local classpath_mg2d="$1"
  local repertoire_temporaire
  local sortie

  repertoire_temporaire="$(mktemp -d)"
  cat > "${repertoire_temporaire}/VerificationClasspathMG2D.java" <<'JAVA'
import MG2D.geometrie.Dessin;

public final class VerificationClasspathMG2D {
  private VerificationClasspathMG2D() {
  }

  public static void main(String[] arguments) {
    System.out.println(Dessin.class.getName());
  }
}
JAVA

  if ! javac -cp "${classpath_mg2d}" "${repertoire_temporaire}/VerificationClasspathMG2D.java"; then
    ajouter_erreur "Compilation d une classe de verification MG2D impossible"
    rm -rf "${repertoire_temporaire}"
    return 0
  fi

  sortie="$(java -cp "${repertoire_temporaire}:${classpath_mg2d}" VerificationClasspathMG2D 2>/dev/null || true)"
  [[ "${sortie}" == "MG2D.geometrie.Dessin" ]] \
    || ajouter_erreur "Chargement runtime de MG2D.geometrie.Dessin impossible"

  rm -rf "${repertoire_temporaire}"
}

#######################################
# Termine le test en erreur si des
# anomalies ont ete collecte.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
echouer_si_erreurs_detectees() {
  local message
  if [[ "${#ERREURS_DETECTEES[@]}" -eq 0 ]]; then
    return 0
  fi

  for message in "${ERREURS_DETECTEES[@]}"; do
    journaliser "ERREUR: ${message}"
  done
  arreter_sur_erreur "${#ERREURS_DETECTEES[@]} erreur(s) detectee(s) sur le classpath MG2D"
}

#######################################
# Point d entree du test classpath MG2D.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
main() {
  local classpath_mg2d

  charger_configuration_borne
  classpath_mg2d="$(obtenir_classpath_mg2d)"

  verifier_classes_requises "${classpath_mg2d}"
  verifier_import_dessin "${classpath_mg2d}"
  echouer_si_erreurs_detectees

  journaliser "Test classpath MG2D: OK"
}

main "$@"
