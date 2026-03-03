#!/usr/bin/env bash
set -euo pipefail

#######################################
# Point d entree shell du workflow de
# migration de versions de la borne.
# Arguments:
#   tous les arguments sont transmis au
#   script Python homologue.
# Retour:
#   code de sortie du script Python.
#######################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "${SCRIPT_DIR}/workflow_migration.py" "$@"
