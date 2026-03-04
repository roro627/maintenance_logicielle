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
  grep -Fq "ControleurMenuBorne" "${REPERTOIRE_BORNE}/Graphique.java" \
    || arreter_sur_erreur "Controleur de menu headless non reference dans Graphique.java"
  grep -Fq "estJeuMaintenanceVerrouille" "${REPERTOIRE_BORNE}/ControleurMenuBorne.java" \
    || arreter_sur_erreur "Verrouillage d acces du mode maintenance absent dans ControleurMenuBorne.java"

  if grep -Eq "getJoyJ1(Haut|Bas|Gauche|Droite)Tape" "${REPERTOIRE_BORNE}/EtatModeMaintenance.java"; then
    arreter_sur_erreur "EtatModeMaintenance utilise des lectures joystick Tape qui consomment les entrees du menu"
  fi
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
# Verifie que le bootstrap evite les
# artefacts root bloquants apres sudo.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_bootstrap_permissions_apres_sudo() {
  grep -Fq "executer_comme_utilisateur_appelant" "${RACINE_PROJET}/bootstrap_borne.sh" \
    || arreter_sur_erreur "Execution non-systeme sous utilisateur appelant absente dans bootstrap_borne.sh"
  grep -Fq "normaliser_permissions_post_bootstrap" "${RACINE_PROJET}/bootstrap_borne.sh" \
    || arreter_sur_erreur "Normalisation permissions finales absente dans bootstrap_borne.sh"
}

#######################################
# Verifie que la configuration Docker
# locale reutilise bien l elevation
# systeme pour groupadd/usermod.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_elevation_groupe_docker() {
  grep -Fq "prefixe_systeme=(\"\${prefixe_elevation}\")" "${RACINE_PROJET}/scripts/install/installer_borne.sh" \
    || arreter_sur_erreur "Elevation systeme du groupe docker absente dans installer_borne.sh"
  grep -Fq "\"\${prefixe_systeme[@]}\" groupadd docker" "${RACINE_PROJET}/scripts/install/installer_borne.sh" \
    || arreter_sur_erreur "groupadd docker n utilise pas l elevation systeme dans installer_borne.sh"
  grep -Fq "\"\${prefixe_systeme[@]}\" usermod -aG docker" "${RACINE_PROJET}/scripts/install/installer_borne.sh" \
    || arreter_sur_erreur "usermod docker n utilise pas l elevation systeme dans installer_borne.sh"
}

#######################################
# Verifie que le bootstrap n exige pas
# Codex CLI en mode test et gere les
# Node.js trop anciens pour Codex.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_garde_codex_et_nodejs() {
  grep -Fq "garantir_nodejs_compatible_codex" "${RACINE_PROJET}/scripts/install/installer_borne.sh" \
    || arreter_sur_erreur "Mise a niveau Node.js pour Codex absente dans installer_borne.sh"
  grep -Fq "https://deb.nodesource.com/setup_\${VERSION_NODE_SOURCE_MAJEURE}.x" "${RACINE_PROJET}/scripts/install/installer_borne.sh" \
    || arreter_sur_erreur "Depot officiel NodeSource absent dans installer_borne.sh"
  grep -Fq "Mode test actif: verification Codex CLI ignoree" "${RACINE_PROJET}/scripts/install/installer_borne.sh" \
    || arreter_sur_erreur "Garde Codex en mode test absente dans installer_borne.sh"
  grep -Fq "NODE_VERSION_MIN_CODEX=16.0" "${RACINE_PROJET}/config/versions_minimales.env" \
    || arreter_sur_erreur "Version minimale Node.js pour Codex absente de config/versions_minimales.env"
}

#######################################
# Verifie que toutes les compilations
# Java shell passent par un encodage
# source explicite et centralise.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_encodage_java_explicite() {
  local utilisations_javac_directes
  local motif_helper_javac="javac -encoding \"\${ENCODAGE_SOURCES_JAVA}\" \"\$@\""
  local recherche_javac=""

  grep -Fq "ENCODAGE_SOURCES_JAVA" "${REPERTOIRE_BORNE}/config/borne.env" \
    || arreter_sur_erreur "Encodage Java centralise absent de borne.env"
  grep -Fq "${motif_helper_javac}" "${RACINE_PROJET}/scripts/lib/outils_communs.sh" \
    || arreter_sur_erreur "Helper javac a encodage explicite absent de scripts/lib/outils_communs.sh"

  if command -v rg >/dev/null 2>&1; then
    recherche_javac="$(
      rg -n '^[[:space:]]*(if[[:space:]]+![[:space:]]+)?javac([[:space:]]|$)' "${REPERTOIRE_BORNE}" "${RACINE_PROJET}/scripts" -g '*.sh' \
        || true
    )"
  else
    recherche_javac="$(
      grep -RsnE --include='*.sh' '^[[:space:]]*(if[[:space:]]+![[:space:]]+)?javac([[:space:]]|$)' "${REPERTOIRE_BORNE}" "${RACINE_PROJET}/scripts" \
        || true
    )"
  fi

  utilisations_javac_directes="$(
    printf '%s\n' "${recherche_javac}" | grep -Fv "${motif_helper_javac}" || true
  )"
  [[ -z "${utilisations_javac_directes}" ]] \
    || arreter_sur_erreur \
      "Compilation Java shell hors helper detectee." \
      "Remplacez les appels javac directs par executer_javac pour imposer ${ENCODAGE_SOURCES_JAVA}."
}

