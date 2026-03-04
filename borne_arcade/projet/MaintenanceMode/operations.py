"""Operations disponibles dans le mode maintenance de la borne."""

from __future__ import annotations

import datetime
import json
import locale
import os
import queue
import re
import shutil
import subprocess
import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple


ConsommateurJournal = Callable[[str], None]
TIMEOUT_PAR_DEFAUT = 120
TIMEOUT_DIAGNOSTIC_SECONDES = 20
INTERVALLE_LECTURE_PAR_DEFAUT_MS = 100
DOSSIER_CACHE_MAINTENANCE_RELATIF = Path(".cache") / "maintenance_logicielle"
DOSSIER_CACHE_LOGS_RELATIF = Path(".cache") / "maintenance_logicielle" / "logs"
DOSSIER_TEMPORAIRE_LOGS = Path("/tmp") / "maintenance_logicielle" / "logs"
FICHIER_TEST_ECRITURE_LOGS = ".ecriture_logs_maintenance.tmp"
FICHIER_ETAT_MIGRATION = "etat_migration.json"
FICHIER_CONFIGURATION_ASSISTANT_IA = Path(__file__).resolve().parents[3] / "config" / "assistant_ia_migration.json"
FICHIER_MODELE_PROMPT_ASSISTANT_IA = Path(__file__).resolve().parents[3] / "config" / "prompt_migration_ia.md"
MESSAGE_HOTE_APT_NON_SUPPORTE = (
    "Hote non compatible avec la migration apt. "
    "Action recommandee: executer cette etape sur Raspberry Pi OS ou Debian."
)
DOCUMENTS_MIGRATION_IA = [
    "docs/technique.md",
    "docs/tests.md",
    "docs/architecture.md",
    "docs/utilisateur.md",
    "docs/deploiement.md",
    "docs/installation.md",
    "docs/compatibilite_dependances.md",
    "docs/index.md",
    "docs/rendu.md",
]
COMMANDES_QUALITE_MIGRATION = [
    "./scripts/tests/lancer_suite.sh",
    "~/.local/bin/act -W .github/workflows/qualite.yml -j verification --container-architecture linux/amd64 -P ubuntu-latest=catthehacker/ubuntu:act-latest",
    "~/.local/bin/act -W .github/workflows/verification_reelle.yml -j verification_reelle_debian11 --container-architecture linux/amd64 -P ubuntu-latest=catthehacker/ubuntu:act-latest",
]
PAQUETS_SYSTEME_BORNE = [
    "git",
    "curl",
    "openjdk-17-jdk",
    "python3",
    "python3-venv",
    "python3-pip",
    "checkstyle",
    "pylint",
    "shellcheck",
    "xdotool",
    "lua5.4",
    "libsndfile1",
    "love",
]
PAQUETS_RESET_NON_SYSTEME_BORNE = [
    "checkstyle",
    "pylint",
    "shellcheck",
    "xdotool",
    "lua5.4",
    "love",
]
PAQUETS_RESET_SYSTEME_PROTEGES_BORNE = [
    "git",
    "curl",
    "openjdk-17-jdk",
    "python3",
    "python3-venv",
    "python3-pip",
    "libsndfile1",
]
COMMANDES_PRE_REQUIS_BORNE = {
    "git": ["git"],
    "curl": ["curl"],
    "openjdk-17-jdk": ["java"],
    "python3": ["python3"],
    "python3-venv": ["python3"],
    "python3-pip": ["pip3", "pip"],
    "checkstyle": ["checkstyle"],
    "pylint": ["pylint"],
    "shellcheck": ["shellcheck"],
    "xdotool": ["xdotool"],
    "lua5.4": ["lua5.4", "lua"],
    "libsndfile1": [],
    "love": ["love"],
}
REPERTOIRES_RESET_RELATIFS = [
    Path(".venv"),
    Path("build"),
    Path("site"),
    Path(".cache") / "bootstrap_borne",
]
FICHIERS_RESET_RELATIFS = [
    Path(".etat_derniere_maj"),
    Path(".post_pull.lock"),
]

CONFIGURATION_PAR_DEFAUT = {
    "fenetre": {
        "largeur": 1280,
        "hauteur": 1024,
        "mode_affichage": "fenetre_sans_bordure",
        "position_x": 0,
        "position_y": 0,
        "fps": 30,
    },
    "interface": {
        "marge_horizontale": 36,
        "marge_verticale": 28,
        "hauteur_entete": 112,
        "hauteur_pied": 72,
        "espacement_colonnes": 20,
        "largeur_colonne_operations": 540,
        "rayon_bordure": 16,
        "hauteur_ligne_operation": 48,
        "hauteur_ligne_journal": 24,
        "nombre_lignes_journal": 27,
        "taille_police_titre": 44,
        "taille_police_texte": 24,
        "taille_police_journal": 20,
        "intervalle_animation_ms": 300,
    },
    "theme": {
        "fond_haut": [7, 14, 30],
        "fond_bas": [2, 6, 16],
        "panneau": [16, 24, 44],
        "panneau_bord": [56, 94, 140],
        "texte_principal": [233, 239, 255],
        "texte_secondaire": [174, 190, 226],
        "accent": [0, 208, 154],
        "erreur": [241, 98, 98],
        "succes": [106, 210, 134],
        "info": [88, 184, 255],
        "selection": [24, 48, 86],
    },
    "journal": {
        "taille_max_lignes_interface": 240,
        "intervalle_lecture_processus_ms": 100,
        "pas_scroll_journal": 6,
        "pas_scroll_horizontal_journal": 8,
    },
    "temps_max_secondes": {
        "diagnostic": 20,
        "git_pull": 240,
        "git_retour_precedent": 240,
        "pipeline_post_pull": 600,
        "mise_a_jour_os": 1800,
        "reset_pre_requis": 1800,
        "actualiser_cibles_migration": 60,
        "appliquer_migration_cible": 3600,
        "preparer_placeholder_ia_migration": 7200,
        "relancer_qualite_complete": 14400,
        "proposer_pr_migration": 600,
    },
    "fichier_verrouillage": ".verrouillage_mode_maintenance",
}
CONFIGURATION_ASSISTANT_IA_PAR_DEFAUT = {
    "codex": {
        "commande": "codex",
        "modele": "qwen3:8b",
        "fournisseur_local": "ollama",
        "utiliser_provider_oss": True,
        "activer_recherche_web": True,
        "sortie_json": True,
        "couleur": "never",
        "politique_approbation": "never",
        "sandbox": "danger-full-access",
        "ignorer_verification_git": False,
        "arguments_supplementaires": [],
    },
    "ollama": {
        "base_url": "http://10.22.28.190:11434",
    },
    "mcp": {
        "context7": {
            "actif": True,
            "commande": "npx",
            "arguments": ["-y", "@upstash/context7-mcp"],
            "delai_demarrage_secondes": 120,
            "timeout_outil_secondes": 300,
        }
    },
    "prompt": {
        "chemin_modele": "config/prompt_migration_ia.md",
    },
}
FICHIER_CONFIGURATION_CIBLES_MIGRATION = Path(__file__).resolve().parents[3] / "config" / "cibles_migration.json"
CONFIGURATION_CIBLES_MIGRATION_PAR_DEFAUT = {
    "cibles": [
        {
            "id": "systeme_apt",
            "titre": "Systeme apt",
            "description": "Mise a jour globale Debian/Raspberry Pi OS via apt full-upgrade.",
            "type": "systeme_apt",
            "commande_version_installee": [
                "sh",
                "-lc",
                ". /etc/os-release && printf '%s (%s)\\n' \"${PRETTY_NAME:-Systeme inconnu}\" \"${VERSION_ID:-?}\"",
            ],
            "commandes_migration": [
                ["apt-get", "update"],
                ["apt-get", "full-upgrade", "-y"],
            ],
        },
        {
            "id": "python3",
            "titre": "Python",
            "description": "Interpreteur Python systeme et outils pip/venv.",
            "type": "paquet_apt",
            "paquet_apt": "python3",
            "commande_version_installee": ["python3", "--version"],
            "commandes_migration": [
                ["apt-get", "install", "-y", "python3", "python3-venv", "python3-pip"],
            ],
        },
        {
            "id": "java17",
            "titre": "Java 17",
            "description": "JDK OpenJDK cible pour la borne Java/MG2D.",
            "type": "paquet_apt",
            "paquet_apt": "openjdk-17-jdk",
            "commande_version_installee": ["java", "-version"],
            "commandes_migration": [
                ["apt-get", "install", "-y", "openjdk-17-jdk"],
            ],
        },
        {
            "id": "lua54",
            "titre": "Lua 5.4",
            "description": "Interpreteur Lua utilise par les jeux Lua et les validateurs headless.",
            "type": "paquet_apt",
            "paquet_apt": "lua5.4",
            "commande_version_installee": ["lua", "-v"],
            "commandes_migration": [
                ["apt-get", "install", "-y", "lua5.4"],
            ],
        },
        {
            "id": "love",
            "titre": "LÖVE",
            "description": "Runtime LÖVE2D utilise par les jeux CursedWare et Lua.",
            "type": "paquet_apt",
            "paquet_apt": "love",
            "commande_version_installee": ["love", "--version"],
            "commandes_migration": [
                ["apt-get", "install", "-y", "love"],
            ],
        },
    ]
}


def charger_configuration(chemin_configuration: Path) -> Dict[str, object]:
    """Charge la configuration JSON du mode maintenance.

    Args:
        chemin_configuration: Chemin du fichier JSON de configuration.

    Returns:
        Un dictionnaire de configuration fusionne avec les valeurs par defaut.
    """

    configuration = json.loads(json.dumps(CONFIGURATION_PAR_DEFAUT))
    if not chemin_configuration.exists():
        return configuration

    with chemin_configuration.open("r", encoding="utf-8") as flux:
        donnees = json.load(flux)

    for cle, valeur in donnees.items():
        if isinstance(valeur, dict) and isinstance(configuration.get(cle), dict):
            configuration[cle].update(valeur)
        else:
            configuration[cle] = valeur
    return configuration


def charger_configuration_assistant_ia(chemin_configuration: Path | None = None) -> Dict[str, object]:
    """Charge la configuration JSON de l assistant IA de migration.

    Args:
        chemin_configuration: Chemin optionnel du fichier de configuration.

    Returns:
        Dictionnaire fusionne avec les valeurs par defaut.
    """

    configuration = json.loads(json.dumps(CONFIGURATION_ASSISTANT_IA_PAR_DEFAUT))
    chemin = chemin_configuration or FICHIER_CONFIGURATION_ASSISTANT_IA
    if not chemin.exists():
        return configuration

    with chemin.open("r", encoding="utf-8") as flux:
        donnees = json.load(flux)

    for cle, valeur in donnees.items():
        if isinstance(valeur, dict) and isinstance(configuration.get(cle), dict):
            configuration[cle].update(valeur)
        else:
            configuration[cle] = valeur
    return configuration


def obtenir_racine_projet() -> Path:
    """Retourne la racine du depot depuis le dossier du jeu.

    Args:
        Aucun.

    Returns:
        Chemin absolu de la racine du projet.
    """

    return Path(__file__).resolve().parents[3]


def lister_dossiers_logs_candidats(racine_projet: Path) -> List[Path]:
    """Liste les dossiers potentiels de journalisation.

    Args:
        racine_projet: Racine du depot.

    Returns:
        Liste ordonnee des dossiers candidats.
    """

    return [
        racine_projet / "logs",
        Path.home() / DOSSIER_CACHE_LOGS_RELATIF,
        DOSSIER_TEMPORAIRE_LOGS,
    ]


def tester_ecriture_dossier_logs(dossier_logs: Path) -> bool:
    """Verifie qu un dossier de logs est bien inscriptible.

    Args:
        dossier_logs: Dossier a tester.

    Returns:
        True si l ecriture est possible, sinon False.
    """

    fichier_test = dossier_logs / FICHIER_TEST_ECRITURE_LOGS
    try:
        dossier_logs.mkdir(parents=True, exist_ok=True)
        fichier_test.write_text("ok", encoding="utf-8")
        fichier_test.unlink()
        return True
    except OSError:
        return False


def selectionner_dossier_logs(racine_projet: Path) -> Path:
    """Selectionne le premier dossier de logs accessible en ecriture.

    Args:
        racine_projet: Racine du depot.

    Returns:
        Dossier valide pour la journalisation.

    Raises:
        OSError: Si aucun dossier n est inscriptible.
    """

    for dossier_logs in lister_dossiers_logs_candidats(racine_projet):
        if tester_ecriture_dossier_logs(dossier_logs):
            return dossier_logs

    message = (
        "Aucun dossier de logs accessible. "
        "Action recommandee: verifier les permissions puis relancer l operation."
    )
    raise OSError(message)


def obtenir_encodage_processus() -> str:
    """Retourne l encodage prefere pour les sous-processus.

    Args:
        Aucun.

    Returns:
        Nom d encodage valide.
    """

    return locale.getpreferredencoding(False) or "utf-8"


def obtenir_dossier_cache_maintenance(racine_projet: Path) -> Path:
    """Retourne le dossier cache technique du workflow maintenance.

    Args:
        racine_projet: Racine du depot.

    Returns:
        Dossier cache cree si necessaire.
    """

    dossier_cache = racine_projet / DOSSIER_CACHE_MAINTENANCE_RELATIF
    dossier_cache.mkdir(parents=True, exist_ok=True)
    return dossier_cache


def obtenir_fichier_etat_migration(racine_projet: Path) -> Path:
    """Construit le chemin du fichier d etat de migration.

    Args:
        racine_projet: Racine du depot.

    Returns:
        Chemin absolu du fichier JSON d etat.
    """

    return obtenir_dossier_cache_maintenance(racine_projet) / FICHIER_ETAT_MIGRATION


def charger_etat_migration(racine_projet: Path) -> Dict[str, object]:
    """Charge l etat persistant du workflow de migration.

    Args:
        racine_projet: Racine du depot.

    Returns:
        Dictionnaire d etat vide si absent ou invalide.
    """

    chemin_etat = obtenir_fichier_etat_migration(racine_projet)
    if not chemin_etat.exists():
        return {}

    try:
        with chemin_etat.open("r", encoding="utf-8") as flux:
            donnees = json.load(flux)
    except (json.JSONDecodeError, OSError):
        return {}

    if not isinstance(donnees, dict):
        return {}
    return donnees


def enregistrer_etat_migration(racine_projet: Path, etat: Dict[str, object]) -> Path:
    """Persiste l etat du workflow de migration.

    Args:
        racine_projet: Racine du depot.
        etat: Dictionnaire d etat a ecrire.

    Returns:
        Chemin du fichier ecrit.
    """

    chemin_etat = obtenir_fichier_etat_migration(racine_projet)
    chemin_etat.parent.mkdir(parents=True, exist_ok=True)
    with chemin_etat.open("w", encoding="utf-8") as flux:
        json.dump(etat, flux, indent=2, ensure_ascii=False)
        flux.write("\n")
    return chemin_etat


