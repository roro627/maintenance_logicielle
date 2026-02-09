#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

#######################################
# Genere un index HTML minimal en mode secours.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
generer_index_secours() {
  local sortie_html="${RACINE_PROJET}/docs/build/index.html"
  cat > "${sortie_html}" <<'HTML'
<!doctype html>
<html lang="fr">
  <head>
    <meta charset="utf-8" />
    <title>Documentation borne arcade</title>
  </head>
  <body>
    <h1>Documentation borne arcade</h1>
    <p>Generation en mode secours sans mkdocs.</p>
  </body>
</html>
HTML
}

#######################################
# Genere la documentation avec mkdocs ou fallback.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
generer_documentation() {
  rm -rf "${RACINE_PROJET}/docs/build"
  mkdir -p "${RACINE_PROJET}/docs/build"

  if command -v mkdocs >/dev/null 2>&1; then
    journaliser "Generation documentation via mkdocs"
    mkdocs build -f "${RACINE_PROJET}/mkdocs.yml"
  else
    journaliser "mkdocs absent: fallback de documentation"
    cp "${RACINE_PROJET}/docs"/*.md "${RACINE_PROJET}/docs/build/"
    generer_index_secours
  fi
}

#######################################
# Point d entree du generateur de documentation.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
main() {
  charger_configuration_borne
  generer_documentation
  journaliser "Documentation generee"
}

main "$@"
