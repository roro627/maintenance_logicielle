#!/usr/bin/env bash
set -euo pipefail

"$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lancer_jeu_python.sh" "PianoTile" "app/game.py"