def effacer_etat_migration_obsolete(racine_projet: Path) -> bool:
    """Supprime l etat de migration persistant si present.

    Args:
        racine_projet: Racine du depot.

    Returns:
        True si un fichier a ete supprime, sinon False.
    """

    chemin_etat = obtenir_fichier_etat_migration(racine_projet)
    if not chemin_etat.exists():
        return False
    chemin_etat.unlink()
    return True


def capturer_contexte_git(racine_projet: Path) -> Dict[str, object]:
    """Capture le contexte git courant du depot.

    Args:
        racine_projet: Racine du depot.

    Returns:
        Dictionnaire de contexte git tolerent a l absence de git.
    """

    contexte = {
        "git_disponible": False,
        "branche_git": "(indisponible)",
        "commit_git": "(indisponible)",
        "depot_propre": False,
    }
    if shutil.which("git") is None:
        return contexte

    succes_branche, sortie_branche = executer_commande_capture(
        ["git", "-C", str(racine_projet), "rev-parse", "--abbrev-ref", "HEAD"],
        racine_projet,
    )
    succes_commit, sortie_commit = executer_commande_capture(
        ["git", "-C", str(racine_projet), "rev-parse", "HEAD"],
        racine_projet,
    )
    succes_statut, sortie_statut = executer_commande_capture(
        ["git", "-C", str(racine_projet), "status", "--porcelain"],
        racine_projet,
    )

    contexte["git_disponible"] = succes_branche or succes_commit or succes_statut
    if succes_branche:
        contexte["branche_git"] = extraire_premiere_ligne_non_vide(sortie_branche)
    if succes_commit:
        contexte["commit_git"] = extraire_premiere_ligne_non_vide(sortie_commit)
    if succes_statut:
        contexte["depot_propre"] = not sortie_statut.strip()
    return contexte


def determiner_dossier_sortie_artefacts(
    racine_projet: Path,
    contexte_operation: Dict[str, object] | None,
) -> Path:
    """Determine le dossier de sortie des artefacts d une operation.

    Args:
        racine_projet: Racine du depot.
        contexte_operation: Contexte optionnel d execution.

    Returns:
        Dossier de sortie cree si necessaire.
    """

    dossier_sortie = ""
    if isinstance(contexte_operation, dict):
        valeur = contexte_operation.get("dossier_sortie")
        if isinstance(valeur, str):
            dossier_sortie = valeur.strip()

    if dossier_sortie:
        chemin_sortie = Path(dossier_sortie).expanduser()
        if not chemin_sortie.is_absolute():
            chemin_sortie = racine_projet / chemin_sortie
        chemin_sortie.mkdir(parents=True, exist_ok=True)
        return chemin_sortie

    return selectionner_dossier_logs(racine_projet)


def lister_operations() -> List[Dict[str, str]]:
    """Retourne la liste ordonnee des operations de maintenance.

    Args:
        Aucun.

    Returns:
        Liste d operations avec identifiant, titre et description.
    """

    return [
        {
            "id": "diagnostic",
            "titre": "Diagnostic rapide",
            "description": "Controle versions, RAM et espace disque.",
        },
        {
            "id": "actualiser_cibles_migration",
            "titre": "Recharger cibles migration",
            "description": "Detecte versions installees et candidates via CLI.",
        },
        {
            "id": "appliquer_migration_cible",
            "titre": "Appliquer migration cible",
            "description": "Execute la commande de migration de la cible choisie.",
        },
        {
            "id": "preparer_placeholder_ia_migration",
            "titre": "Lancer assistant IA migration",
            "description": "Genere le brief IA puis lance Codex/Ollama en temps reel (code/tests/docs/scripts).",
        },
        {
            "id": "relancer_qualite_complete",
            "titre": "Relancer qualite complete",
            "description": "Relance suite locale et workflows act obligatoires.",
        },
        {
            "id": "proposer_pr_migration",
            "titre": "Proposer PR migration",
            "description": "Pousse la branche courante puis ouvre une PR via gh.",
        },
        {
            "id": "git_pull",
            "titre": "Git pull",
            "description": "Met a jour le depot local en fast-forward.",
        },
        {
            "id": "git_retour_precedent",
            "titre": "Retour commit precedent",
            "description": "Revient au commit precedent (reset --hard HEAD~1) si depot propre.",
        },
        {
            "id": "pipeline_post_pull",
            "titre": "Pipeline post-pull",
            "description": "Compilation, lint, tests et documentation.",
        },
        {
            "id": "mise_a_jour_os",
            "titre": "Mise a jour OS",
            "description": "apt update + apt full-upgrade -y.",
        },
        {
            "id": "reset_pre_requis",
            "titre": "Reset prerequis",
            "description": "Mode sur: purge des prerequis non-systeme + nettoyage local pour retest a zero.",
        },
    ]


def obtenir_fichier_verrouillage(configuration: Dict[str, object]) -> Path:
    """Construit le chemin du fichier de reverrouillage de session.

    Args:
        configuration: Configuration chargee du mode maintenance.

    Returns:
        Chemin absolu du fichier signal de verrouillage.
    """

    nom_fichier = str(configuration.get("fichier_verrouillage", ".verrouillage_mode_maintenance"))
    return Path(__file__).resolve().parent / nom_fichier


def creer_fichier_verrouillage(configuration: Dict[str, object]) -> Path:
    """Cree le fichier signal pour reverrouiller le mode maintenance.

    Args:
        configuration: Configuration chargee du mode maintenance.

    Returns:
        Chemin du fichier cree.
    """

    chemin = obtenir_fichier_verrouillage(configuration)
    contenu = f"verrouille_le={datetime.datetime.now().isoformat(timespec='seconds')}\n"
    chemin.write_text(contenu, encoding="utf-8")
    return chemin


def preparer_ligne_journal(message: str) -> str:
    """Formate une ligne de journal avec horodatage court.

    Args:
        message: Message brut a journaliser.

    Returns:
        Ligne prete a afficher et stocker.
    """

    horodatage = datetime.datetime.now().strftime("%H:%M:%S")
    return f"[{horodatage}] {message}"


def extraire_premiere_ligne_sortie(sortie: str) -> str:
    """Retourne une premiere ligne exploitable meme si la sortie est vide.

    Args:
        sortie: Texte brut de sortie commande.

    Returns:
        Premiere ligne, ou message de repli si vide.
    """

    lignes = sortie.splitlines()
    if not lignes:
        return "(sortie indisponible)"
    return lignes[0]


def paquet_systeme_installe(nom_paquet: str) -> bool:
    """Indique si un paquet systeme est installe via dpkg-query.

    Args:
        nom_paquet: Nom du paquet apt.

    Returns:
        True si le paquet est installe, sinon False.
    """

    if shutil.which("dpkg-query") is None:
        return False

    resultat = subprocess.run(
        ["dpkg-query", "-W", "-f=${Status}", nom_paquet],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding=obtenir_encodage_processus(),
        errors="replace",
        check=False,
    )
    return resultat.returncode == 0 and "install ok installed" in resultat.stdout


def diagnostiquer_pre_requis_borne(journaliser: ConsommateurJournal) -> bool:
    """Diagnostique la presence des pre-requis systeme cibles de la borne.

    Args:
        journaliser: Fonction de journalisation.

    Returns:
        True si tous les pre-requis sont detectes, sinon False.
    """

    journaliser("=== Verification prerequis borne ===")
    succes_global = True

    for paquet in PAQUETS_SYSTEME_BORNE:
        commandes_cibles = COMMANDES_PRE_REQUIS_BORNE.get(paquet, [])
        if paquet_systeme_installe(paquet):
            journaliser(f"OK prerequis paquet: {paquet}")
            continue

        if commandes_cibles and any(shutil.which(commande) is not None for commande in commandes_cibles):
            commande_presente = next(
                commande for commande in commandes_cibles if shutil.which(commande) is not None
            )
            journaliser(
                f"OK prerequis outil: {commande_presente} (paquet apt attendu: {paquet})"
            )
            continue

        succes_global = False
        journaliser(
            "ATTENTION: prerequis manquant: "
            f"{paquet}. Action recommandee: lancez sudo ./bootstrap_borne.sh pour installer automatiquement."
        )

    return succes_global


def charger_configuration_cibles_migration(
    chemin_configuration: Path | None = None,
) -> List[Dict[str, object]]:
    """Charge la definition centralisee des cibles de migration.

    Args:
        chemin_configuration: Fichier JSON optionnel de cibles.

    Returns:
        Liste des cibles de migration disponibles.
    """

    configuration = json.loads(json.dumps(CONFIGURATION_CIBLES_MIGRATION_PAR_DEFAUT))
    chemin = chemin_configuration or FICHIER_CONFIGURATION_CIBLES_MIGRATION
    if not chemin.exists():
        return configuration["cibles"]

    with chemin.open("r", encoding="utf-8") as flux:
        donnees = json.load(flux)

    if isinstance(donnees, dict) and isinstance(donnees.get("cibles"), list):
        return donnees["cibles"]
    return configuration["cibles"]