#######################################
# Verifie que le cache MG2D invalide les
# classes compilees avec un bytecode trop
# recent pour le javac courant.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_invalidation_cache_mg2d_trop_recent() {
  grep -Fq "classfile_compatible_avec_javac_courant" "${RACINE_PROJET}/scripts/lib/outils_communs.sh" \
    || arreter_sur_erreur "Verification de compatibilite bytecode MG2D absente de scripts/lib/outils_communs.sh"
  grep -Fq "obtenir_version_majeure_javac_courant" "${RACINE_PROJET}/scripts/lib/outils_communs.sh" \
    || arreter_sur_erreur "Detection version majeure javac absente de scripts/lib/outils_communs.sh"
  grep -Fq "verifier_rejet_cache_mg2d_trop_recent" "${RACINE_PROJET}/scripts/tests/test_classpath_mg2d.sh" \
    || arreter_sur_erreur "Test de rejet cache MG2D trop recent absent de scripts/tests/test_classpath_mg2d.sh"
}

#######################################
# Verifie que l installateur reconnait
# npm/node deja disponibles quand ils
# viennent du paquet NodeSource nodejs.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_detection_npm_nodesource() {
  local motif_boucle_dependances="if dependance_systeme_disponible \"\${paquet}\"; then"

  grep -Fq "dependance_systeme_disponible()" "${RACINE_PROJET}/scripts/install/installer_borne.sh" \
    || arreter_sur_erreur "Helper de detection dependance systeme absent de installer_borne.sh"
  grep -Fq "command -v node >/dev/null 2>&1 && return 0" "${RACINE_PROJET}/scripts/install/installer_borne.sh" \
    || arreter_sur_erreur "Detection nodejs via commande absente de installer_borne.sh"
  grep -Fq "command -v npm >/dev/null 2>&1 && return 0" "${RACINE_PROJET}/scripts/install/installer_borne.sh" \
    || arreter_sur_erreur "Detection npm via commande absente de installer_borne.sh"
  grep -Fq "${motif_boucle_dependances}" "${RACINE_PROJET}/scripts/install/installer_borne.sh" \
    || arreter_sur_erreur "Boucle dependances systeme n utilise pas le helper de detection portable"
}

#######################################
# Verifie que les workflows et scripts
# critiques lancent les .sh via bash
# ou helper portable sans exiger 100755.
# Arguments:
#   aucun
# Retour:
#   0
#######################################
verifier_execution_shell_portable() {
  grep -Fq "run: bash ./scripts/tests/lancer_suite.sh" "${RACINE_PROJET}/.github/workflows/qualite.yml" \
    || arreter_sur_erreur "Workflow qualite n execute pas lancer_suite.sh via bash"
  grep -Fq "bash ./bootstrap_borne.sh" "${RACINE_PROJET}/.github/workflows/verification_reelle.yml" \
    || arreter_sur_erreur "Workflow verification_reelle n execute pas bootstrap_borne.sh via bash"
  grep -Fq "bash ./scripts/tests/lancer_suite.sh" "${RACINE_PROJET}/.github/workflows/verification_reelle.yml" \
    || arreter_sur_erreur "Workflow verification_reelle n execute pas lancer_suite.sh via bash"

  grep -Fq "executer_script_shell()" "${RACINE_PROJET}/scripts/lib/outils_communs.sh" \
    || arreter_sur_erreur "Helper executer_script_shell absent de scripts/lib/outils_communs.sh"
  grep -Fq "executer_script_shell \"\${SCRIPT_DIR}/\${script_test}\"" "${RACINE_PROJET}/scripts/tests/lancer_suite.sh" \
    || arreter_sur_erreur "Suite complete n utilise pas le helper shell portable"
  grep -Fq "executer_script_shell \"\${SCRIPT_DIR}/test_versions_compatibilite.sh\"" "${RACINE_PROJET}/scripts/tests/test_smoke.sh" \
    || arreter_sur_erreur "Smoke tests n utilisent pas le helper shell portable"
  grep -Fq "[[ -f \"\${script_requis}\" ]]" "${RACINE_PROJET}/bootstrap_borne.sh" \
    || arreter_sur_erreur "Bootstrap exige encore le bit executable avant installation"
  grep -Fq "executer_comme_utilisateur_appelant bash \"\${REPERTOIRE_BORNE}/compilation.sh\"" "${RACINE_PROJET}/bootstrap_borne.sh" \
    || arreter_sur_erreur "Bootstrap n execute pas compilation.sh via bash"
  grep -Fq "env EVITER_TEST_DEPLOIEMENT=1 bash \"\${RACINE_PROJET}/scripts/tests/lancer_suite.sh\"" "${RACINE_PROJET}/scripts/deploiement/post_pull_update.sh" \
    || arreter_sur_erreur "Pipeline post-pull n execute pas lancer_suite.sh via bash"
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
  verifier_bootstrap_permissions_apres_sudo
  verifier_elevation_groupe_docker
  verifier_garde_codex_et_nodejs
  verifier_encodage_java_explicite
  verifier_invalidation_cache_mg2d_trop_recent
  verifier_detection_npm_nodesource
  verifier_execution_shell_portable
  journaliser "Test anti regressions: OK"
}

main "$@"
