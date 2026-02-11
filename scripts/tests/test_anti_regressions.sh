#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/outils_communs.sh
source "${SCRIPT_DIR}/../lib/outils_communs.sh"

#######################################
# Verifie l absence de chemins absolus Raspberry figes.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_absence_chemins_figes() {
  if grep -RsnE --include='*.java' --include='*.sh' "/home/pi/git/borne_arcade|/home/pi/git/MG2D|/home/\\\$USER/git/MG2D" "${REPERTOIRE_BORNE}" >/dev/null; then
    arreter_sur_erreur "Chemin absolu fige detecte dans borne_arcade"
  fi
}

#######################################
# Verifie l absence de constructeurs wrappers depricies.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_absence_wrappers_depricies() {
  if grep -RsnE --include='*.java' 'new Integer\(|new Long\(' "${REPERTOIRE_BORNE}" >/dev/null; then
    arreter_sur_erreur "Constructeur wrapper deprecie detecte"
  fi
}

#######################################
# Verifie la protection contre l absence de musiques de fond.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_garde_musiques_fond() {
  if ! grep -Fq "Files.isDirectory(cheminMusiques)" "${REPERTOIRE_BORNE}/Graphique.java"; then
    arreter_sur_erreur "Garde de repertoire sound/bg manquante dans Graphique.java"
  fi
}

#######################################
# Verifie l integration du mode
# maintenance cache.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_integration_mode_maintenance() {
  [[ -f "${REPERTOIRE_BORNE}/config/maintenance_mode.properties" ]] \
    || arreter_sur_erreur "Configuration mode maintenance manquante"
  [[ -x "${REPERTOIRE_BORNE}/MaintenanceMode.sh" ]] \
    || arreter_sur_erreur "Lanceur MaintenanceMode.sh manquant ou non executable"
  [[ -f "${REPERTOIRE_BORNE}/projet/MaintenanceMode/main.py" ]] \
    || arreter_sur_erreur "main.py manquant pour le jeu MaintenanceMode"
  [[ -f "${REPERTOIRE_BORNE}/projet/MaintenanceMode/config_maintenance.json" ]] \
    || arreter_sur_erreur "config_maintenance.json manquant pour le jeu MaintenanceMode"

  grep -Fq "EtatModeMaintenance" "${REPERTOIRE_BORNE}/Graphique.java" \
    || arreter_sur_erreur "Mode maintenance non reference dans Graphique.java"
  grep -Fq "!etatModeMaintenance.estDebloque()" "${REPERTOIRE_BORNE}/Graphique.java" \
    || arreter_sur_erreur "Verrouillage d acces du mode maintenance absent dans Graphique.java"
}

#######################################
# Verifie la robustesse PianoTile en cas
# d absence de librosa.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_fallback_pianotile_librosa() {
  local dossier_pianotile="${REPERTOIRE_BORNE}/projet/PianoTile"

  [[ -f "${dossier_pianotile}/requirements.txt" ]] \
    || arreter_sur_erreur "requirements.txt manquant pour PianoTile"
  grep -Eq '^librosa[<>=]' "${dossier_pianotile}/requirements.txt" \
    || arreter_sur_erreur "Dependance librosa absente de requirements.txt PianoTile"

  grep -Fq "except ModuleNotFoundError" "${dossier_pianotile}/ui/utils/piano.py" \
    || arreter_sur_erreur "Fallback librosa manquant dans PianoTile/ui/utils/piano.py"
  grep -Fq "__generate_notes_fallback" "${dossier_pianotile}/ui/utils/piano.py" \
    || arreter_sur_erreur "Generation fallback PianoTile manquante"
}

#######################################
# Verifie la protection contre les erreurs
# de droits sur le dossier build.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_messages_permission_build() {
  grep -Fq "verifier_acces_ecriture_build_compilation" "${REPERTOIRE_BORNE}/compilation.sh" \
    || arreter_sur_erreur "Protection ecriture build absente dans compilation.sh"
  grep -Fq "verifier_acces_ecriture_build_clean" "${REPERTOIRE_BORNE}/clean.sh" \
    || arreter_sur_erreur "Protection ecriture build absente dans clean.sh"
}

#######################################
# Point d entree du test anti regressions.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
main() {
  charger_configuration_borne
  verifier_absence_chemins_figes
  verifier_absence_wrappers_depricies
  verifier_garde_musiques_fond
  verifier_integration_mode_maintenance
  verifier_fallback_pianotile_librosa
  verifier_messages_permission_build
  journaliser "Test anti regressions: OK"
}

main "$@"