def executer_commande_capture(
    commande: List[str],
    repertoire_travail: Path,
    timeout_secondes: int = 20,
) -> Tuple[bool, str]:
    """Execute une commande courte et retourne sa sortie combinee.

    Args:
        commande: Liste d arguments shell.
        repertoire_travail: Dossier de travail pour l execution.
        timeout_secondes: Timeout maximal.

    Returns:
        Tuple (succes, sortie combinee).
    """

    try:
        resultat = subprocess.run(
            commande,
            cwd=str(repertoire_travail),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding=obtenir_encodage_processus(),
            errors="replace",
            timeout=max(1, timeout_secondes),
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as erreur:
        return False, str(erreur)
    return resultat.returncode == 0, (resultat.stdout or "").strip()


def extraire_premiere_ligne_non_vide(sortie: str) -> str:
    """Retourne la premiere ligne non vide d une sortie texte.

    Args:
        sortie: Texte source.

    Returns:
        Premiere ligne non vide ou message de repli.
    """

    for ligne in sortie.splitlines():
        ligne_nettoyee = ligne.strip()
        if ligne_nettoyee:
            return ligne_nettoyee
    return "(indisponible)"


def extraire_valeur_apt_policy(sortie: str, cle: str) -> str:
    """Extrait une valeur clee depuis `apt-cache policy`.

    Args:
        sortie: Sortie brute de `apt-cache policy`.
        cle: Cle attendue (`Installed`, `Candidate`, ...).

    Returns:
        Valeur extraite ou chaine vide.
    """

    prefixe = f"{cle}:"
    for ligne in sortie.splitlines():
        ligne_epuree = ligne.strip()
        if ligne_epuree.startswith(prefixe):
            return ligne_epuree.split(":", 1)[1].strip()
    return ""


def lire_variables_os_release(chemin_os_release: Path | None = None) -> Dict[str, str]:
    """Lit le fichier `/etc/os-release` si disponible.

    Args:
        chemin_os_release: Chemin optionnel du fichier a lire.

    Returns:
        Dictionnaire de cles/valeurs shell simplifiees.
    """

    chemin = chemin_os_release or Path("/etc/os-release")
    if not chemin.exists():
        return {}

    variables: Dict[str, str] = {}
    with chemin.open("r", encoding="utf-8") as flux:
        for ligne in flux:
            ligne = ligne.strip()
            if not ligne or "=" not in ligne or ligne.startswith("#"):
                continue
            cle, valeur = ligne.split("=", 1)
            variables[cle] = valeur.strip().strip('"')
    return variables


def decrire_support_hote_migration_apt(exiger_os_release: bool = False) -> Tuple[bool, str]:
    """Indique si l hote courant supporte la migration via apt.

    Args:
        exiger_os_release: True pour exiger `/etc/os-release`.

    Returns:
        Tuple (supportee, raison si indisponible).
    """

    if os.name != "posix":
        return False, MESSAGE_HOTE_APT_NON_SUPPORTE

    commandes_obligatoires = ["apt-get", "apt-cache", "dpkg-query"]
    manquants = [commande for commande in commandes_obligatoires if shutil.which(commande) is None]
    if manquants:
        return (
            False,
            f"{MESSAGE_HOTE_APT_NON_SUPPORTE} Outils manquants: {', '.join(manquants)}.",
        )

    variables_os_release = lire_variables_os_release()
    if not variables_os_release:
        return (
            False,
            f"{MESSAGE_HOTE_APT_NON_SUPPORTE} Fichier /etc/os-release absent.",
        )

    identifiant_systeme = variables_os_release.get("ID", "").strip().lower()
    nom_systeme = variables_os_release.get("PRETTY_NAME", "").strip()
    if identifiant_systeme in {"debian", "raspbian"} or "raspberry pi os" in nom_systeme.lower():
        return True, ""

    return (
        False,
        f"{MESSAGE_HOTE_APT_NON_SUPPORTE} Systeme detecte: {nom_systeme or identifiant_systeme or '(indisponible)'}.",
    )


def obtenir_version_systeme_installee() -> str:
    """Retourne une description lisible du systeme courant.

    Args:
        Aucun.

    Returns:
        Texte lisible du systeme ou `(indisponible)`.
    """

    variables = lire_variables_os_release()
    if not variables:
        return "(indisponible)"

    pretty_name = variables.get("PRETTY_NAME", "").strip()
    version_id = variables.get("VERSION_ID", "").strip()
    if pretty_name and version_id and version_id not in pretty_name:
        return f"{pretty_name} ({version_id})"
    if pretty_name:
        return pretty_name
    if version_id:
        return version_id
    return "(indisponible)"


def obtenir_version_paquet_installee(paquet: str, racine_projet: Path) -> str:
    """Retourne la version installee d un paquet via `dpkg-query`.

    Args:
        paquet: Nom du paquet Debian.
        racine_projet: Racine du depot pour l execution.

    Returns:
        Version installee ou `(aucune)`.
    """

    if shutil.which("dpkg-query") is None:
        return "(indisponible)"

    succes, sortie = executer_commande_capture(
        ["dpkg-query", "-W", "-f=${Version}", paquet],
        racine_projet,
    )
    if not succes or not sortie:
        return "(aucune)"
    return sortie


def obtenir_version_candidate_paquet(paquet: str, racine_projet: Path) -> str:
    """Retourne la version candidate d un paquet via `apt-cache policy`.

    Args:
        paquet: Nom du paquet Debian.
        racine_projet: Racine du depot pour l execution.

    Returns:
        Version candidate ou `(indisponible)`.
    """

    if shutil.which("apt-cache") is None:
        return "(indisponible)"

    succes, sortie = executer_commande_capture(["apt-cache", "policy", paquet], racine_projet)
    if not succes:
        return "(indisponible)"

    version_candidate = extraire_valeur_apt_policy(sortie, "Candidate")
    if not version_candidate:
        return "(indisponible)"
    return version_candidate


def obtenir_version_humaine_installee(
    definition_cible: Dict[str, object],
    racine_projet: Path,
) -> str:
    """Retourne une version lisible pour l interface a partir d une commande.

    Args:
        definition_cible: Definition de cible de migration.
        racine_projet: Racine du depot pour l execution.

    Returns:
        Version lisible ou `(indisponible)`.
    """

    commande = definition_cible.get("commande_version_installee")
    if not isinstance(commande, list) or not commande:
        return "(indisponible)"

    succes, sortie = executer_commande_capture([str(argument) for argument in commande], racine_projet)
    if not succes:
        return "(indisponible)"
    return extraire_premiere_ligne_non_vide(sortie)


def version_candidate_superieure(version_installee: str, version_candidate: str) -> bool:
    """Indique si une version candidate est superieure a la version installee.

    Args:
        version_installee: Version actuellement installee.
        version_candidate: Version candidate detectee.

    Returns:
        True si la candidate est plus recente.
    """

    if version_candidate in {"", "(indisponible)", "(none)"}:
        return False
    if version_installee in {"", "(aucune)", "(none)"}:
        return True
    if shutil.which("dpkg") is None:
        return version_candidate != version_installee

    resultat = subprocess.run(
        ["dpkg", "--compare-versions", version_candidate, "gt", version_installee],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding=obtenir_encodage_processus(),
        errors="replace",
        check=False,
    )
    return resultat.returncode == 0


def compter_mises_a_jour_systeme_candidats(racine_projet: Path) -> Tuple[int, str]:
    """Compte les paquets qui seraient modifies par `apt-get -s full-upgrade`.

    Args:
        racine_projet: Racine du depot pour l execution.

    Returns:
        Tuple (nombre de paquets, resume lisible).
    """

    if shutil.which("apt-get") is None:
        return 0, "(indisponible)"

    succes, sortie = executer_commande_capture(["apt-get", "-s", "full-upgrade"], racine_projet, timeout_secondes=60)
    if not succes:
        return 0, "(indisponible)"

    lignes_inst = [ligne.strip() for ligne in sortie.splitlines() if ligne.startswith("Inst ")]
    nombre_paquets = len(lignes_inst)
    if nombre_paquets == 0:
        return 0, "Aucune mise a jour systeme candidate"
    return nombre_paquets, f"{nombre_paquets} paquet(s) apt a mettre a jour"


def formater_commande_migration_lisible(commandes: List[List[str]]) -> str:
    """Retourne une representation lisible d une liste de commandes de migration.

    Args:
        commandes: Commandes shell sequentielles.

    Returns:
        Texte compact des commandes.
    """

    segments = [" ".join(commande) for commande in commandes if commande]
    if not segments:
        return "(aucune commande)"
    return " ; ".join(segments)


def collecter_cibles_migration(racine_projet: Path | None = None) -> List[Dict[str, object]]:
    """Construit le catalogue vivant des cibles de migration.

    Args:
        racine_projet: Racine du depot optionnelle.

    Returns:
        Liste de cibles enrichies avec versions et etat de migration.
    """

    racine = racine_projet or obtenir_racine_projet()
    cibles_calculees: List[Dict[str, object]] = []

    for definition in charger_configuration_cibles_migration():
        cible = dict(definition)
        type_cible = str(cible.get("type", ""))
        commandes_migration = cible.get("commandes_migration", [])
        if not isinstance(commandes_migration, list):
            commandes_migration = []
        cible["commandes_migration"] = commandes_migration
        cible["commande_migration_lisible"] = formater_commande_migration_lisible(commandes_migration)
        cible["supportee_sur_hote"] = True
        cible["raison_indisponibilite"] = ""

        if type_cible == "systeme_apt":
            supportee, raison = decrire_support_hote_migration_apt(exiger_os_release=True)
            version_installee = obtenir_version_systeme_installee()
            nombre_paquets = 0
            version_candidate = "(indisponible)"
            if supportee:
                nombre_paquets, version_candidate = compter_mises_a_jour_systeme_candidats(racine)
            cible["version_installee"] = version_installee
            cible["version_candidate"] = version_candidate
            cible["supportee_sur_hote"] = supportee
            cible["raison_indisponibilite"] = raison
            if supportee:
                cible["migration_disponible"] = nombre_paquets > 0
                cible["resume_migration"] = (
                    "Migration disponible" if nombre_paquets > 0 else "Systeme deja aligne"
                )
            else:
                cible["migration_disponible"] = False
                cible["resume_migration"] = "Migration indisponible sur cet hote"
        else:
            supportee, raison = decrire_support_hote_migration_apt()
            paquet_apt = str(cible.get("paquet_apt", ""))
            version_installee = obtenir_version_humaine_installee(cible, racine)
            version_installee_paquet = "(indisponible)"
            version_candidate = "(indisponible)"
            if supportee:
                version_installee_paquet = obtenir_version_paquet_installee(paquet_apt, racine)
                version_candidate = obtenir_version_candidate_paquet(paquet_apt, racine)
            if version_installee == "(indisponible)" and version_installee_paquet != "(indisponible)":
                version_installee = version_installee_paquet
            cible["version_installee"] = version_installee
            cible["version_candidate"] = version_candidate
            cible["version_paquet_installee"] = version_installee_paquet
            cible["supportee_sur_hote"] = supportee
            cible["raison_indisponibilite"] = raison
            cible["migration_disponible"] = supportee and version_candidate_superieure(
                version_installee_paquet,
                version_candidate,
            )
            if supportee:
                cible["resume_migration"] = (
                    "Migration disponible" if cible["migration_disponible"] else "Composant deja aligne"
                )
            else:
                cible["resume_migration"] = "Migration indisponible sur cet hote"

        cibles_calculees.append(cible)

    return cibles_calculees


def selectionner_cible_migration(
    cibles: List[Dict[str, object]],
    identifiant: str,
) -> Dict[str, object] | None:
    """Retourne la cible de migration correspondant a un identifiant.

    Args:
        cibles: Catalogue calcule des cibles.
        identifiant: Identifiant recherche.

    Returns:
        Dictionnaire cible ou None si absent.
    """

    for cible in cibles:
        if cible.get("id") == identifiant:
            return cible
    return None


def extraire_identifiant_cible_migration(contexte_operation: Dict[str, object] | None) -> str:
    """Extrait l identifiant de cible de migration depuis un contexte d operation.

    Args:
        contexte_operation: Contexte optionnel fourni par l interface.

    Returns:
        Identifiant ou chaine vide.
    """

    if not isinstance(contexte_operation, dict):
        return ""
    identifiant = contexte_operation.get("cible_migration_id", "")
    if not isinstance(identifiant, str):
        return ""
    return identifiant.strip()


def verifier_etat_migration_pour_cible(
    racine_projet: Path,
    cible: Dict[str, object],
    exiger_migration: bool = False,
    exiger_assistant_ia: bool = False,
    exiger_qualite: bool = False,
    autoriser_commit_courant_different: bool = False,
) -> Tuple[bool, str, Dict[str, object]]:
    """Verifie qu un etat de migration coherent existe pour une cible.

    Args:
        racine_projet: Racine du depot.
        cible: Cible attendue.
        exiger_migration: True pour exiger une migration appliquee.
        exiger_assistant_ia: True pour exiger l execution de l assistant IA.
        exiger_qualite: True pour exiger une qualite verifiee.
        autoriser_commit_courant_different: True pour reutiliser la session sur un nouveau commit.

    Returns:
        Tuple (etat_valide, message_si_ko, etat_charge).
    """

    etat = charger_etat_migration(racine_projet)
    if not etat:
        return (
            False,
            "Aucune session de migration enregistree. "
            "Action recommandee: appliquez d abord la migration de la cible choisie.",
            {},
        )

    if etat.get("cible_id") != cible.get("id"):
        return (
            False,
            "La session de migration courante ne correspond pas a la cible selectionnee. "
            "Action recommandee: reappliquez la migration pour cette cible.",
            etat,
        )

    if exiger_migration and not etat.get("migration_appliquee"):
        return (
            False,
            "La migration n a pas encore ete appliquee pour cette cible. "
            "Action recommandee: lancez d abord l operation d application.",
            etat,
        )

    if exiger_assistant_ia and not etat.get("placeholder_ia_genere"):
        return (
            False,
            "L etape assistant IA n a pas encore ete executee pour cette cible. "
            "Action recommandee: lancez d abord `preparer-ia`.",
            etat,
        )

    if exiger_qualite and not etat.get("qualite_verifiee"):
        return (
            False,
            "La qualite complete n a pas ete validee pour cette cible. "
            "Action recommandee: lancez l operation de qualite avant la PR.",
            etat,
        )

    contexte_git = capturer_contexte_git(racine_projet)
    commit_actuel = str(contexte_git.get("commit_git", "(indisponible)"))
    commit_session = str(etat.get("commit_git", "(indisponible)"))
    if (
        not autoriser_commit_courant_different
        and commit_session
        and commit_session != "(indisponible)"
        and commit_actuel != commit_session
    ):
        return (
            False,
            "Le commit courant ne correspond plus a la session de migration enregistree. "
            "Action recommandee: relancez la qualite sur le commit actuel.",
            etat,
        )

    return True, "", etat


def construire_etat_session_migration(
    cible: Dict[str, object],
    racine_projet: Path,
    migration_appliquee: bool,
) -> Dict[str, object]:
    """Construit un etat initial de session pour une migration.

    Args:
        cible: Cible concernee.
        racine_projet: Racine du depot.
        migration_appliquee: Etat de la migration systeme.

    Returns:
        Dictionnaire complet d etat de session.
    """

    contexte_git = capturer_contexte_git(racine_projet)
    return {
        "cible_id": cible.get("id", ""),
        "titre": cible.get("titre", ""),
        "version_installee": cible.get("version_installee", "(indisponible)"),
        "version_candidate": cible.get("version_candidate", "(indisponible)"),
        "branche_git": contexte_git.get("branche_git", "(indisponible)"),
        "commit_git": contexte_git.get("commit_git", "(indisponible)"),
        "migration_appliquee": migration_appliquee,
        "placeholder_ia_genere": False,
        "chemin_placeholder_md": "",
        "chemin_placeholder_json": "",
        "chemin_reponse_ia": "",
        "chemin_transcription_ia_jsonl": "",
        "qualite_verifiee": False,
        "chemin_rapport_qualite": "",
        "horodatage_derniere_etape": datetime.datetime.now().isoformat(timespec="seconds"),
    }


def mettre_a_jour_etat_session_migration(
    racine_projet: Path,
    mises_a_jour: Dict[str, object],
) -> Dict[str, object]:
    """Fusionne puis persiste des mises a jour de session migration.

    Args:
        racine_projet: Racine du depot.
        mises_a_jour: Valeurs a fusionner dans l etat.

    Returns:
        Etat resultant apres ecriture.
    """

    etat = charger_etat_migration(racine_projet)
    etat.update(mises_a_jour)
    etat["horodatage_derniere_etape"] = datetime.datetime.now().isoformat(timespec="seconds")
    contexte_git = capturer_contexte_git(racine_projet)
    etat["branche_git"] = contexte_git.get("branche_git", "(indisponible)")
    etat["commit_git"] = contexte_git.get("commit_git", "(indisponible)")
    enregistrer_etat_migration(racine_projet, etat)
    return etat


def lister_documents_migration_a_mettre_a_jour() -> List[str]:
    """Retourne la liste documentaire cible du workflow de migration.

    Args:
        Aucun.

    Returns:
        Liste ordonnee des documents a reviser.
    """

    return list(DOCUMENTS_MIGRATION_IA)


def sanitiser_fragment_git(valeur: str) -> str:
    """Sanitise un fragment de texte pour un usage branche/titre git.

    Args:
        valeur: Texte brut.

    Returns:
        Chaine nettoyee compatible git.
    """

    valeur_nettoyee = re.sub(r"[^a-zA-Z0-9._-]+", "-", valeur.strip().lower())
    valeur_nettoyee = re.sub(r"-{2,}", "-", valeur_nettoyee).strip("-")
    return valeur_nettoyee or "migration"


def construire_nom_branche_migration(cible: Dict[str, object]) -> str:
    """Construit un nom de branche recommande pour une migration.

    Args:
        cible: Cible selectionnee.

    Returns:
        Nom de branche propose.
    """

    identifiant = sanitiser_fragment_git(str(cible.get("id", "migration")))
    candidate = sanitiser_fragment_git(str(cible.get("version_candidate", "candidate")))
    return f"migration/{identifiant}-{candidate}"


def generer_titre_pr_migration(cible: Dict[str, object]) -> str:
    """Construit un titre standardise de Pull Request pour une migration.

    Args:
        cible: Cible selectionnee.

    Returns:
        Titre de PR propose.
    """

    titre_cible = str(cible.get("titre", "migration"))
    version_candidate = str(cible.get("version_candidate", "candidate"))
    return f"chore: migrer {titre_cible} vers {version_candidate}"


def rendre_chemin_relatif_au_projet(racine_projet: Path, chemin: Path) -> str:
    """Retourne un chemin relatif au depot quand c est possible.

    Args:
        racine_projet: Racine du depot.
        chemin: Chemin absolu ou relatif a formater.

    Returns:
        Chemin relatif portable pour affichage/prompt.
    """

    try:
        return str(chemin.resolve().relative_to(racine_projet.resolve())).replace("\\", "/")
    except ValueError:
        return str(chemin)


def charger_modele_prompt_assistant_ia(
    racine_projet: Path,
    configuration_assistant: Dict[str, object],
) -> str:
    """Charge le template texte du prompt de migration assistee.

    Args:
        racine_projet: Racine du depot.
        configuration_assistant: Configuration chargee de l assistant IA.

    Returns:
        Texte du prompt de base, ou un modele integre en repli.
    """

    configuration_prompt = configuration_assistant.get("prompt", {})
    chemin_modele = ""
    if isinstance(configuration_prompt, dict):
        valeur = configuration_prompt.get("chemin_modele", "")
        if isinstance(valeur, str):
            chemin_modele = valeur.strip()

    candidats: List[Path] = []
    if chemin_modele:
        candidat = Path(chemin_modele).expanduser()
        if not candidat.is_absolute():
            candidat = racine_projet / candidat
        candidats.append(candidat)
    candidats.append(FICHIER_MODELE_PROMPT_ASSISTANT_IA)

    deja_vus: set[Path] = set()
    for candidat in candidats:
        if candidat in deja_vus:
            continue
        deja_vus.add(candidat)
        if candidat.exists():
            return candidat.read_text(encoding="utf-8")

    return "\n".join(
        [
            "Tu es l assistant IA de migration de versions pour ArcadeCare.",
            "",
            "Objectif:",
            "- Rendre le depot compatible avec la cible {{CIBLE_TITRE}}.",
            "- Adapter le code, les tests, la documentation et les scripts touches par la migration.",
            "",
            "Contexte obligatoire:",
            "- Lire d abord {{CHEMIN_BRIEF_JSON}} puis {{CHEMIN_BRIEF_MARKDOWN}}.",
            "- Respecter strictement AGENTS.md.",
            "- Ne jamais modifier MG2D/.",
            "",
            "Validation obligatoire:",
            "{{COMMANDES_QUALITE}}",
            "",
            "Sortie finale attendue:",
            "- Resume des changements.",
            "- Tests/commandes executes et resultat.",
            "- Risques ou blocages restants.",
        ]
    )


def construire_payload_contexte_ia_migration(
    cible: Dict[str, object],
    etat_session: Dict[str, object],
    configuration_assistant: Dict[str, object],
    racine_projet: Path,
    chemins_artefacts: Dict[str, Path],
) -> Dict[str, object]:
    """Construit le manifeste JSON stable du brief de migration IA.

    Args:
        cible: Cible de migration selectionnee.
        etat_session: Etat de session courant.
        configuration_assistant: Configuration locale Codex/Ollama.
        racine_projet: Racine du depot.
        chemins_artefacts: Chemins des artefacts de contexte/reponse.

    Returns:
        Dictionnaire JSON stable a serialiser.
    """

    configuration_codex = configuration_assistant.get("codex", {})
    configuration_ollama = configuration_assistant.get("ollama", {})
    configuration_context7 = (
        configuration_assistant.get("mcp", {}).get("context7", {})
        if isinstance(configuration_assistant.get("mcp", {}), dict)
        else {}
    )
    return {
        "contexte": {
            "workflow": "migration_versions_borne_arcade",
            "horodatage": datetime.datetime.now().isoformat(timespec="seconds"),
            "ordre_impose": [
                "detection",
                "choix_cible",
                "migration",
                "adaptation_ia",
                "qualite",
                "proposition_pr",
                "revue_humaine",
                "merge_apres_accord",
            ],
        },
        "artefacts": {
            "brief_markdown": rendre_chemin_relatif_au_projet(racine_projet, chemins_artefacts["brief_markdown"]),
            "brief_json": rendre_chemin_relatif_au_projet(racine_projet, chemins_artefacts["brief_json"]),
            "reponse_ia_markdown": rendre_chemin_relatif_au_projet(
                racine_projet,
                chemins_artefacts["reponse_ia_markdown"],
            ),
            "transcription_ia_jsonl": rendre_chemin_relatif_au_projet(
                racine_projet,
                chemins_artefacts["transcription_ia_jsonl"],
            ),
        },
        "cible": {
            "id": cible.get("id"),
            "titre": cible.get("titre"),
            "description": cible.get("description"),
            "type": cible.get("type"),
            "commande_migration_lisible": cible.get("commande_migration_lisible"),
        },
        "versions": {
            "installee": cible.get("version_installee"),
            "candidate": cible.get("version_candidate"),
        },
        "git": {
            "branche_git": etat_session.get("branche_git", "(indisponible)"),
            "commit_git": etat_session.get("commit_git", "(indisponible)"),
        },
        "assistant_ia": {
            "orchestrateur": "codex exec",
            "modele": configuration_codex.get("modele", "qwen3:8b"),
            "fournisseur_local": configuration_codex.get("fournisseur_local", "ollama"),
            "base_url_oss": normaliser_base_url_codex_oss(
                str(configuration_ollama.get("base_url", "")) if isinstance(configuration_ollama, dict) else ""
            ),
            "utiliser_provider_oss": bool(configuration_codex.get("utiliser_provider_oss", True)),
            "recherche_web_activee": bool(configuration_codex.get("activer_recherche_web", True)),
            "mcp_context7_actif": bool(configuration_context7.get("actif", True)),
        },
        "travaux_attendus": [
            "Adapter le code source impacte par la migration.",
            "Mettre a jour les tests automatiques necessaires.",
            "Mettre a jour la documentation dans docs/.",
            "Mettre a jour les scripts de build, installation et deploiement si necessaire.",
            "Relancer toute la qualite jusqu au vert avant la proposition de PR.",
        ],
        "documents_a_mettre_a_jour": lister_documents_migration_a_mettre_a_jour(),
        "commandes_qualite": list(COMMANDES_QUALITE_MIGRATION),
        "criteres_acceptation": [
            "Toutes les commandes qualite doivent etre vertes.",
            "La PR doit etre proposee uniquement via CLI.",
            "La relecture humaine reste obligatoire.",
            "Le merge est interdit sans accord explicite.",
        ],
        "backend_ia": {
            "backend": "codex",
            "provider_local": configuration_codex.get("fournisseur_local", "ollama"),
            "modele": configuration_codex.get("modele", "qwen3:8b"),
            "message": "Execution pilotee par `codex exec --json` avec streaming temps reel.",
        },
    }


def construire_contenu_brief_ia_markdown(
    cible: Dict[str, object],
    etat_session: Dict[str, object],
    configuration_assistant: Dict[str, object],
    racine_projet: Path,
    chemins_artefacts: Dict[str, Path],
) -> str:
    """Construit le brief Markdown lu par l humain et par l agent.

    Args:
        cible: Cible de migration selectionnee.
        etat_session: Etat de session courant.
        configuration_assistant: Configuration locale Codex/Ollama.
        racine_projet: Racine du depot.
        chemins_artefacts: Chemins des artefacts de contexte/reponse.

    Returns:
        Texte Markdown complet.
    """

    lignes_documents = [f"- `{document}`" for document in lister_documents_migration_a_mettre_a_jour()]
    lignes_commandes = [f"- `{commande}`" for commande in COMMANDES_QUALITE_MIGRATION]
    configuration_codex = configuration_assistant.get("codex", {})
    configuration_ollama = configuration_assistant.get("ollama", {})
    return "\n".join(
        [
            "# Brief IA migration",
            "",
            "## Etat courant",
            f"- Cible: {cible.get('titre')}",
            f"- Identifiant: {cible.get('id')}",
            f"- Version installee: {cible.get('version_installee')}",
            f"- Version candidate: {cible.get('version_candidate')}",
            f"- Commande de migration: {cible.get('commande_migration_lisible')}",
            f"- Branche git: {etat_session.get('branche_git', '(indisponible)')}",
            f"- Commit git: {etat_session.get('commit_git', '(indisponible)')}",
            "",
            "## Backend IA",
            f"- Orchestrateur: `codex exec --json`",
            f"- Provider local: `{configuration_codex.get('fournisseur_local', 'ollama')}`",
            f"- Modele: `{configuration_codex.get('modele', 'qwen3:8b')}`",
            f"- Serveur Ollama: `{normaliser_base_url_codex_oss(str(configuration_ollama.get('base_url', '')) if isinstance(configuration_ollama, dict) else '')}`",
            f"- Recherche web live: {'oui' if configuration_codex.get('activer_recherche_web', True) else 'non'}",
            "",
            "## Artefacts",
            f"- Brief JSON: `{rendre_chemin_relatif_au_projet(racine_projet, chemins_artefacts['brief_json'])}`",
            f"- Reponse IA: `{rendre_chemin_relatif_au_projet(racine_projet, chemins_artefacts['reponse_ia_markdown'])}`",
            f"- Trace JSONL: `{rendre_chemin_relatif_au_projet(racine_projet, chemins_artefacts['transcription_ia_jsonl'])}`",
            "",
            "## Travail attendu de l assistant IA",
            "1. Adapter le code source impacte par la migration.",
            "2. Mettre a jour les tests automatiques necessaires.",
            "3. Mettre a jour la documentation dans docs/.",
            "4. Mettre a jour les scripts de build/deploiement si necessaire.",
            "5. Relancer toute la qualite jusqu au vert.",
            "",
            "## Documents a verifier",
            *lignes_documents,
            "",
            "## Commandes qualite obligatoires",
            *lignes_commandes,
            "",
            "## Gouvernance",
            "- Proposer la PR en ligne de commande uniquement.",
            "- Revue humaine obligatoire.",
            "- Merge interdit sans accord explicite.",
        ]
    )


def construire_prompt_assistant_ia_migration(
    modele_prompt: str,
    cible: Dict[str, object],
    etat_session: Dict[str, object],
    configuration_assistant: Dict[str, object],
    racine_projet: Path,
    chemins_artefacts: Dict[str, Path],
) -> str:
    """Construit le prompt final transmis a Codex.

    Args:
        modele_prompt: Template de prompt.
        cible: Cible de migration selectionnee.
        etat_session: Etat persistant de la session.
        configuration_assistant: Configuration locale Codex/Ollama.
        racine_projet: Racine du depot.
        chemins_artefacts: Chemins du brief et des sorties IA.

    Returns:
        Prompt final pret a etre envoye sur stdin.
    """

    configuration_codex = configuration_assistant.get("codex", {})
    substitutions = {
        "{{RACINE_PROJET}}": str(racine_projet),
        "{{CIBLE_ID}}": str(cible.get("id", "")),
        "{{CIBLE_TITRE}}": str(cible.get("titre", "")),
        "{{VERSION_INSTALLEE}}": str(cible.get("version_installee", "(indisponible)")),
        "{{VERSION_CANDIDATE}}": str(cible.get("version_candidate", "(indisponible)")),
        "{{COMMANDE_MIGRATION}}": str(cible.get("commande_migration_lisible", "(indisponible)")),
        "{{BRANCHE_GIT}}": str(etat_session.get("branche_git", "(indisponible)")),
        "{{COMMIT_GIT}}": str(etat_session.get("commit_git", "(indisponible)")),
        "{{MODELE_IA}}": str(configuration_codex.get("modele", "qwen3:8b")),
        "{{FOURNISSEUR_LOCAL_IA}}": str(configuration_codex.get("fournisseur_local", "ollama")),
        "{{CHEMIN_BRIEF_JSON}}": rendre_chemin_relatif_au_projet(racine_projet, chemins_artefacts["brief_json"]),
        "{{CHEMIN_BRIEF_MARKDOWN}}": rendre_chemin_relatif_au_projet(
            racine_projet,
            chemins_artefacts["brief_markdown"],
        ),
        "{{CHEMIN_REPONSE_IA}}": rendre_chemin_relatif_au_projet(
            racine_projet,
            chemins_artefacts["reponse_ia_markdown"],
        ),
        "{{CHEMIN_TRACE_IA_JSONL}}": rendre_chemin_relatif_au_projet(
            racine_projet,
            chemins_artefacts["transcription_ia_jsonl"],
        ),
        "{{DOCUMENTS_A_METTRE_A_JOUR}}": "\n".join(
            f"- `{document}`" for document in lister_documents_migration_a_mettre_a_jour()
        ),
        "{{COMMANDES_QUALITE}}": "\n".join(f"- `{commande}`" for commande in COMMANDES_QUALITE_MIGRATION),
    }

    prompt = modele_prompt
    for marqueur, valeur in substitutions.items():
        prompt = prompt.replace(marqueur, valeur)
    return prompt.strip() + "\n"


def construire_surcharges_codex_context7(configuration_assistant: Dict[str, object]) -> List[str]:
    """Construit les surcharges `-c` pour activer Context7 dans Codex.

    Args:
        configuration_assistant: Configuration de l assistant IA.

    Returns:
        Liste de paires cle/valeur au format Codex CLI.
    """

    configuration_mcp = configuration_assistant.get("mcp", {})
    if not isinstance(configuration_mcp, dict):
        return []
    configuration_context7 = configuration_mcp.get("context7", {})
    if not isinstance(configuration_context7, dict):
        return []

    arguments_context7 = configuration_context7.get("arguments", ["-y", "@upstash/context7-mcp"])
    if not isinstance(arguments_context7, list):
        arguments_context7 = ["-y", "@upstash/context7-mcp"]

    return [
        f"mcp_servers.context7.command={json.dumps(str(configuration_context7.get('commande', 'npx')))}",
        f"mcp_servers.context7.args={json.dumps([str(argument) for argument in arguments_context7])}",
        f"mcp_servers.context7.startup_timeout_sec={int(configuration_context7.get('delai_demarrage_secondes', 120))}",
        f"mcp_servers.context7.tool_timeout_sec={int(configuration_context7.get('timeout_outil_secondes', 300))}",
        f"mcp_servers.context7.enabled={'true' if configuration_context7.get('actif', True) else 'false'}",
    ]


def normaliser_base_url_codex_oss(base_url: str) -> str:
    """Normalise l URL d un serveur OSS compatible Codex.

    Args:
        base_url: URL brute issue de la configuration.

    Returns:
        URL normalisee pointant sur le prefixe `/v1`.
    """

    url = base_url.strip().rstrip("/")
    if not url:
        return ""
    if url.endswith("/v1"):
        return url
    return f"{url}/v1"


def construire_environnement_codex_migration(configuration_assistant: Dict[str, object]) -> Dict[str, str]:
    """Construit les variables d environnement pour l execution Codex.

    Args:
        configuration_assistant: Configuration locale Codex/Ollama.

    Returns:
        Variables d environnement a injecter au processus.
    """

    environnement: Dict[str, str] = {}
    configuration_codex = configuration_assistant.get("codex", {})
    configuration_ollama = configuration_assistant.get("ollama", {})
    if not isinstance(configuration_codex, dict) or not isinstance(configuration_ollama, dict):
        return environnement

    fournisseur_local = str(configuration_codex.get("fournisseur_local", "ollama")).strip().lower()
    if fournisseur_local != "ollama":
        return environnement

    base_url = str(configuration_ollama.get("base_url", "")).strip()
    base_url_normalisee = normaliser_base_url_codex_oss(base_url)
    if base_url_normalisee:
        environnement["CODEX_OSS_BASE_URL"] = base_url_normalisee
    return environnement


def construire_commande_codex_migration(
    configuration_assistant: Dict[str, object],
    racine_projet: Path,
    chemin_reponse_ia: Path,
) -> List[str]:
    """Construit la ligne de commande Codex pour l etape IA de migration.

    Args:
        configuration_assistant: Configuration locale Codex/Ollama.
        racine_projet: Racine du depot.
        chemin_reponse_ia: Fichier de sortie du dernier message agent.

    Returns:
        Liste d arguments prete pour `subprocess.Popen`.
    """

    configuration_codex = configuration_assistant.get("codex", {})
    if not isinstance(configuration_codex, dict):
        configuration_codex = {}

    commande = [str(configuration_codex.get("commande", "codex")), "exec"]
    if configuration_codex.get("utiliser_provider_oss", True):
        commande.append("--oss")

    fournisseur_local = str(configuration_codex.get("fournisseur_local", "ollama")).strip()
    if fournisseur_local:
        commande.extend(["--local-provider", fournisseur_local])

    modele = str(configuration_codex.get("modele", "qwen3:8b")).strip()
    if modele:
        commande.extend(["-m", modele])

    politique_approbation = str(configuration_codex.get("politique_approbation", "never")).strip()
    mode_sandbox = str(configuration_codex.get("sandbox", "danger-full-access")).strip()
    if politique_approbation == "never" and mode_sandbox == "danger-full-access":
        commande.append("--dangerously-bypass-approvals-and-sandbox")
    elif politique_approbation == "on-request" and mode_sandbox == "workspace-write":
        commande.append("--full-auto")
    elif mode_sandbox:
        commande.extend(["-s", mode_sandbox])

    couleur = str(configuration_codex.get("couleur", "never")).strip()
    if couleur:
        commande.extend(["--color", couleur])

    if configuration_codex.get("sortie_json", True):
        commande.append("--json")

    commande.extend(["-C", str(racine_projet), "-o", str(chemin_reponse_ia)])
    if configuration_codex.get("ignorer_verification_git", False):
        commande.append("--skip-git-repo-check")

    for surcharge in construire_surcharges_codex_context7(configuration_assistant):
        commande.extend(["-c", surcharge])

    arguments_supplementaires = configuration_codex.get("arguments_supplementaires", [])
    if isinstance(arguments_supplementaires, list):
        commande.extend(str(argument) for argument in arguments_supplementaires)

    commande.append("-")
    return commande


def verifier_outils_assistant_ia(configuration_assistant: Dict[str, object]) -> Tuple[bool, str]:
    """Verifie la disponibilite minimale de Codex et de la configuration OSS.

    Args:
        configuration_assistant: Configuration locale Codex/Ollama.

    Returns:
        Tuple (succes, message en cas d erreur).
    """

    configuration_codex = configuration_assistant.get("codex", {})
    configuration_ollama = configuration_assistant.get("ollama", {})
    commande_codex = (
        str(configuration_codex.get("commande", "codex"))
        if isinstance(configuration_codex, dict)
        else "codex"
    )
    fournisseur_local = (
        str(configuration_codex.get("fournisseur_local", "ollama")).strip().lower()
        if isinstance(configuration_codex, dict)
        else "ollama"
    )

    if shutil.which(commande_codex) is None:
        return (
            False,
            f"Assistant IA impossible: commande `{commande_codex}` introuvable. "
            "Action recommandee: installez Codex CLI puis relancez `preparer-ia`.",
        )

    if fournisseur_local == "ollama":
        base_url = (
            str(configuration_ollama.get("base_url", ""))
            if isinstance(configuration_ollama, dict)
            else ""
        ).strip()
        if not normaliser_base_url_codex_oss(base_url):
            return (
                False,
                "Assistant IA impossible: URL du serveur Ollama absente. "
                "Action recommandee: renseignez `ollama.base_url` dans `config/assistant_ia_migration.json`.",
            )

    return True, ""


def ecrire_reponse_ia_si_absente(chemin_reponse_ia: Path, contenu: str) -> bool:
    """Ecrit la reponse IA si aucun fichier final n a encore ete produit.

    Args:
        chemin_reponse_ia: Fichier cible de la reponse agent.
        contenu: Contenu de secours a ecrire.

    Returns:
        True si le fichier existe et contient un texte non vide apres l operation.
    """

    if chemin_reponse_ia.exists() and chemin_reponse_ia.read_text(encoding="utf-8").strip():
        return True

    if contenu.strip():
        chemin_reponse_ia.write_text(contenu.strip() + "\n", encoding="utf-8")
        return True

    return False


def extraire_texte_evenement_codex(item: Dict[str, object]) -> str:
    """Extrait un texte utile depuis un item JSONL emis par Codex.

    Args:
        item: Item brut de l evenement `item.completed`.

    Returns:
        Texte normalise sur une ligne ou plusieurs.
    """

    for cle in ("text", "message", "content", "summary"):
        valeur = item.get(cle)
        if isinstance(valeur, str) and valeur.strip():
            return valeur.strip()
    return ""


def formater_lignes_evenement_codex(
    ligne_brute: str,
    etat_evenements: Dict[str, object],
) -> List[str]:
    """Transforme une ligne JSONL Codex en journal lisible pour l interface.

    Args:
        ligne_brute: Ligne brute issue de stdout.
        etat_evenements: Etat mutable de collecte du flux.

    Returns:
        Liste de lignes a injecter dans le journal.
    """

    ligne = ligne_brute.strip()
    if not ligne:
        return []

    try:
        evenement = json.loads(ligne)
    except json.JSONDecodeError:
        return [f"IA brut: {ligne}"]

    if not isinstance(evenement, dict):
        return [f"IA evenement non supporte: {ligne}"]

    type_evenement = str(evenement.get("type", ""))
    if type_evenement == "thread.started":
        identifiant = str(evenement.get("thread_id", "(indisponible)"))
        return [f"IA session demarree: {identifiant}"]
    if type_evenement == "turn.started":
        return ["IA tour demarre."]
    if type_evenement == "turn.completed":
        usage = evenement.get("usage", {})
        if isinstance(usage, dict):
            etat_evenements["usage"] = usage
            entree = usage.get("input_tokens", 0)
            sortie = usage.get("output_tokens", 0)
            return [f"IA tour termine. Tokens entree={entree}, sortie={sortie}."]
        return ["IA tour termine."]

    if type_evenement != "item.completed":
        return []

    item = evenement.get("item", {})
    if not isinstance(item, dict):
        return []

    type_item = str(item.get("type", ""))
    texte = extraire_texte_evenement_codex(item)
    if type_item == "agent_message":
        if texte:
            etat_evenements["dernier_message_agent"] = texte
            return [f"IA: {ligne_texte}" for ligne_texte in texte.splitlines() if ligne_texte.strip()]
        return ["IA: message final vide."]
    if type_item == "reasoning":
        if texte:
            return [f"IA raisonnement: {ligne_texte}" for ligne_texte in texte.splitlines() if ligne_texte.strip()]
        return []
    if type_item in {"tool_call", "tool_result"}:
        nom_outil = str(item.get("tool_name", item.get("name", type_item)))
        if texte:
            return [f"IA outil {nom_outil}: {ligne_texte}" for ligne_texte in texte.splitlines() if ligne_texte.strip()]
        return [f"IA outil {nom_outil}."]
    return []

def ecrire_json_formate(chemin_fichier: Path, contenu: Dict[str, object]) -> Path:
    """Ecrit un dictionnaire JSON formate dans un fichier.

    Args:
        chemin_fichier: Fichier cible.
        contenu: Dictionnaire a serialiser.

    Returns:
        Chemin du fichier ecrit.
    """

    with chemin_fichier.open("w", encoding="utf-8") as flux:
        json.dump(contenu, flux, indent=2, ensure_ascii=False)
        flux.write("\n")
    return chemin_fichier


def generer_corps_pr_migration(cible: Dict[str, object], etat_session: Dict[str, object]) -> str:
    """Construit le corps standardise d une Pull Request de migration.

    Args:
        cible: Cible selectionnee.
        etat_session: Etat de session courant.

    Returns:
        Corps de PR multi-ligne.
    """

    return "\n".join(
        [
            "## Resume",
            f"- Cible: {cible.get('titre', 'inconnue')}",
            f"- Version installee: {cible.get('version_installee', '(indisponible)')}",
            f"- Version candidate: {cible.get('version_candidate', '(indisponible)')}",
            f"- Brief IA: {etat_session.get('chemin_placeholder_md', '(indisponible)')}",
            f"- Reponse IA: {etat_session.get('chemin_reponse_ia', '(indisponible)')}",
            f"- Rapport qualite: {etat_session.get('chemin_rapport_qualite', '(indisponible)')}",
            "",
            "## Workflow",
            "- Migration appliquee via commande CLI.",
            "- Adaptation code/tests/docs/scripts realisee via Codex CLI + Ollama avec brief Markdown + JSON.",
            "- Suite qualite complete relancee et verte avant proposition de merge.",
            "",
            "## Validation",
            "- Validation locale `./scripts/tests/lancer_suite.sh` verte.",
            "- Validation `act` du workflow `qualite.yml` verte.",
            "- Validation `act` du workflow `verification_reelle.yml` verte.",
            "- Relecture humaine obligatoire avant merge.",
            "- Merge interdit sans accord explicite.",
        ]
    )


def creer_journaliseur(
    chemin_journal: Path,
    consommateur_journal: ConsommateurJournal | None,
) -> ConsommateurJournal:
    """Construit une fonction de journalisation commune.

    Args:
        chemin_journal: Chemin du fichier de journal cible.
        consommateur_journal: Callback optionnel pour diffusion temps reel.

    Returns:
        Fonction prenant une ligne de journal et la persistant.
    """

    chemin_journal.write_text("", encoding="utf-8")

    def journaliser(message: str) -> None:
        """Ecrit une ligne dans le journal et notifie l interface.

        Args:
            message: Message a tracer.

        Returns:
            Aucun.
        """

        ligne = preparer_ligne_journal(message)
        with chemin_journal.open("a", encoding="utf-8") as flux:
            flux.write(ligne + "\n")
        if consommateur_journal is not None:
            consommateur_journal(ligne)

    return journaliser


def executer_operation(
    operation_id: str,
    configuration: Dict[str, object],
    consommateur_journal: ConsommateurJournal | None = None,
    contexte_operation: Dict[str, object] | None = None,
) -> Tuple[bool, str, Path]:
    """Execute une operation de maintenance et journalise son resultat.

    Args:
        operation_id: Identifiant de l operation a executer.
        configuration: Configuration chargee du mode maintenance.
        consommateur_journal: Callback optionnel pour afficher les logs en direct.
        contexte_operation: Contexte optionnel associe a l operation.

    Returns:
        Un tuple (succes, message, chemin_journal).
    """

    racine_projet = obtenir_racine_projet()
    chemin_journal = DOSSIER_TEMPORAIRE_LOGS / "maintenance_mode_journal_indisponible.log"
    journaliser: ConsommateurJournal | None = None

    try:
        chemin_journal = preparer_fichier_journal(racine_projet, operation_id)
        journaliser = creer_journaliseur(chemin_journal, consommateur_journal)
        journaliser(f"Debut de l operation '{operation_id}'.")

        if operation_id == "diagnostic":
            succes, message, _ = operation_diagnostic(configuration, racine_projet, chemin_journal, journaliser)
        elif operation_id == "actualiser_cibles_migration":
            succes, message, _ = operation_actualiser_cibles_migration(
                configuration,
                racine_projet,
                chemin_journal,
                journaliser,
            )
        elif operation_id == "appliquer_migration_cible":
            succes, message, _ = operation_appliquer_migration_cible(
                configuration,
                racine_projet,
                chemin_journal,
                journaliser,
                contexte_operation,
            )
        elif operation_id == "preparer_placeholder_ia_migration":
            succes, message, _ = operation_preparer_placeholder_ia_migration(
                configuration,
                racine_projet,
                chemin_journal,
                journaliser,
                contexte_operation,
            )
        elif operation_id == "relancer_qualite_complete":
            succes, message, _ = operation_relancer_qualite_complete(
                configuration,
                racine_projet,
                chemin_journal,
                journaliser,
                contexte_operation,
            )
        elif operation_id == "proposer_pr_migration":
            succes, message, _ = operation_proposer_pr_migration(
                configuration,
                racine_projet,
                chemin_journal,
                journaliser,
                contexte_operation,
            )
        elif operation_id == "git_pull":
            succes, message, _ = operation_git_pull(configuration, racine_projet, chemin_journal, journaliser)
        elif operation_id == "git_retour_precedent":
            succes, message, _ = operation_git_retour_precedent(
                configuration,
                racine_projet,
                chemin_journal,
                journaliser,
            )
        elif operation_id == "pipeline_post_pull":
            succes, message, _ = operation_pipeline_post_pull(
                configuration,
                racine_projet,
                chemin_journal,
                journaliser,
            )
        elif operation_id == "mise_a_jour_os":
            succes, message, _ = operation_mise_a_jour_os(configuration, racine_projet, chemin_journal, journaliser)
        elif operation_id == "reset_pre_requis":
            succes, message, _ = operation_reset_pre_requis(configuration, racine_projet, chemin_journal, journaliser)
        else:
            message = (
                f"Operation inconnue: {operation_id}. "
                "Action recommandee: selectionnez une operation valide dans la liste."
            )
            journaliser(message)
            return False, message, chemin_journal

        etat_final = "SUCCES" if succes else "ECHEC"
        journaliser(f"Fin de l operation '{operation_id}' ({etat_final}).")
        return succes, message, chemin_journal
    except Exception as erreur:  # pylint: disable=broad-exception-caught
        message = (
            f"Operation interrompue par une erreur inattendue: {erreur}. "
            "Action recommandee: consulter le journal puis relancer l operation."
        )
        ligne = f"ERREUR: {message}"
        if journaliser is not None:
            journaliser(ligne)
        elif consommateur_journal is not None:
            consommateur_journal(preparer_ligne_journal(ligne))
        return False, message, chemin_journal


def preparer_fichier_journal(racine_projet: Path, operation_id: str) -> Path:
    """Prepare le fichier de journalisation d une operation.

    Args:
        racine_projet: Racine du depot.
        operation_id: Identifiant operation.

    Returns:
        Chemin complet du journal.
    """

    dossier_logs = selectionner_dossier_logs(racine_projet)
    horodatage = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return dossier_logs / f"maintenance_mode_{operation_id}_{horodatage}.log"


def extraire_timeout(configuration: Dict[str, object], operation_id: str) -> int:
    """Retourne le timeout configure pour une operation.

    Args:
        configuration: Configuration chargee.
        operation_id: Identifiant de l operation.

    Returns:
        Timeout en secondes.
    """

    section_timeouts = configuration.get("temps_max_secondes", {})
    if not isinstance(section_timeouts, dict):
        return TIMEOUT_PAR_DEFAUT
    valeur = section_timeouts.get(operation_id, TIMEOUT_PAR_DEFAUT)
    try:
        return int(valeur)
    except (TypeError, ValueError):
        return TIMEOUT_PAR_DEFAUT


def extraire_intervalle_lecture(configuration: Dict[str, object]) -> float:
    """Retourne l intervalle de lecture du flux processus.

    Args:
        configuration: Configuration chargee.

    Returns:
        Intervalle en secondes pour la lecture non bloquante.
    """

    section_journal = configuration.get("journal", {})
    if not isinstance(section_journal, dict):
        return INTERVALLE_LECTURE_PAR_DEFAUT_MS / 1000.0

    valeur = section_journal.get("intervalle_lecture_processus_ms", INTERVALLE_LECTURE_PAR_DEFAUT_MS)
    try:
        millisecondes = int(valeur)
    except (TypeError, ValueError):
        millisecondes = INTERVALLE_LECTURE_PAR_DEFAUT_MS

    millisecondes = max(10, millisecondes)
    return millisecondes / 1000.0


def operation_diagnostic(
    configuration: Dict[str, object],
    racine_projet: Path,
    chemin_journal: Path,
    journaliser: ConsommateurJournal,
) -> Tuple[bool, str, Path]:
    """Execute un diagnostic rapide du systeme.

    Args:
        configuration: Configuration chargee.
        racine_projet: Racine du depot.
        chemin_journal: Journal cible.
        journaliser: Fonction de trace et diffusion en direct.

    Returns:
        Resultat (succes, message, chemin journal).
    """

    _ = chemin_journal
    commandes = [
        ["uname", "-a"],
        ["python3", "--version"],
        ["java", "-version"],
        ["free", "-h"],
        ["df", "-h", str(racine_projet)],
    ]

    succes_global = diagnostiquer_pre_requis_borne(journaliser)
    intervalle_lecture = extraire_intervalle_lecture(configuration)
    journaliser("=== Diagnostic maintenance ===")

    for commande in commandes:
        if shutil.which(commande[0]) is None:
            succes_global = False
            journaliser(
                "ATTENTION: commande diagnostique indisponible: "
                f"{commande[0]}. Action recommandee: relancez sudo ./bootstrap_borne.sh."
            )
            continue
        journaliser(f"$ {' '.join(commande)}")
        succes, sortie = executer_commande(
            commande,
            racine_projet,
            timeout_secondes=TIMEOUT_DIAGNOSTIC_SECONDES,
            consommateur_sortie=journaliser,
            intervalle_lecture_secondes=intervalle_lecture,
        )
        if not succes:
            succes_global = False
            journaliser(f"ERREUR: {extraire_premiere_ligne_sortie(sortie)}")

    if succes_global:
        return True, "Diagnostic termine avec succes.", chemin_journal
    return False, "Diagnostic termine avec erreurs (voir journal).", chemin_journal


def verifier_git_disponible(journaliser: ConsommateurJournal) -> bool:
    """Verifie la disponibilite de git avant operation.

    Args:
        journaliser: Fonction de trace et diffusion en direct.

    Returns:
        True si git est disponible, sinon False.
    """

    if shutil.which("git") is not None:
        return True

    journaliser(
        "ERREUR: git est introuvable sur ce systeme. "
        "Action recommandee: relancez sudo ./bootstrap_borne.sh pour installer les pre-requis."
    )
    return False


def operation_git_pull(
    configuration: Dict[str, object],
    racine_projet: Path,
    chemin_journal: Path,
    journaliser: ConsommateurJournal,
) -> Tuple[bool, str, Path]:
    """Execute un git pull fast-forward sur le depot.

    Args:
        configuration: Configuration chargee.
        racine_projet: Racine du depot.
        chemin_journal: Journal cible.
        journaliser: Fonction de trace et diffusion en direct.

    Returns:
        Resultat (succes, message, chemin journal).
    """

    if not verifier_git_disponible(journaliser):
        return (
            False,
            "Git pull impossible: git introuvable. Relancez sudo ./bootstrap_borne.sh.",
            chemin_journal,
        )

    timeout_secondes = extraire_timeout(configuration, "git_pull")
    intervalle_lecture = extraire_intervalle_lecture(configuration)
    commande = ["git", "-C", str(racine_projet), "pull", "--ff-only"]

    journaliser(f"$ {' '.join(commande)}")
    succes, sortie = executer_commande(
        commande,
        racine_projet,
        timeout_secondes=timeout_secondes,
        consommateur_sortie=journaliser,
        intervalle_lecture_secondes=intervalle_lecture,
    )

    if succes:
        return True, "Git pull termine.", chemin_journal

    journaliser(f"ERREUR: {extraire_premiere_ligne_sortie(sortie)}")
    return False, "Echec git pull. Verifiez les conflits et la connexion.", chemin_journal


def operation_git_retour_precedent(
    configuration: Dict[str, object],
    racine_projet: Path,
    chemin_journal: Path,
    journaliser: ConsommateurJournal,
) -> Tuple[bool, str, Path]:
    """Revient au commit precedent si le depot est propre.

    Args:
        configuration: Configuration chargee.
        racine_projet: Racine du depot.
        chemin_journal: Journal cible.
        journaliser: Fonction de trace et diffusion en direct.

    Returns:
        Resultat (succes, message, chemin journal).
    """

    if not verifier_git_disponible(journaliser):
        return (
            False,
            "Retour commit precedent impossible: git introuvable. Relancez sudo ./bootstrap_borne.sh.",
            chemin_journal,
        )

    timeout_secondes = extraire_timeout(configuration, "git_retour_precedent")
    intervalle_lecture = extraire_intervalle_lecture(configuration)

    controles = [
        ["git", "-C", str(racine_projet), "rev-parse", "--is-inside-work-tree"],
        ["git", "-C", str(racine_projet), "rev-parse", "--verify", "HEAD~1"],
    ]
    for commande in controles:
        journaliser(f"$ {' '.join(commande)}")
        succes, sortie = executer_commande(
            commande,
            racine_projet,
            timeout_secondes=timeout_secondes,
            consommateur_sortie=journaliser,
            intervalle_lecture_secondes=intervalle_lecture,
        )
        if not succes:
            journaliser(f"ERREUR: {extraire_premiere_ligne_sortie(sortie)}")
            return (
                False,
                "Retour commit precedent impossible: depot git invalide ou historique insuffisant.",
                chemin_journal,
            )

    commande_statut = ["git", "-C", str(racine_projet), "status", "--porcelain"]
    journaliser(f"$ {' '.join(commande_statut)}")
    resultat_statut = subprocess.run(
        commande_statut,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding=obtenir_encodage_processus(),
        errors="replace",
        check=False,
    )
    sortie_statut = (resultat_statut.stdout or "").strip()
    if resultat_statut.returncode != 0:
        journaliser(f"ERREUR: {extraire_premiere_ligne_sortie(resultat_statut.stdout or '')}")
        return (
            False,
            "Retour commit precedent impossible: echec lecture statut git.",
            chemin_journal,
        )

    if sortie_statut:
        journaliser("ERREUR: Depot non propre detecte par git status --porcelain.")
        return (
            False,
            "Retour commit precedent refuse: modifications locales detectees. "
            "Action recommandee: commit/stash des changements puis relancez.",
            chemin_journal,
        )

    commande_reset = ["git", "-C", str(racine_projet), "reset", "--hard", "HEAD~1"]
    journaliser(f"$ {' '.join(commande_reset)}")
    succes, sortie = executer_commande(
        commande_reset,
        racine_projet,
        timeout_secondes=timeout_secondes,
        consommateur_sortie=journaliser,
        intervalle_lecture_secondes=intervalle_lecture,
    )
    if not succes:
        journaliser(f"ERREUR: {extraire_premiere_ligne_sortie(sortie)}")
        return False, "Retour commit precedent en echec (voir journal).", chemin_journal

    return True, "Retour commit precedent termine.", chemin_journal


def operation_pipeline_post_pull(
    configuration: Dict[str, object],
    racine_projet: Path,
    chemin_journal: Path,
    journaliser: ConsommateurJournal,
) -> Tuple[bool, str, Path]:
    """Execute le pipeline post-pull versionne du projet.

    Args:
        configuration: Configuration chargee.
        racine_projet: Racine du depot.
        chemin_journal: Journal cible.
        journaliser: Fonction de trace et diffusion en direct.

    Returns:
        Resultat (succes, message, chemin journal).
    """

    timeout_secondes = extraire_timeout(configuration, "pipeline_post_pull")
    intervalle_lecture = extraire_intervalle_lecture(configuration)
    script_pipeline = racine_projet / "scripts" / "deploiement" / "post_pull_update.sh"
    commande = [str(script_pipeline)]

    journaliser(f"$ {' '.join(commande)}")
    succes, sortie = executer_commande(
        commande,
        racine_projet,
        timeout_secondes=timeout_secondes,
        consommateur_sortie=journaliser,
        intervalle_lecture_secondes=intervalle_lecture,
    )

    if succes:
        return True, "Pipeline post-pull termine.", chemin_journal

    journaliser(f"ERREUR: {extraire_premiere_ligne_sortie(sortie)}")
    return False, "Pipeline post-pull en erreur. Consultez le journal.", chemin_journal


def operation_mise_a_jour_os(
    configuration: Dict[str, object],
    racine_projet: Path,
    chemin_journal: Path,
    journaliser: ConsommateurJournal,
) -> Tuple[bool, str, Path]:
    """Execute la mise a jour systeme via apt.

    Args:
        configuration: Configuration chargee.
        racine_projet: Racine du depot.
        chemin_journal: Journal cible.
        journaliser: Fonction de trace et diffusion en direct.

    Returns:
        Resultat (succes, message, chemin journal).
    """

    timeout_secondes = extraire_timeout(configuration, "mise_a_jour_os")
    intervalle_lecture = extraire_intervalle_lecture(configuration)
    prefixe_sudo = obtenir_prefixe_privileges_systeme()
    if prefixe_sudo is None:
        message = (
            "Mise a jour OS impossible: sudo non disponible en mode non interactif. "
            "Action recommandee: lancer la borne avec sudo ou executer la mise a jour depuis un terminal admin."
        )
        journaliser(f"ERREUR: {message}")
        return False, message, chemin_journal

    commandes = [
        prefixe_sudo + ["apt-get", "update"],
        prefixe_sudo + ["apt-get", "full-upgrade", "-y"],
    ]

    for commande in commandes:
        journaliser(f"$ {' '.join(commande)}")
        succes, sortie = executer_commande(
            commande,
            racine_projet,
            timeout_secondes=timeout_secondes,
            consommateur_sortie=journaliser,
            intervalle_lecture_secondes=intervalle_lecture,
        )
        if not succes:
            journaliser(f"ERREUR: {extraire_premiere_ligne_sortie(sortie)}")
            return False, "Echec de la mise a jour OS (voir journal).", chemin_journal

    return True, "Mise a jour OS terminee.", chemin_journal


def nettoyer_artefacts_reset(racine_projet: Path, journaliser: ConsommateurJournal) -> Tuple[bool, str]:
    """Nettoie les artefacts locaux pour retester une installation a zero.

    Args:
        racine_projet: Racine du depot.
        journaliser: Fonction de trace vers le journal operation.

    Returns:
        Tuple (succes, message) pour cette phase locale.
    """

    for repertoire_relatif in REPERTOIRES_RESET_RELATIFS:
        repertoire_cible = racine_projet / repertoire_relatif
        if not repertoire_cible.exists():
            continue
        try:
            shutil.rmtree(repertoire_cible)
            journaliser(f"Artefact supprime: {repertoire_cible}")
        except OSError as erreur:
            message = (
                f"Impossible de supprimer {repertoire_cible}: {erreur}. "
                "Action recommandee: corriger les permissions puis relancer le reset."
            )
            journaliser(f"ERREUR: {message}")
            return False, message

    for fichier_relatif in FICHIERS_RESET_RELATIFS:
        fichier_cible = racine_projet / fichier_relatif
        if not fichier_cible.exists():
            continue
        try:
            fichier_cible.unlink()
            journaliser(f"Fichier supprime: {fichier_cible}")
        except OSError as erreur:
            message = (
                f"Impossible de supprimer {fichier_cible}: {erreur}. "
                "Action recommandee: corriger les permissions puis relancer le reset."
            )
            journaliser(f"ERREUR: {message}")
            return False, message

    return True, "Nettoyage local termine."


def lister_paquets_reset_non_systeme_installes() -> List[str]:
    """Liste les paquets non-systeme effectivement installes et purgables en mode sur.

    Args:
        Aucun.

    Returns:
        Liste ordonnee des paquets installes ciblables par le reset sur.
    """

    paquets_proteges = set(PAQUETS_RESET_SYSTEME_PROTEGES_BORNE)
    paquets_installes: List[str] = []
    for paquet in PAQUETS_RESET_NON_SYSTEME_BORNE:
        if paquet in paquets_proteges:
            continue
        if paquet_systeme_installe(paquet):
            paquets_installes.append(paquet)
    return paquets_installes


def operation_reset_pre_requis(
    configuration: Dict[str, object],
    racine_projet: Path,
    chemin_journal: Path,
    journaliser: ConsommateurJournal,
) -> Tuple[bool, str, Path]:
    """Purge en mode sur les prerequis non-systeme puis nettoie les artefacts locaux.

    Args:
        configuration: Configuration chargee.
        racine_projet: Racine du depot.
        chemin_journal: Journal cible.
        journaliser: Fonction de trace et diffusion en direct.

    Returns:
        Resultat (succes, message, chemin journal).
    """

    timeout_secondes = extraire_timeout(configuration, "reset_pre_requis")
    intervalle_lecture = extraire_intervalle_lecture(configuration)
    prefixe_sudo = obtenir_prefixe_privileges_systeme()
    if prefixe_sudo is None:
        message = (
            "Reset prerequis impossible: sudo non disponible en mode non interactif. "
            "Action recommandee: lancer la borne avec sudo ou executer le reset depuis un terminal admin."
        )
        journaliser(f"ERREUR: {message}")
        return False, message, chemin_journal

    paquets_non_systeme_installes = lister_paquets_reset_non_systeme_installes()
    if paquets_non_systeme_installes:
        journaliser(
            "Mode sur: purge uniquement des prerequis non-systeme installes: "
            + ", ".join(paquets_non_systeme_installes)
        )
    else:
        journaliser("Mode sur: aucun prerequis non-systeme installe a purger.")

    journaliser(
        "Paquets systeme proteges (non purges): "
        + ", ".join(PAQUETS_RESET_SYSTEME_PROTEGES_BORNE)
    )

    commandes = []
    if paquets_non_systeme_installes:
        commandes.append(prefixe_sudo + ["apt-get", "remove", "--purge", "-y"] + paquets_non_systeme_installes)
    commandes.append(prefixe_sudo + ["apt-get", "clean"])

    for commande in commandes:
        journaliser(f"$ {' '.join(commande)}")
        succes, sortie = executer_commande(
            commande,
            racine_projet,
            timeout_secondes=timeout_secondes,
            consommateur_sortie=journaliser,
            intervalle_lecture_secondes=intervalle_lecture,
        )
        if not succes:
            journaliser(f"ERREUR: {extraire_premiere_ligne_sortie(sortie)}")
            return False, "Echec reset prerequis systeme (voir journal).", chemin_journal

    succes_nettoyage, message_nettoyage = nettoyer_artefacts_reset(racine_projet, journaliser)
    if not succes_nettoyage:
        return False, message_nettoyage, chemin_journal

    journaliser(message_nettoyage)
    return (
        True,
        "Reset prerequis termine en mode sur. Relancez bootstrap_borne.sh pour reinstaller.",
        chemin_journal,
    )


def obtenir_cible_migration_contextualisee(
    contexte_operation: Dict[str, object] | None,
    racine_projet: Path,
) -> Tuple[Dict[str, object] | None, List[Dict[str, object]]]:
    """Retourne la cible de migration issue du contexte courant.

    Args:
        contexte_operation: Contexte optionnel fourni par l interface.
        racine_projet: Racine du depot.

    Returns:
        Tuple (cible selectionnee ou None, catalogue des cibles).
    """

    cibles = collecter_cibles_migration(racine_projet)
    identifiant = extraire_identifiant_cible_migration(contexte_operation)
    return selectionner_cible_migration(cibles, identifiant), cibles


def operation_actualiser_cibles_migration(
    configuration: Dict[str, object],
    racine_projet: Path,
    chemin_journal: Path,
    journaliser: ConsommateurJournal,
) -> Tuple[bool, str, Path]:
    """Recharge et journalise les versions installees/candidates des cibles.

    Args:
        configuration: Configuration chargee.
        racine_projet: Racine du depot.
        chemin_journal: Journal cible.
        journaliser: Fonction de trace et diffusion.

    Returns:
        Resultat (succes, message, chemin journal).
    """

    _ = configuration
    _ = chemin_journal
    cibles = collecter_cibles_migration(racine_projet)
    if not cibles:
        return (
            False,
            "Aucune cible de migration configuree. Verifiez config/cibles_migration.json.",
            chemin_journal,
        )

    journaliser("=== Cibles de migration detectees ===")
    for cible in cibles:
        if cible.get("supportee_sur_hote"):
            etat = "MIGRATION DISPONIBLE" if cible.get("migration_disponible") else "A JOUR"
        else:
            etat = f"INDISPONIBLE ({cible.get('raison_indisponibilite')})"
        journaliser(
            f"{cible.get('titre')}: installee={cible.get('version_installee')} | "
            f"candidate={cible.get('version_candidate')} | etat={etat}"
        )

    return True, f"{len(cibles)} cible(s) de migration rechargee(s).", chemin_journal


def operation_appliquer_migration_cible(
    configuration: Dict[str, object],
    racine_projet: Path,
    chemin_journal: Path,
    journaliser: ConsommateurJournal,
    contexte_operation: Dict[str, object] | None,
) -> Tuple[bool, str, Path]:
    """Applique la migration systeme correspondant a la cible selectionnee.

    Args:
        configuration: Configuration chargee.
        racine_projet: Racine du depot.
        chemin_journal: Journal cible.
        journaliser: Fonction de trace et diffusion.
        contexte_operation: Contexte incluant la cible choisie.

    Returns:
        Resultat (succes, message, chemin journal).
    """

    cible, _ = obtenir_cible_migration_contextualisee(contexte_operation, racine_projet)
    if cible is None:
        message = (
            "Aucune cible de migration selectionnee. "
            "Action recommandee: choisissez une cible dans la combobox puis relancez."
        )
        journaliser(f"ERREUR: {message}")
        return False, message, chemin_journal

    if not cible.get("supportee_sur_hote"):
        message = str(cible.get("raison_indisponibilite") or MESSAGE_HOTE_APT_NON_SUPPORTE)
        journaliser(f"ERREUR: {message}")
        return False, message, chemin_journal

    if not cible.get("migration_disponible"):
        message = (
            f"Aucune migration candidate detectee pour {cible.get('titre')}. "
            "Action recommandee: rechargez les cibles ou choisissez une autre cible."
        )
        journaliser(f"ERREUR: {message}")
        return False, message, chemin_journal

    prefixe_sudo = obtenir_prefixe_privileges_systeme()
    if prefixe_sudo is None:
        message = (
            "Migration impossible: sudo non disponible en mode non interactif. "
            "Action recommandee: lancer la borne avec sudo ou executer la migration depuis un terminal admin."
        )
        journaliser(f"ERREUR: {message}")
        return False, message, chemin_journal

    timeout_secondes = extraire_timeout(configuration, "appliquer_migration_cible")
    intervalle_lecture = extraire_intervalle_lecture(configuration)
    commandes = cible.get("commandes_migration", [])
    if not isinstance(commandes, list) or not commandes:
        message = (
            f"Aucune commande de migration configuree pour {cible.get('titre')}. "
            "Action recommandee: completez config/cibles_migration.json."
        )
        journaliser(f"ERREUR: {message}")
        return False, message, chemin_journal

    journaliser(
        f"Cible retenue: {cible.get('titre')} | installee={cible.get('version_installee')} | "
        f"candidate={cible.get('version_candidate')}"
    )
    for commande in commandes:
        if not isinstance(commande, list) or not commande:
            continue
        commande_complete = prefixe_sudo + [str(argument) for argument in commande]
        journaliser(f"$ {' '.join(commande_complete)}")
        succes, sortie = executer_commande(
            commande_complete,
            racine_projet,
            timeout_secondes=timeout_secondes,
            consommateur_sortie=journaliser,
            intervalle_lecture_secondes=intervalle_lecture,
        )
        if not succes:
            journaliser(f"ERREUR: {extraire_premiere_ligne_sortie(sortie)}")
            return (
                False,
                f"Echec de migration pour {cible.get('titre')} (voir journal).",
                chemin_journal,
            )

    effacer_etat_migration_obsolete(racine_projet)
    etat_session = construire_etat_session_migration(cible, racine_projet, migration_appliquee=True)
    chemin_etat = enregistrer_etat_migration(racine_projet, etat_session)
    journaliser(f"Session migration enregistree: {chemin_etat}")
    return (
        True,
        f"Migration appliquee pour {cible.get('titre')}. Session: {chemin_etat}",
        chemin_journal,
    )


def operation_preparer_placeholder_ia_migration(
    configuration: Dict[str, object],
    racine_projet: Path,
    chemin_journal: Path,
    journaliser: ConsommateurJournal,
    contexte_operation: Dict[str, object] | None,
) -> Tuple[bool, str, Path]:
    """Prepare le brief IA puis lance Codex/Ollama pour la migration.

    Args:
        configuration: Configuration chargee.
        racine_projet: Racine du depot.
        chemin_journal: Journal cible.
        journaliser: Fonction de trace et diffusion.
        contexte_operation: Contexte incluant la cible choisie.

    Returns:
        Resultat (succes, message, chemin journal).
    """

    cible, _ = obtenir_cible_migration_contextualisee(contexte_operation, racine_projet)
    if cible is None:
        message = (
            "Assistant IA impossible: aucune cible de migration selectionnee. "
            "Action recommandee: choisissez une cible dans la combobox."
        )
        journaliser(f"ERREUR: {message}")
        return False, message, chemin_journal

    etat_valide, message_etat, etat_session = verifier_etat_migration_pour_cible(
        racine_projet,
        cible,
        exiger_migration=True,
    )
    if not etat_valide:
        journaliser(f"ERREUR: {message_etat}")
        return False, message_etat, chemin_journal

    configuration_assistant = charger_configuration_assistant_ia()
    dossier_sortie = determiner_dossier_sortie_artefacts(racine_projet, contexte_operation)
    horodatage = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    chemins_artefacts = {
        "brief_markdown": dossier_sortie / f"brief_ia_migration_{cible.get('id')}_{horodatage}.md",
        "brief_json": dossier_sortie / f"brief_ia_migration_{cible.get('id')}_{horodatage}.json",
        "reponse_ia_markdown": dossier_sortie / f"reponse_ia_migration_{cible.get('id')}_{horodatage}.md",
        "transcription_ia_jsonl": dossier_sortie / f"transcription_ia_migration_{cible.get('id')}_{horodatage}.jsonl",
    }
    contenu_markdown = construire_contenu_brief_ia_markdown(
        cible,
        etat_session,
        configuration_assistant,
        racine_projet,
        chemins_artefacts,
    )
    contenu_json = construire_payload_contexte_ia_migration(
        cible,
        etat_session,
        configuration_assistant,
        racine_projet,
        chemins_artefacts,
    )
    modele_prompt = charger_modele_prompt_assistant_ia(racine_projet, configuration_assistant)
    prompt = construire_prompt_assistant_ia_migration(
        modele_prompt,
        cible,
        etat_session,
        configuration_assistant,
        racine_projet,
        chemins_artefacts,
    )

    chemins_artefacts["brief_markdown"].write_text(contenu_markdown + "\n", encoding="utf-8")
    ecrire_json_formate(chemins_artefacts["brief_json"], contenu_json)
    journaliser(f"Brief IA Markdown genere: {chemins_artefacts['brief_markdown']}")
    journaliser(f"Brief IA JSON genere: {chemins_artefacts['brief_json']}")

    outils_valides, message_outils = verifier_outils_assistant_ia(configuration_assistant)
    if not outils_valides:
        mettre_a_jour_etat_session_migration(
            racine_projet,
            {
                "placeholder_ia_genere": False,
                "chemin_placeholder_md": str(chemins_artefacts["brief_markdown"]),
                "chemin_placeholder_json": str(chemins_artefacts["brief_json"]),
                "chemin_reponse_ia": "",
                "chemin_transcription_ia_jsonl": "",
                "qualite_verifiee": False,
                "chemin_rapport_qualite": "",
            },
        )
        journaliser(f"ERREUR: {message_outils}")
        return False, message_outils, chemin_journal

    timeout_secondes = extraire_timeout(configuration, "preparer_placeholder_ia_migration")
    intervalle_lecture = extraire_intervalle_lecture(configuration)
    commande = construire_commande_codex_migration(
        configuration_assistant,
        racine_projet,
        chemins_artefacts["reponse_ia_markdown"],
    )
    environnement_codex = construire_environnement_codex_migration(configuration_assistant)
    lignes_brutes: List[str] = []
    etat_evenements: Dict[str, object] = {"dernier_message_agent": "", "usage": {}}

    def consommer_sortie_codex(ligne: str) -> None:
        """Convertit le flux JSONL Codex en lignes lisibles pour le journal.

        Args:
            ligne: Ligne brute provenant de la CLI Codex.

        Returns:
            Aucun.
        """

        lignes_brutes.append(ligne)
        for ligne_formatee in formater_lignes_evenement_codex(ligne, etat_evenements):
            journaliser(ligne_formatee)

    journaliser("Lancement assistant IA: " + " ".join(argument for argument in commande[:-1]) + " < prompt stdin")
    if environnement_codex.get("CODEX_OSS_BASE_URL"):
        journaliser(f"Assistant IA: serveur Ollama distant configure via CODEX_OSS_BASE_URL={environnement_codex['CODEX_OSS_BASE_URL']}")
    succes_codex, sortie_codex = executer_commande(
        commande,
        racine_projet,
        timeout_secondes=timeout_secondes,
        consommateur_sortie=consommer_sortie_codex,
        intervalle_lecture_secondes=intervalle_lecture,
        entree_texte=prompt,
        variables_environnement=environnement_codex,
    )
    chemins_artefacts["transcription_ia_jsonl"].write_text(
        "\n".join(lignes_brutes) + ("\n" if lignes_brutes else ""),
        encoding="utf-8",
    )

    dernier_message_agent = str(etat_evenements.get("dernier_message_agent", "")).strip()
    reponse_presente = ecrire_reponse_ia_si_absente(chemins_artefacts["reponse_ia_markdown"], dernier_message_agent)
    succes_assistant = succes_codex and reponse_presente
    mettre_a_jour_etat_session_migration(
        racine_projet,
        {
            "placeholder_ia_genere": succes_assistant,
            "chemin_placeholder_md": str(chemins_artefacts["brief_markdown"]),
            "chemin_placeholder_json": str(chemins_artefacts["brief_json"]),
            "chemin_reponse_ia": (
                str(chemins_artefacts["reponse_ia_markdown"]) if reponse_presente else ""
            ),
            "chemin_transcription_ia_jsonl": str(chemins_artefacts["transcription_ia_jsonl"]),
            "qualite_verifiee": False,
            "chemin_rapport_qualite": "",
        },
    )
    journaliser(f"Trace IA JSONL ecrite: {chemins_artefacts['transcription_ia_jsonl']}")
    if reponse_presente:
        journaliser(f"Reponse IA ecrite: {chemins_artefacts['reponse_ia_markdown']}")

    if not succes_assistant:
        if succes_codex and not reponse_presente:
            message_echec = (
                "Assistant IA termine sans reponse finale exploitable. "
                "Action recommandee: verifier la trace JSONL puis relancer `preparer-ia`."
            )
        else:
            message_echec = (
                f"Echec assistant IA pour {cible.get('titre')}. "
                f"Details: {sortie_codex}"
            )
        journaliser(f"ERREUR: {message_echec}")
        return False, message_echec, chemin_journal

    return (
        True,
        f"Assistant IA termine pour {cible.get('titre')}."
        f" Brief: {chemins_artefacts['brief_markdown']}"
        f" | Reponse: {chemins_artefacts['reponse_ia_markdown']}"
        f" | Trace: {chemins_artefacts['transcription_ia_jsonl']}",
        chemin_journal,
    )


def trouver_commande_act() -> List[str] | None:
    """Retourne une commande `act` exploitable pour les workflows locaux.

    Args:
        Aucun.

    Returns:
        Prefixe de commande act, ou None si absent.
    """

    candidats = [
        Path.home() / ".local" / "bin" / "act",
        Path("/usr/local/bin/act"),
    ]
    for candidat in candidats:
        if candidat.exists():
            return [str(candidat)]

    commande_path = shutil.which("act")
    if commande_path:
        return [commande_path]
    return None


def creer_rapport_qualite_migration(
    racine_projet: Path,
    cible: Dict[str, object],
    etat_session: Dict[str, object],
    suite_locale_ok: bool,
    workflow_qualite_ok: bool,
    workflow_verification_reelle_ok: bool,
) -> Path:
    """Genere un rapport JSON structure pour la qualite de migration.

    Args:
        racine_projet: Racine du depot.
        cible: Cible de migration concernee.
        etat_session: Etat de session courant.
        suite_locale_ok: Statut de `lancer_suite.sh`.
        workflow_qualite_ok: Statut du workflow `qualite.yml`.
        workflow_verification_reelle_ok: Statut du workflow `verification_reelle.yml`.

    Returns:
        Chemin du rapport JSON genere.
    """

    dossier_logs = selectionner_dossier_logs(racine_projet)
    horodatage = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    chemin_rapport = dossier_logs / f"rapport_qualite_migration_{cible.get('id')}_{horodatage}.json"
    rapport = {
        "cible_id": cible.get("id"),
        "commit_git": etat_session.get("commit_git", "(indisponible)"),
        "branche_git": etat_session.get("branche_git", "(indisponible)"),
        "suite_locale_ok": suite_locale_ok,
        "workflow_qualite_ok": workflow_qualite_ok,
        "workflow_verification_reelle_ok": workflow_verification_reelle_ok,
        "succes_global": suite_locale_ok and workflow_qualite_ok and workflow_verification_reelle_ok,
        "horodatage": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    return ecrire_json_formate(chemin_rapport, rapport)


def operation_relancer_qualite_complete(
    configuration: Dict[str, object],
    racine_projet: Path,
    chemin_journal: Path,
    journaliser: ConsommateurJournal,
    contexte_operation: Dict[str, object] | None,
) -> Tuple[bool, str, Path]:
    """Relance la qualite complete du depot, y compris les workflows `act`.

    Args:
        configuration: Configuration chargee.
        racine_projet: Racine du depot.
        chemin_journal: Journal cible.
        journaliser: Fonction de trace et diffusion.
        contexte_operation: Contexte incluant la cible choisie.

    Returns:
        Resultat (succes, message, chemin journal).
    """

    cible, _ = obtenir_cible_migration_contextualisee(contexte_operation, racine_projet)
    if cible is None:
        message = (
            "Relance qualite complete impossible: aucune cible de migration selectionnee. "
            "Action recommandee: choisissez une cible dans la combobox ou via --cible."
        )
        journaliser(f"ERREUR: {message}")
        return False, message, chemin_journal

    etat_valide, message_etat, etat_session = verifier_etat_migration_pour_cible(
        racine_projet,
        cible,
        exiger_migration=True,
        exiger_assistant_ia=True,
        autoriser_commit_courant_different=True,
    )
    if not etat_valide:
        journaliser(f"ERREUR: {message_etat}")
        return False, message_etat, chemin_journal

    timeout_secondes = extraire_timeout(configuration, "relancer_qualite_complete")
    intervalle_lecture = extraire_intervalle_lecture(configuration)
    commande_act = trouver_commande_act()
    suite_locale_ok = False
    workflow_qualite_ok = False
    workflow_verification_reelle_ok = False

    if commande_act is None:
        message = (
            "Relance qualite complete impossible: act introuvable. "
            "Action recommandee: installez act puis relancez l operation."
        )
        chemin_rapport = creer_rapport_qualite_migration(
            racine_projet,
            cible,
            etat_session,
            suite_locale_ok,
            workflow_qualite_ok,
            workflow_verification_reelle_ok,
        )
        mettre_a_jour_etat_session_migration(
            racine_projet,
            {
                "qualite_verifiee": False,
                "chemin_rapport_qualite": str(chemin_rapport),
            },
        )
        journaliser(f"ERREUR: {message}")
        journaliser(f"Rapport qualite ecrit: {chemin_rapport}")
        return False, message, chemin_journal

    commandes = [
        ("suite_locale_ok", [str(racine_projet / "scripts" / "tests" / "lancer_suite.sh")]),
        (
            "workflow_qualite_ok",
            commande_act
            + [
                "-W",
                ".github/workflows/qualite.yml",
                "-j",
                "verification",
                "--container-architecture",
                "linux/amd64",
                "-P",
                "ubuntu-latest=catthehacker/ubuntu:act-latest",
            ],
        ),
        (
            "workflow_verification_reelle_ok",
            commande_act
            + [
                "-W",
                ".github/workflows/verification_reelle.yml",
                "-j",
                "verification_reelle_debian11",
                "--container-architecture",
                "linux/amd64",
                "-P",
                "ubuntu-latest=catthehacker/ubuntu:act-latest",
            ],
        ),
    ]

    for identifiant_commande, commande in commandes:
        journaliser(f"$ {' '.join(commande)}")
        succes, sortie = executer_commande(
            commande,
            racine_projet,
            timeout_secondes=timeout_secondes,
            consommateur_sortie=journaliser,
            intervalle_lecture_secondes=intervalle_lecture,
        )
        if identifiant_commande == "suite_locale_ok":
            suite_locale_ok = succes
        elif identifiant_commande == "workflow_qualite_ok":
            workflow_qualite_ok = succes
        elif identifiant_commande == "workflow_verification_reelle_ok":
            workflow_verification_reelle_ok = succes

        if not succes:
            chemin_rapport = creer_rapport_qualite_migration(
                racine_projet,
                cible,
                etat_session,
                suite_locale_ok,
                workflow_qualite_ok,
                workflow_verification_reelle_ok,
            )
            mettre_a_jour_etat_session_migration(
                racine_projet,
                {
                    "qualite_verifiee": False,
                    "chemin_rapport_qualite": str(chemin_rapport),
                },
            )
            journaliser(f"ERREUR: {extraire_premiere_ligne_sortie(sortie)}")
            journaliser(f"Rapport qualite ecrit: {chemin_rapport}")
            return False, "Relance qualite complete en echec (voir journal).", chemin_journal

    chemin_rapport = creer_rapport_qualite_migration(
        racine_projet,
        cible,
        etat_session,
        suite_locale_ok,
        workflow_qualite_ok,
        workflow_verification_reelle_ok,
    )
    mettre_a_jour_etat_session_migration(
        racine_projet,
        {
            "qualite_verifiee": True,
            "chemin_rapport_qualite": str(chemin_rapport),
        },
    )
    journaliser(f"Rapport qualite ecrit: {chemin_rapport}")
    return (
        True,
        f"Relance qualite complete terminee pour {cible.get('titre')}. Rapport: {chemin_rapport}",
        chemin_journal,
    )


def operation_proposer_pr_migration(
    configuration: Dict[str, object],
    racine_projet: Path,
    chemin_journal: Path,
    journaliser: ConsommateurJournal,
    contexte_operation: Dict[str, object] | None,
) -> Tuple[bool, str, Path]:
    """Pousse la branche courante et propose une Pull Request via `gh`.

    Args:
        configuration: Configuration chargee.
        racine_projet: Racine du depot.
        chemin_journal: Journal cible.
        journaliser: Fonction de trace et diffusion.
        contexte_operation: Contexte incluant la cible choisie.

    Returns:
        Resultat (succes, message, chemin journal).
    """

    cible, _ = obtenir_cible_migration_contextualisee(contexte_operation, racine_projet)
    if cible is None:
        message = (
            "Proposition de PR impossible: aucune cible de migration selectionnee. "
            "Action recommandee: choisissez une cible dans la combobox."
        )
        journaliser(f"ERREUR: {message}")
        return False, message, chemin_journal

    etat_valide, message_etat, etat_session = verifier_etat_migration_pour_cible(
        racine_projet,
        cible,
        exiger_migration=True,
        exiger_assistant_ia=True,
        exiger_qualite=True,
    )
    if not etat_valide:
        journaliser(f"ERREUR: {message_etat}")
        return False, message_etat, chemin_journal

    if not verifier_git_disponible(journaliser):
        return (
            False,
            "Proposition de PR impossible: git introuvable. Relancez sudo ./bootstrap_borne.sh.",
            chemin_journal,
        )

    if shutil.which("gh") is None:
        message = (
            "Proposition de PR impossible: gh introuvable. "
            "Action recommandee: installez GitHub CLI puis relancez l operation."
        )
        journaliser(f"ERREUR: {message}")
        return False, message, chemin_journal

    chemin_rapport = Path(str(etat_session.get("chemin_rapport_qualite", "")))
    if not chemin_rapport.exists():
        message = (
            "Proposition de PR impossible: rapport qualite introuvable. "
            "Action recommandee: relancez l operation de qualite."
        )
        journaliser(f"ERREUR: {message}")
        return False, message, chemin_journal

    timeout_secondes = extraire_timeout(configuration, "proposer_pr_migration")
    intervalle_lecture = extraire_intervalle_lecture(configuration)

    succes_branche, sortie_branche = executer_commande_capture(
        ["git", "-C", str(racine_projet), "rev-parse", "--abbrev-ref", "HEAD"],
        racine_projet,
    )
    branche_courante = extraire_premiere_ligne_non_vide(sortie_branche)
    if not succes_branche or branche_courante in {"HEAD", "main", "master"}:
        branche_recommandee = construire_nom_branche_migration(cible)
        message = (
            "Proposition de PR refusee depuis HEAD/main/master. "
            f"Action recommandee: git switch -c {branche_recommandee} puis committez les changements."
        )
        journaliser(f"ERREUR: {message}")
        return False, message, chemin_journal

    branche_session = str(etat_session.get("branche_git", "(indisponible)"))
    if branche_session not in {"", "(indisponible)"} and branche_courante != branche_session:
        message = (
            "Proposition de PR impossible: la branche courante ne correspond plus a la session de migration. "
            "Action recommandee: relancez la qualite depuis la branche actuelle."
        )
        journaliser(f"ERREUR: {message}")
        return False, message, chemin_journal

    succes_statut, sortie_statut = executer_commande_capture(
        ["git", "-C", str(racine_projet), "status", "--porcelain"],
        racine_projet,
    )
    if not succes_statut:
        message = "Proposition de PR impossible: echec lecture statut git."
        journaliser(f"ERREUR: {message}")
        return False, message, chemin_journal

    if sortie_statut.strip():
        message = (
            "Proposition de PR refusee: depot non propre. "
            "Action recommandee: committez ou stash les changements avant d ouvrir la PR."
        )
        journaliser(f"ERREUR: {message}")
        return False, message, chemin_journal

    titre_pr = generer_titre_pr_migration(cible)
    corps_pr = generer_corps_pr_migration(cible, etat_session)
    commandes = [
        ["git", "-C", str(racine_projet), "push", "-u", "origin", branche_courante],
        [
            "gh",
            "pr",
            "create",
            "--base",
            "main",
            "--head",
            branche_courante,
            "--title",
            titre_pr,
            "--body",
            corps_pr,
        ],
    ]

    for commande in commandes:
        journaliser(f"$ {' '.join(commande)}")
        succes, sortie = executer_commande(
            commande,
            racine_projet,
            timeout_secondes=timeout_secondes,
            consommateur_sortie=journaliser,
            intervalle_lecture_secondes=intervalle_lecture,
        )
        if not succes:
            journaliser(f"ERREUR: {extraire_premiere_ligne_sortie(sortie)}")
            return False, "Proposition de PR en echec (voir journal).", chemin_journal

    return (
        True,
        f"PR proposee pour {cible.get('titre')} depuis {branche_courante}.",
        chemin_journal,
    )


def obtenir_prefixe_privileges_systeme() -> List[str] | None:
    """Determine le prefixe de commande systeme privilegie.

    Args:
        Aucun.

    Returns:
        Une liste prefixe (`[]` en root, `['sudo', '-n']` sinon), ou None si impossible.
    """

    if hasattr(os, "geteuid") and os.geteuid() == 0:
        return []

    try:
        resultat = subprocess.run(
            ["sudo", "-n", "true"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding=obtenir_encodage_processus(),
            errors="replace",
            check=False,
        )
    except FileNotFoundError:
        return None

    if resultat.returncode == 0:
        return ["sudo", "-n"]
    return None


def diffuser_ligne(consommateur_sortie: ConsommateurJournal | None, ligne: str) -> None:
    """Diffuse une ligne de sortie vers le callback si present.

    Args:
        consommateur_sortie: Callback optionnel de diffusion.
        ligne: Ligne de sortie a transmettre.

    Returns:
        Aucun.
    """

    if consommateur_sortie is not None:
        consommateur_sortie(ligne)


def executer_commande(
    commande: List[str],
    repertoire_travail: Path,
    timeout_secondes: int,
    consommateur_sortie: ConsommateurJournal | None = None,
    intervalle_lecture_secondes: float = INTERVALLE_LECTURE_PAR_DEFAUT_MS / 1000.0,
    entree_texte: str | None = None,
    variables_environnement: Dict[str, str] | None = None,
) -> Tuple[bool, str]:
    """Execute une commande systeme et retourne sa sortie combinee.

    Args:
        commande: Liste des arguments de la commande.
        repertoire_travail: Repertoire de travail de la commande.
        timeout_secondes: Delai maximal en secondes.
        consommateur_sortie: Callback optionnel pour remonter les lignes en direct.
        intervalle_lecture_secondes: Intervalle de polling du flux processus.
        entree_texte: Texte optionnel a envoyer sur stdin.
        variables_environnement: Variables d environnement additionnelles.

    Returns:
        Un tuple (succes, sortie texte).
    """

    environnement_processus = os.environ.copy()
    if variables_environnement:
        environnement_processus.update(variables_environnement)

    try:
        processus = subprocess.Popen(
            commande,
            cwd=str(repertoire_travail),
            stdin=subprocess.PIPE if entree_texte is not None else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding=obtenir_encodage_processus(),
            errors="replace",
            bufsize=1,
            env=environnement_processus,
        )
    except FileNotFoundError:
        message = (
            f"Commande introuvable: {commande[0]}. "
            "Action recommandee: installez la commande manquante puis relancez l operation."
        )
        diffuser_ligne(consommateur_sortie, message)
        return False, message

    flux_sortie = processus.stdout
    if flux_sortie is None:
        processus.kill()
        message = (
            "Sortie standard indisponible pour la commande. "
            "Action recommandee: relancez la commande depuis un terminal pour diagnostic detaille."
        )
        diffuser_ligne(consommateur_sortie, message)
        return False, message

    if entree_texte is not None and processus.stdin is not None:
        try:
            processus.stdin.write(entree_texte)
            if not entree_texte.endswith("\n"):
                processus.stdin.write("\n")
            processus.stdin.flush()
        finally:
            processus.stdin.close()

    lignes_capturees: List[str] = []
    file_sortie: queue.Queue[str | None] = queue.Queue()
    intervalle_lecture = max(0.02, intervalle_lecture_secondes)
    flux_termine = False
    timeout_declenche = threading.Event()
    message_timeout = (
        f"Commande expiree apres {timeout_secondes} secondes: {' '.join(commande)}. "
        "Action recommandee: verifier la connectivite puis ajuster le timeout dans config_maintenance.json."
    )

    def lire_flux() -> None:
        """Lit le flux du processus dans un thread dedie.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        try:
            for ligne_brute in iter(flux_sortie.readline, ""):
                file_sortie.put(ligne_brute.rstrip("\r\n"))
        finally:
            file_sortie.put(None)

    def declencher_timeout() -> None:
        """Force l arret du processus quand le delai maximal est depasse.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        if processus.poll() is not None:
            return
        timeout_declenche.set()
        try:
            processus.kill()
        except OSError:
            pass

    thread_lecture = threading.Thread(target=lire_flux, daemon=True)
    thread_lecture.start()
    minuteur_timeout = threading.Timer(max(1, timeout_secondes), declencher_timeout)
    minuteur_timeout.daemon = True
    minuteur_timeout.start()

    try:
        while True:
            if processus.poll() is not None and flux_termine and file_sortie.empty():
                break

            attente = intervalle_lecture if processus.poll() is None else 0.02
            try:
                ligne = file_sortie.get(timeout=attente)
            except queue.Empty:
                continue

            if ligne is None:
                flux_termine = True
                continue

            if ligne:
                lignes_capturees.append(ligne)
                diffuser_ligne(consommateur_sortie, ligne)
    finally:
        minuteur_timeout.cancel()
        try:
            processus.wait(timeout=1)
        except subprocess.TimeoutExpired:
            processus.kill()
            processus.wait(timeout=1)
        thread_lecture.join(timeout=1)
        flux_sortie.close()

    while not file_sortie.empty():
        ligne = file_sortie.get_nowait()
        if ligne is None:
            continue
        if ligne:
            lignes_capturees.append(ligne)
            diffuser_ligne(consommateur_sortie, ligne)

    if not lignes_capturees:
        lignes_capturees.append("(aucune sortie)")
        diffuser_ligne(consommateur_sortie, "(aucune sortie)")

    sortie_complete = "\n".join(lignes_capturees)
    code_retour = processus.returncode if processus.returncode is not None else 1
    if timeout_declenche.is_set():
        diffuser_ligne(consommateur_sortie, message_timeout)
        return False, message_timeout
    if code_retour == 0:
        return True, sortie_complete

    message_echec = f"Commande en echec (code={code_retour}) pour: {' '.join(commande)}"
    diffuser_ligne(consommateur_sortie, message_echec)
    return False, f"{message_echec}\n{sortie_complete}"
