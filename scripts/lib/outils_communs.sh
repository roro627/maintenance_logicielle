#!/usr/bin/env bash
set -euo pipefail

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

  if [[ -f "${FICHIER_CONFIG_BORNE}" ]]; then
    # shellcheck source=/dev/null
    source "${FICHIER_CONFIG_BORNE}"
  fi

  CHEMIN_MG2D="${CHEMIN_MG2D:-${RACINE_PROJET}/MG2D}"
  COMMANDE_PYTHON="${COMMANDE_PYTHON:-python3}"
  DELAI_EXTINCTION_SECONDES="${DELAI_EXTINCTION_SECONDES:-30}"
  CLAVIER_BORNE="${CLAVIER_BORNE:-borne}"
  RESOLUTION_X="${RESOLUTION_X:-1280}"
  RESOLUTION_Y="${RESOLUTION_Y:-1024}"

  export RACINE_PROJET REPERTOIRE_BORNE FICHIER_CONFIG_BORNE
  export CHEMIN_MG2D COMMANDE_PYTHON DELAI_EXTINCTION_SECONDES CLAVIER_BORNE
  export RESOLUTION_X RESOLUTION_Y
}

#######################################
# Termine le script avec un message d erreur.
# Arguments:
#   $1: message erreur
# Retour:
#   sort avec code 1
#######################################
arreter_sur_erreur() {
  local message="$1"
  journaliser "ERREUR: ${message}"
  exit 1
}
