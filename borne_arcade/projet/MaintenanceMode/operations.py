"""Operations disponibles dans le mode maintenance de la borne."""

from __future__ import annotations

import datetime
import json
import os
import select
import shutil
import subprocess
import time
from pathlib import Path
from typing import Callable, Dict, List, Tuple


ConsommateurJournal = Callable[[str], None]
TIMEOUT_PAR_DEFAUT = 120
TIMEOUT_DIAGNOSTIC_SECONDES = 20
INTERVALLE_LECTURE_PAR_DEFAUT_MS = 100
DOSSIER_CACHE_LOGS_RELATIF = Path(".cache") / "maintenance_logicielle" / "logs"
DOSSIER_TEMPORAIRE_LOGS = Path("/tmp") / "maintenance_logicielle" / "logs"
FICHIER_TEST_ECRITURE_LOGS = ".ecriture_logs_maintenance.tmp"
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
    "fenetre": {"largeur": 1280, "hauteur": 720, "fps": 30},
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
        "nombre_lignes_journal": 18,
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
    },
    "temps_max_secondes": {
        "diagnostic": 20,
        "git_pull": 240,
        "pipeline_post_pull": 600,
        "mise_a_jour_os": 1800,
        "reset_pre_requis": 1800,
    },
    "fichier_verrouillage": ".verrouillage_mode_maintenance",
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
            "id": "git_pull",
            "titre": "Git pull",
            "description": "Met a jour le depot local en fast-forward.",
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
            "description": "Purge apt des prerequis borne + nettoyage local pour retest a zero.",
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
) -> Tuple[bool, str, Path]:
    """Execute une operation de maintenance et journalise son resultat.

    Args:
        operation_id: Identifiant de l operation a executer.
        configuration: Configuration chargee du mode maintenance.
        consommateur_journal: Callback optionnel pour afficher les logs en direct.

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
        elif operation_id == "git_pull":
            succes, message, _ = operation_git_pull(configuration, racine_projet, chemin_journal, journaliser)
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

    succes_global = True
    intervalle_lecture = extraire_intervalle_lecture(configuration)
    journaliser("=== Diagnostic maintenance ===")

    for commande in commandes:
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
            journaliser(f"ERREUR: {sortie.splitlines()[0]}")

    if succes_global:
        return True, "Diagnostic termine avec succes.", chemin_journal
    return False, "Diagnostic termine avec erreurs (voir journal).", chemin_journal


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

    journaliser(f"ERREUR: {sortie.splitlines()[0]}")
    return False, "Echec git pull. Verifiez les conflits et la connexion.", chemin_journal


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

    journaliser(f"ERREUR: {sortie.splitlines()[0]}")
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
            journaliser(f"ERREUR: {sortie.splitlines()[0]}")
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


def operation_reset_pre_requis(
    configuration: Dict[str, object],
    racine_projet: Path,
    chemin_journal: Path,
    journaliser: ConsommateurJournal,
) -> Tuple[bool, str, Path]:
    """Purge les prerequis systeme puis nettoie les artefacts locaux.

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

    commandes = [
        prefixe_sudo + ["apt-get", "remove", "--purge", "-y"] + PAQUETS_SYSTEME_BORNE,
        prefixe_sudo + ["apt-get", "autoremove", "--purge", "-y"],
        prefixe_sudo + ["apt-get", "clean"],
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
            journaliser(f"ERREUR: {sortie.splitlines()[0]}")
            return False, "Echec reset prerequis systeme (voir journal).", chemin_journal

    succes_nettoyage, message_nettoyage = nettoyer_artefacts_reset(racine_projet, journaliser)
    if not succes_nettoyage:
        return False, message_nettoyage, chemin_journal

    journaliser(message_nettoyage)
    return True, "Reset prerequis termine. Relancez bootstrap_borne.sh pour reinstaller.", chemin_journal


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
) -> Tuple[bool, str]:
    """Execute une commande systeme et retourne sa sortie combinee.

    Args:
        commande: Liste des arguments de la commande.
        repertoire_travail: Repertoire de travail de la commande.
        timeout_secondes: Delai maximal en secondes.
        consommateur_sortie: Callback optionnel pour remonter les lignes en direct.
        intervalle_lecture_secondes: Intervalle de polling du flux processus.

    Returns:
        Un tuple (succes, sortie texte).
    """

    try:
        processus = subprocess.Popen(
            commande,
            cwd=str(repertoire_travail),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
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

    lignes_capturees: List[str] = []
    instant_depart = time.monotonic()
    limite_temps = instant_depart + max(1, timeout_secondes)
    intervalle_lecture = max(0.02, intervalle_lecture_secondes)

    try:
        while True:
            maintenant = time.monotonic()
            if maintenant >= limite_temps:
                processus.kill()
                try:
                    processus.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    pass
                message_timeout = (
                    f"Commande expiree apres {timeout_secondes} secondes: {' '.join(commande)}. "
                    "Action recommandee: verifier la connectivite puis ajuster le timeout dans config_maintenance.json."
                )
                diffuser_ligne(consommateur_sortie, message_timeout)
                return False, message_timeout

            temps_restant = max(0.0, limite_temps - maintenant)
            attente = min(intervalle_lecture, temps_restant)
            flux_pret, _, _ = select.select([flux_sortie], [], [], attente)

            if flux_sortie in flux_pret:
                ligne_brute = flux_sortie.readline()
                if ligne_brute:
                    ligne = ligne_brute.rstrip("\n")
                    if ligne:
                        lignes_capturees.append(ligne)
                        diffuser_ligne(consommateur_sortie, ligne)

            if processus.poll() is not None:
                break

        sortie_restante = flux_sortie.read()
        if sortie_restante:
            for ligne in sortie_restante.splitlines():
                if ligne:
                    lignes_capturees.append(ligne)
                    diffuser_ligne(consommateur_sortie, ligne)
    finally:
        flux_sortie.close()

    if not lignes_capturees:
        lignes_capturees.append("(aucune sortie)")
        diffuser_ligne(consommateur_sortie, "(aucune sortie)")

    sortie_complete = "\n".join(lignes_capturees)
    code_retour = processus.returncode if processus.returncode is not None else 1
    if code_retour == 0:
        return True, sortie_complete

    message_echec = f"Commande en echec (code={code_retour}) pour: {' '.join(commande)}"
    diffuser_ligne(consommateur_sortie, message_echec)
    return False, f"{message_echec}\n{sortie_complete}"
