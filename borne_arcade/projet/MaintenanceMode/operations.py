"""Operations disponibles dans le mode maintenance de la borne."""

from __future__ import annotations

import datetime
import json
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple


CONFIGURATION_PAR_DEFAUT = {
    "fenetre": {"largeur": 1280, "hauteur": 720, "fps": 30},
    "temps_max_secondes": {
        "diagnostic": 20,
        "git_pull": 240,
        "pipeline_post_pull": 600,
        "mise_a_jour_os": 1800,
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


def executer_operation(operation_id: str, configuration: Dict[str, object]) -> Tuple[bool, str, Path]:
    """Execute une operation de maintenance et journalise son resultat.

    Args:
        operation_id: Identifiant de l operation a executer.
        configuration: Configuration chargee du mode maintenance.

    Returns:
        Un tuple (succes, message, chemin_journal).
    """

    racine_projet = obtenir_racine_projet()
    chemin_journal = preparer_fichier_journal(racine_projet, operation_id)

    if operation_id == "diagnostic":
        return operation_diagnostic(configuration, racine_projet, chemin_journal)
    if operation_id == "git_pull":
        return operation_git_pull(configuration, racine_projet, chemin_journal)
    if operation_id == "pipeline_post_pull":
        return operation_pipeline_post_pull(configuration, racine_projet, chemin_journal)
    if operation_id == "mise_a_jour_os":
        return operation_mise_a_jour_os(configuration, racine_projet, chemin_journal)

    message = f"Operation inconnue: {operation_id}"
    chemin_journal.write_text(message + "\n", encoding="utf-8")
    return False, message, chemin_journal


def preparer_fichier_journal(racine_projet: Path, operation_id: str) -> Path:
    """Prepare le fichier de journalisation d une operation.

    Args:
        racine_projet: Racine du depot.
        operation_id: Identifiant operation.

    Returns:
        Chemin complet du journal.
    """

    dossier_logs = racine_projet / "logs"
    dossier_logs.mkdir(parents=True, exist_ok=True)
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
        return 120
    valeur = section_timeouts.get(operation_id, 120)
    try:
        return int(valeur)
    except (TypeError, ValueError):
        return 120


def operation_diagnostic(
    configuration: Dict[str, object],
    racine_projet: Path,
    chemin_journal: Path,
) -> Tuple[bool, str, Path]:
    """Execute un diagnostic rapide du systeme.

    Args:
        configuration: Configuration chargee.
        racine_projet: Racine du depot.
        chemin_journal: Journal cible.

    Returns:
        Resultat (succes, message, chemin journal).
    """

    _ = configuration
    commandes = [
        ["uname", "-a"],
        ["python3", "--version"],
        ["java", "-version"],
        ["free", "-h"],
        ["df", "-h", str(racine_projet)],
    ]

    lignes_journal = ["=== Diagnostic maintenance ==="]
    succes_global = True
    for commande in commandes:
        succes, sortie = executer_commande(commande, racine_projet, timeout_secondes=20)
        lignes_journal.append(f"$ {' '.join(commande)}")
        lignes_journal.append(sortie)
        if not succes:
            succes_global = False

    chemin_journal.write_text("\n".join(lignes_journal) + "\n", encoding="utf-8")
    if succes_global:
        return True, "Diagnostic termine avec succes.", chemin_journal
    return False, "Diagnostic termine avec erreurs (voir journal).", chemin_journal


def operation_git_pull(
    configuration: Dict[str, object],
    racine_projet: Path,
    chemin_journal: Path,
) -> Tuple[bool, str, Path]:
    """Execute un git pull fast-forward sur le depot.

    Args:
        configuration: Configuration chargee.
        racine_projet: Racine du depot.
        chemin_journal: Journal cible.

    Returns:
        Resultat (succes, message, chemin journal).
    """

    timeout_secondes = extraire_timeout(configuration, "git_pull")
    succes, sortie = executer_commande(
        ["git", "-C", str(racine_projet), "pull", "--ff-only"],
        racine_projet,
        timeout_secondes=timeout_secondes,
    )
    chemin_journal.write_text(sortie + "\n", encoding="utf-8")

    if succes:
        return True, "Git pull termine.", chemin_journal
    return False, "Echec git pull. Verifiez les conflits et la connexion.", chemin_journal


def operation_pipeline_post_pull(
    configuration: Dict[str, object],
    racine_projet: Path,
    chemin_journal: Path,
) -> Tuple[bool, str, Path]:
    """Execute le pipeline post-pull versionne du projet.

    Args:
        configuration: Configuration chargee.
        racine_projet: Racine du depot.
        chemin_journal: Journal cible.

    Returns:
        Resultat (succes, message, chemin journal).
    """

    timeout_secondes = extraire_timeout(configuration, "pipeline_post_pull")
    script_pipeline = racine_projet / "scripts" / "deploiement" / "post_pull_update.sh"
    succes, sortie = executer_commande(
        [str(script_pipeline)],
        racine_projet,
        timeout_secondes=timeout_secondes,
    )
    chemin_journal.write_text(sortie + "\n", encoding="utf-8")

    if succes:
        return True, "Pipeline post-pull termine.", chemin_journal
    return False, "Pipeline post-pull en erreur. Consultez le journal.", chemin_journal


def operation_mise_a_jour_os(
    configuration: Dict[str, object],
    racine_projet: Path,
    chemin_journal: Path,
) -> Tuple[bool, str, Path]:
    """Execute la mise a jour systeme via apt.

    Args:
        configuration: Configuration chargee.
        racine_projet: Racine du depot.
        chemin_journal: Journal cible.

    Returns:
        Resultat (succes, message, chemin journal).
    """

    timeout_secondes = extraire_timeout(configuration, "mise_a_jour_os")
    prefixe_sudo = obtenir_prefixe_privileges_systeme()
    if prefixe_sudo is None:
        message = (
            "Mise a jour OS impossible: sudo non disponible en mode non interactif. "
            "Action recommandee: lancer la borne avec sudo ou executer la mise a jour depuis un terminal admin."
        )
        chemin_journal.write_text(message + "\n", encoding="utf-8")
        return False, message, chemin_journal

    commandes = [
        prefixe_sudo + ["apt-get", "update"],
        prefixe_sudo + ["apt-get", "full-upgrade", "-y"],
    ]

    lignes_journal = []
    for commande in commandes:
        succes, sortie = executer_commande(commande, racine_projet, timeout_secondes=timeout_secondes)
        lignes_journal.append(f"$ {' '.join(commande)}")
        lignes_journal.append(sortie)
        if not succes:
            chemin_journal.write_text("\n".join(lignes_journal) + "\n", encoding="utf-8")
            return False, "Echec de la mise a jour OS (voir journal).", chemin_journal

    chemin_journal.write_text("\n".join(lignes_journal) + "\n", encoding="utf-8")
    return True, "Mise a jour OS terminee.", chemin_journal


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


def executer_commande(
    commande: List[str],
    repertoire_travail: Path,
    timeout_secondes: int,
) -> Tuple[bool, str]:
    """Execute une commande systeme et retourne sa sortie combinee.

    Args:
        commande: Liste des arguments de la commande.
        repertoire_travail: Repertoire de travail de la commande.
        timeout_secondes: Delai maximal en secondes.

    Returns:
        Un tuple (succes, sortie texte).
    """

    try:
        resultat = subprocess.run(
            commande,
            cwd=str(repertoire_travail),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout_secondes,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return False, f"Commande expiree apres {timeout_secondes} secondes: {' '.join(commande)}"
    except FileNotFoundError:
        return False, f"Commande introuvable: {commande[0]}"

    sortie = resultat.stdout.strip()
    if not sortie:
        sortie = "(aucune sortie)"

    if resultat.returncode == 0:
        return True, sortie
    return False, f"code={resultat.returncode}\n{sortie}"
