#!/usr/bin/env python3
"""Execute les contrats automatiques et les tests cibles des jeux de la borne."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

RACINE_PROJET = Path(__file__).resolve().parents[2]
CHEMIN_MATRICE = RACINE_PROJET / "config" / "matrice_tests_jeux.json"
RUNTIMES_AUTORISES = {"java", "python", "lua"}
REPERTOIRE_JEUX = RACINE_PROJET / "borne_arcade" / "projet"
DOSSIER_CLASSES_JEUX = RACINE_PROJET / "build" / "classes" / "jeux"
PYTHON_PAR_DEFAUT = os.environ.get("COMMANDE_PYTHON", "python3")


@dataclass(frozen=True)
class DefinitionJeu:
    """Decrit un jeu tel qu il apparait dans la matrice de tests.

    Attributes:
        nom: Nom logique du jeu.
        runtime: Runtime principal du jeu.
        dossier: Dossier du jeu relatif a la racine du depot.
        lanceur: Script de lancement relatif a la racine du depot.
        entree: Point d entree du jeu.
        fichiers_obligatoires: Fichiers de configuration et ressources obligatoires.
        commande_test_cible: Commande obligatoire pour le test cible.
    """

    nom: str
    runtime: str
    dossier: Path
    lanceur: Path
    entree: str
    fichiers_obligatoires: tuple[str, ...]
    commande_test_cible: tuple[str, ...]


def charger_arguments() -> argparse.Namespace:
    """Charge les arguments de ligne de commande.

    Returns:
        Namespace argparse normalise.
    """

    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument(
        "--contrats-seulement",
        action="store_true",
        help="Execute uniquement les contrats structurels et le smoke test.",
    )
    analyseur.add_argument(
        "--tests-cibles-seulement",
        action="store_true",
        help="Execute uniquement les commandes de tests cibles declarees.",
    )
    analyseur.add_argument(
        "--runtime",
        choices=sorted(RUNTIMES_AUTORISES),
        help="Filtre l execution sur un runtime particulier.",
    )
    analyseur.add_argument(
        "--jeu",
        help="Filtre l execution sur un seul jeu par son nom logique.",
    )
    return analyseur.parse_args()



def charger_definitions_jeux() -> list[DefinitionJeu]:
    """Charge et valide la matrice de tests des jeux.

    Returns:
        Liste des definitions de jeux triees par nom.

    Raises:
        ValueError: si la matrice est invalide.
    """

    contenu = json.loads(CHEMIN_MATRICE.read_text(encoding="utf-8"))
    entrees = contenu.get("jeux")
    if not isinstance(entrees, list):
        raise ValueError("La matrice de tests doit contenir une cle 'jeux' de type liste.")

    definitions: list[DefinitionJeu] = []
    noms_vus: set[str] = set()
    for entree in entrees:
        nom = entree.get("nom")
        runtime = entree.get("runtime")
        dossier = entree.get("dossier")
        lanceur = entree.get("lanceur")
        point_entree = entree.get("entree")
        fichiers_obligatoires = entree.get("fichiers_obligatoires")
        commande_test_cible = entree.get("commande_test_cible")

        if not isinstance(nom, str) or not nom.strip():
            raise ValueError("Chaque jeu doit definir un nom non vide dans la matrice.")
        if nom in noms_vus:
            raise ValueError(f"Nom de jeu duplique dans la matrice: {nom}")
        noms_vus.add(nom)

        if runtime not in RUNTIMES_AUTORISES:
            raise ValueError(f"Runtime invalide pour {nom}: {runtime}")
        if not isinstance(dossier, str) or not isinstance(lanceur, str) or not isinstance(point_entree, str):
            raise ValueError(f"Chemins invalides dans la matrice pour {nom}")
        if not isinstance(fichiers_obligatoires, list) or not all(isinstance(valeur, str) for valeur in fichiers_obligatoires):
            raise ValueError(f"fichiers_obligatoires invalide pour {nom}")
        if not isinstance(commande_test_cible, list) or not commande_test_cible:
            raise ValueError(f"commande_test_cible obligatoire et invalide pour {nom}")
        if not all(isinstance(valeur, str) for valeur in commande_test_cible):
            raise ValueError(f"commande_test_cible invalide pour {nom}")

        definitions.append(
            DefinitionJeu(
                nom=nom,
                runtime=runtime,
                dossier=RACINE_PROJET / dossier,
                lanceur=RACINE_PROJET / lanceur,
                entree=point_entree,
                fichiers_obligatoires=tuple(fichiers_obligatoires),
                commande_test_cible=tuple(commande_test_cible),
            )
        )

    return sorted(definitions, key=lambda definition: definition.nom.lower())



def verifier_bijection_matrice_et_disque(definitions: Sequence[DefinitionJeu]) -> list[str]:
    """Verifie la correspondance exacte entre matrice et dossiers de jeux.

    Args:
        definitions: Definitions chargees depuis la matrice.

    Returns:
        Liste de messages d erreur detectes.
    """

    noms_matrice = {definition.nom for definition in definitions}
    noms_disque = {chemin.name for chemin in REPERTOIRE_JEUX.iterdir() if chemin.is_dir()}
    erreurs: list[str] = []

    for nom_manquant in sorted(noms_matrice - noms_disque):
        erreurs.append(
            f"ERREUR {nom_manquant} : dossier declare absent du disque. "
            f"ACTION RECOMMANDEE: creez borne_arcade/projet/{nom_manquant} ou corrigez {CHEMIN_MATRICE.relative_to(RACINE_PROJET)}."
        )
    for nom_orphelin in sorted(noms_disque - noms_matrice):
        erreurs.append(
            f"ERREUR {nom_orphelin} : dossier jeu non reference dans la matrice. "
            f"ACTION RECOMMANDEE: ajoutez ce jeu dans {CHEMIN_MATRICE.relative_to(RACINE_PROJET)}."
        )
    return erreurs



def construire_commande(commande_brute: Sequence[str]) -> list[str]:
    """Construit une commande executable depuis la matrice.

    Args:
        commande_brute: Commande declaree dans la matrice.

    Returns:
        Commande prete a l execution.
    """

    commande = list(commande_brute)
    if not commande:
        return commande

    if commande[0] == "python3":
        commande[0] = PYTHON_PAR_DEFAUT
    elif commande[0].startswith("./"):
        commande[0] = str((RACINE_PROJET / commande[0][2:]).resolve())
    return commande



def extraire_message_sortie(sortie: str) -> str:
    """Extrait une ligne utile d une sortie de commande.

    Args:
        sortie: Sortie standard + erreur agregee.

    Returns:
        Premiere ligne non vide, ou un message de secours.
    """

    for ligne in sortie.splitlines():
        ligne_normalisee = ligne.strip()
        if ligne_normalisee:
            return ligne_normalisee
    return "sortie indisponible"



def executer_commande(commande: Sequence[str], environnement: dict[str, str] | None = None) -> tuple[bool, str]:
    """Execute une commande et capture sa sortie.

    Args:
        commande: Commande a executer.
        environnement: Variables d environnement supplementaires.

    Returns:
        Tuple (succes, sortie combinee).
    """

    env = os.environ.copy()
    if environnement is not None:
        env.update(environnement)

    resultat = subprocess.run(
        list(commande),
        cwd=RACINE_PROJET,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    return resultat.returncode == 0, resultat.stdout



def verifier_fichiers_obligatoires(definition: DefinitionJeu) -> None:
    """Verifie la presence et la lisibilite des fichiers obligatoires.

    Args:
        definition: Jeu a verifier.

    Raises:
        ValueError: si un fichier obligatoire est invalide.
    """

    if not definition.dossier.is_dir():
        raise ValueError(
            f"dossier jeu introuvable: {definition.dossier.relative_to(RACINE_PROJET)}. "
            f"ACTION RECOMMANDEE: restaurez le dossier ou corrigez la matrice de tests."
        )

    for nom_fichier in definition.fichiers_obligatoires:
        chemin_fichier = definition.dossier / nom_fichier
        if not chemin_fichier.exists():
            raise ValueError(
                f"fichier obligatoire absent: {chemin_fichier.relative_to(RACINE_PROJET)}. "
                f"ACTION RECOMMANDEE: ajoutez ce fichier avant de relancer les tests."
            )

    description = definition.dossier / "description.txt"
    if not description.read_text(encoding="utf-8").strip():
        raise ValueError(
            f"description.txt vide pour {definition.nom}. "
            f"ACTION RECOMMANDEE: renseignez une description utilisateur exploitable."
        )

    bouton = definition.dossier / "bouton.txt"
    if not bouton.read_text(encoding="utf-8").strip():
        raise ValueError(
            f"bouton.txt vide pour {definition.nom}. "
            f"ACTION RECOMMANDEE: renseignez le mapping joystick/boutons du jeu."
        )

    highscore = definition.dossier / "highscore"
    if not os.access(highscore, os.W_OK):
        raise ValueError(
            f"highscore non modifiable pour {definition.nom}. "
            f"ACTION RECOMMANDEE: corrigez les permissions du fichier highscore."
        )



def verifier_lanceur(definition: DefinitionJeu) -> None:
    """Verifie que le lanceur du jeu existe et est executable.

    Args:
        definition: Jeu a verifier.

    Raises:
        ValueError: si le lanceur est absent ou non executable.
    """

    if not definition.lanceur.is_file():
        raise ValueError(
            f"lanceur introuvable: {definition.lanceur.relative_to(RACINE_PROJET)}. "
            f"ACTION RECOMMANDEE: ajoutez le script de lancement du jeu."
        )
    if not os.access(definition.lanceur, os.X_OK):
        raise ValueError(
            f"lanceur non executable: {definition.lanceur.relative_to(RACINE_PROJET)}. "
            f"ACTION RECOMMANDEE: rendez le script executable avec chmod +x."
        )



def verifier_point_entree(definition: DefinitionJeu) -> None:
    """Verifie le point d entree du jeu selon son runtime.

    Args:
        definition: Jeu a verifier.

    Raises:
        ValueError: si le point d entree est invalide.
    """

    if definition.runtime == "java":
        source = definition.dossier / f"{definition.entree}.java"
        classe = DOSSIER_CLASSES_JEUX / definition.nom / f"{definition.entree}.class"
        if not source.is_file() and not classe.is_file():
            raise ValueError(
                f"classe principale introuvable pour {definition.nom}: {definition.entree}. "
                f"ACTION RECOMMANDEE: verifiez la classe d entree et recompilez la borne."
            )
        return

    entree = definition.dossier / definition.entree
    if definition.runtime == "python":
        if entree.is_dir():
            if not (entree / "__main__.py").is_file():
                raise ValueError(
                    f"point d entree Python introuvable pour {definition.nom}: {definition.entree}/__main__.py. "
                    f"ACTION RECOMMANDEE: ajoutez __main__.py ou corrigez la matrice."
                )
            return
        if not entree.is_file():
            raise ValueError(
                f"point d entree Python introuvable pour {definition.nom}: {definition.entree}. "
                f"ACTION RECOMMANDEE: corrigez le chemin d entree du jeu."
            )
        return

    if not entree.is_file():
        raise ValueError(
            f"fichier main.lua introuvable pour {definition.nom}. "
            f"ACTION RECOMMANDEE: ajoutez un point d entree Lua valide."
        )



def verifier_runtime_specifique(definition: DefinitionJeu) -> None:
    """Applique les verifications specifiques au runtime du jeu.

    Args:
        definition: Jeu a verifier.

    Raises:
        ValueError: si une verification runtime-specifique echoue.
    """

    if definition.runtime != "lua":
        return

    compilateur_lua = shutil.which("luac") or shutil.which("luac5.4") or shutil.which("luac5.3") or shutil.which("luac5.2")
    if compilateur_lua is None:
        print(
            f"INFO {definition.nom} : verification Lua complementaire ignoree (aucun compilateur luac detecte). "
            f"Action recommandee: installez lua5.4 pour activer la verification syntaxique approfondie."
        )
        return

    succes, sortie = executer_commande([compilateur_lua, "-p", str(definition.dossier / definition.entree)])
    if not succes:
        raise ValueError(
            f"echec de verification Lua pour {definition.nom}: {extraire_message_sortie(sortie)}. "
            f"ACTION RECOMMANDEE: corrigez la syntaxe Lua puis relancez les tests."
        )



def executer_smoke_test(definition: DefinitionJeu) -> None:
    """Execute le smoke test non interactif du lanceur.

    Args:
        definition: Jeu a verifier.

    Raises:
        ValueError: si le smoke test echoue.
    """

    succes, sortie = executer_commande(
        [str(definition.lanceur.resolve())],
        environnement={"BORNE_MODE_TEST_JEU": "1"},
    )
    if not succes:
        raise ValueError(
            f"lanceur smoke en echec pour {definition.nom}: {extraire_message_sortie(sortie)}. "
            f"ACTION RECOMMANDEE: corrigez le lanceur ou le point d entree du jeu."
        )



def executer_contrat(definition: DefinitionJeu) -> None:
    """Execute le contrat complet d un jeu.

    Args:
        definition: Jeu a verifier.
    """

    verifier_fichiers_obligatoires(definition)
    verifier_lanceur(definition)
    verifier_point_entree(definition)
    verifier_runtime_specifique(definition)
    executer_smoke_test(definition)



def executer_test_cible(definition: DefinitionJeu) -> None:
    """Execute la commande de test cible d un jeu si elle existe.

    Args:
        definition: Jeu a verifier.

    Raises:
        ValueError: si la commande de test cible echoue.
    """

    commande = construire_commande(definition.commande_test_cible)
    succes, sortie = executer_commande(commande)
    if not succes:
        raise ValueError(
            f"test cible en echec pour {definition.nom}: {extraire_message_sortie(sortie)}. "
            f"ACTION RECOMMANDEE: corrigez le jeu ou son test cible puis relancez la suite."
        )



def filtrer_definitions(definitions: Sequence[DefinitionJeu], runtime: str | None, jeu: str | None) -> Iterable[DefinitionJeu]:
    """Filtre les definitions selon le runtime demande.

    Args:
        definitions: Definitions chargees.
        runtime: Runtime filtre ou None.
        jeu: Nom de jeu filtre ou None.

    Returns:
        Iterable filtre.
    """

    for definition in definitions:
        if runtime is not None and definition.runtime != runtime:
            continue
        if jeu is not None and definition.nom != jeu:
            continue
        yield definition



def main() -> int:
    """Point d entree du runner de contrats jeux.

    Returns:
        Code de sortie shell.
    """

    arguments = charger_arguments()
    if arguments.contrats_seulement and arguments.tests_cibles_seulement:
        print(
            "ERREUR: options incompatibles --contrats-seulement et --tests-cibles-seulement. "
            "ACTION RECOMMANDEE: choisissez un seul mode d execution."
        )
        return 1

    try:
        definitions = charger_definitions_jeux()
    except (OSError, ValueError, json.JSONDecodeError) as erreur:
        print(
            f"ERREUR matrice : {erreur}. ACTION RECOMMANDEE: corrigez {CHEMIN_MATRICE.relative_to(RACINE_PROJET)} puis relancez la suite."
        )
        return 1

    erreurs_globales = verifier_bijection_matrice_et_disque(definitions)
    for erreur in erreurs_globales:
        print(erreur)
    if erreurs_globales:
        return 1

    if arguments.jeu is not None and arguments.jeu not in {definition.nom for definition in definitions}:
        print(
            f"ERREUR: jeu inconnu {arguments.jeu}. "
            f"ACTION RECOMMANDEE: utilisez un jeu reference dans {CHEMIN_MATRICE.relative_to(RACINE_PROJET)}."
        )
        return 1

    erreurs_detectees = False
    for definition in filtrer_definitions(definitions, arguments.runtime, arguments.jeu):
        try:
            if not arguments.tests_cibles_seulement:
                executer_contrat(definition)
                print(f"OK {definition.nom} : contrat")
            if not arguments.contrats_seulement:
                executer_test_cible(definition)
                print(f"OK {definition.nom} : test cible")
        except ValueError as erreur:
            print(f"ERREUR {definition.nom} : {erreur}")
            erreurs_detectees = True

    return 1 if erreurs_detectees else 0


if __name__ == "__main__":
    sys.exit(main())
