#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

ERREURS_DOCSTRINGS_SHELL=()

#######################################
# Ajoute une erreur shell a la liste.
# Arguments:
#   $1: message erreur
# Retour:
#   0
#######################################
ajouter_erreur_docstring_shell() {
  local message="$1"
  ERREURS_DOCSTRINGS_SHELL+=("${message}")
}

#######################################
# Verifie les docstrings Python dans le
# perimetre maintenu du projet.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_docstrings_python_perimetre_maintenu() {
  local sortie
  if ! sortie="$("${COMMANDE_PYTHON}" - "${RACINE_PROJET}" "${REPERTOIRE_BORNE}" <<'PY'
import ast
import sys
from pathlib import Path


def collecter_fichiers_python(dossier_racine):
    """Retourne la liste des fichiers Python a verifier.

    Args:
        dossier_racine: Chemin racine du projet.

    Returns:
        Liste triee des chemins Python cibles.
    """

    cibles = [
        dossier_racine / "scripts",
        Path(sys.argv[2]) / "projet" / "NeonSumo",
    ]
    fichiers = []
    for cible in cibles:
        if not cible.exists():
            continue
        for fichier in cible.rglob("*.py"):
            if ".venv" in fichier.parts or "site" in fichier.parts:
                continue
            fichiers.append(fichier)
    return sorted(set(fichiers))


def verifier_fichier_python(chemin_fichier):
    """Controle qu un fichier Python documente toutes ses fonctions.

    Args:
        chemin_fichier: Fichier Python a verifier.

    Returns:
        Liste de messages d anomalies detectees.
    """

    anomalies = []
    try:
        contenu = chemin_fichier.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        contenu = chemin_fichier.read_text(encoding="latin-1")

    try:
        arbre = ast.parse(contenu, filename=str(chemin_fichier))
    except SyntaxError as erreur:
        anomalies.append(f"{chemin_fichier}:{erreur.lineno}: syntaxe invalide ({erreur.msg})")
        return anomalies

    for noeud in ast.walk(arbre):
        if isinstance(noeud, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if ast.get_docstring(noeud) is None:
                anomalies.append(
                    f"{chemin_fichier}:{noeud.lineno}: docstring manquante pour la fonction {noeud.name}"
                )
    return anomalies


def main():
    """Point d entree du controle docstrings Python.

    Returns:
        0 si conforme, 1 sinon.
    """

    racine = Path(sys.argv[1]).resolve()
    fichiers = collecter_fichiers_python(racine)
    anomalies_globales = []
    for fichier in fichiers:
        anomalies_globales.extend(verifier_fichier_python(fichier))

    if anomalies_globales:
        print("\n".join(anomalies_globales))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PY
)"; then
    while IFS= read -r ligne; do
      [[ -n "${ligne}" ]] || continue
      journaliser "ERREUR: ${ligne}"
    done <<< "${sortie}"
    arreter_sur_erreur \
      "Docstrings Python manquantes dans le perimetre maintenu." \
      "Ajoutez les docstrings signalees puis relancez scripts/tests/test_docstrings.sh."
  fi
}

#######################################
# Verifie les blocs de documentation
# des fonctions shell critiques.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_docstrings_shell_critiques() {
  local fichiers_shell=()
  local fichier=""
  while IFS= read -r fichier; do
    fichiers_shell+=("${fichier}")
  done < <(
    {
      find "${RACINE_PROJET}/scripts" -type f -name '*.sh'
      printf '%s\n' \
        "${REPERTOIRE_BORNE}/compilation.sh" \
        "${REPERTOIRE_BORNE}/lancer_jeu_java.sh" \
        "${REPERTOIRE_BORNE}/lancer_jeu_python.sh" \
        "${REPERTOIRE_BORNE}/lancer_jeu_love.sh" \
        "${REPERTOIRE_BORNE}/clean.sh"
    } | sort -u
  )

  local ligne_fonction=""
  local numero_ligne=0
  local nom_fonction=""
  local debut_fenetre=0
  local contexte=""
  local fichiers_total="${#fichiers_shell[@]}"
  local index_fichier
  for ((index_fichier = 0; index_fichier < fichiers_total; index_fichier++)); do
    fichier="${fichiers_shell[${index_fichier}]}"
    [[ -f "${fichier}" ]] || continue

    while IFS= read -r ligne_fonction; do
      [[ -n "${ligne_fonction}" ]] || continue
      numero_ligne="${ligne_fonction%%:*}"
      nom_fonction="${ligne_fonction#*:}"

      debut_fenetre=$((numero_ligne - 15))
      if [[ "${debut_fenetre}" -lt 1 ]]; then
        debut_fenetre=1
      fi
      contexte="$(sed -n "${debut_fenetre},$((numero_ligne - 1))p" "${fichier}")"

      if [[ "${contexte}" != *"Arguments:"* ]] || [[ "${contexte}" != *"Retour:"* ]]; then
        ajouter_erreur_docstring_shell "${fichier}:${numero_ligne}: bloc doc manquant/incomplet pour ${nom_fonction}"
      fi
    done < <(awk '
      /^[[:space:]]*[a-zA-Z_][a-zA-Z0-9_]*\(\)[[:space:]]*\{/ {
        ligne = $0
        gsub(/^[[:space:]]*/, "", ligne)
        sub(/\(\).*/, "", ligne)
        print NR ":" ligne
      }
    ' "${fichier}")
  done
}

#######################################
# Termine le test en erreur si des
# anomalies shell ont ete collecte.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
echouer_si_erreurs_shell_detectees() {
  local message
  if [[ "${#ERREURS_DOCSTRINGS_SHELL[@]}" -eq 0 ]]; then
    return 0
  fi

  for message in "${ERREURS_DOCSTRINGS_SHELL[@]}"; do
    journaliser "ERREUR: ${message}"
  done
  arreter_sur_erreur \
    "${#ERREURS_DOCSTRINGS_SHELL[@]} erreur(s) de docstrings shell detectee(s)." \
    "Ajoutez les blocs Arguments/Retour des fonctions signalees."
}

#######################################
# Point d entree du test docstrings.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
main() {
  charger_configuration_borne
  verifier_docstrings_python_perimetre_maintenu
  verifier_docstrings_shell_critiques
  echouer_si_erreurs_shell_detectees
  journaliser "Test docstrings: OK"
}

main "$@"
