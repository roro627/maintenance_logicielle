#!/usr/bin/env python3
"""Genere et verifie les README standardises des jeux de la borne."""

from __future__ import annotations

import argparse
import difflib
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

RACINE_PROJET = Path(__file__).resolve().parents[2]
DOSSIER_JEUX = RACINE_PROJET / "borne_arcade" / "projet"
CHEMIN_MATRICE = RACINE_PROJET / "config" / "matrice_tests_jeux.json"
CHEMIN_METADONNEES = RACINE_PROJET / "config" / "readme_jeux.json"
CHEMIN_TEMPLATE = RACINE_PROJET / "docs" / "modeles" / "README_jeu.md"
NOM_README_NORMALISE = "README.md"
NOM_README_MINUSCULE = "readme.md"
NOMS_DOCS_LOCALES = ("GUIDE_UTILISATEUR.md", "DOCUMENTATION_DEVELOPPEUR.md")
LIENS_DOCUMENTATION_COMMUNE = (
    ("Ajout d un jeu", RACINE_PROJET / "docs" / "ajout_jeu.md"),
    ("Tests", RACINE_PROJET / "docs" / "tests.md"),
    ("Utilisateur", RACINE_PROJET / "docs" / "utilisateur.md"),
)
FICHIERS_IMPORTANTS_DE_BASE = (
    ("description.txt", "Description courte affichee dans le menu principal."),
    ("bouton.txt", "Mapping borne lu par le menu et les boites de description."),
    ("highscore", "Persistance locale du score."),
    ("photo_small.png", "Vignette affichee dans le catalogue de jeux."),
)
LIBELLES_RUNTIME = {
    "java": "Java avec MG2D",
    "python": "Python",
    "lua": "Lua avec LOVE2D",
}
IGNORER_ACTIONS = {"", "aucun", "aucune", "rien", "inutilise"}


@dataclass(frozen=True)
class DefinitionTechniqueJeu:
    """Decrit les metadonnees techniques d un jeu.

    Attributes:
        nom: Nom logique du jeu.
        runtime: Runtime principal du jeu.
        dossier: Dossier absolu du jeu.
        lanceur: Script de lancement absolu.
        entree: Point d entree du jeu.
        commande_test_cible: Commande officielle de test cible.
    """

    nom: str
    runtime: str
    dossier: Path
    lanceur: Path
    entree: str
    commande_test_cible: tuple[str, ...]


@dataclass(frozen=True)
class CommandeBorne:
    """Decrit une commande borne a afficher dans le README.

    Attributes:
        commande: Libelle de la commande ou du bouton.
        action: Effet de cette commande dans le jeu.
    """

    commande: str
    action: str


@dataclass(frozen=True)
class MetadonneesReadmeJeu:
    """Decrit les contenus editoriaux d un README de jeu.

    Attributes:
        nom: Nom logique du jeu.
        titre_affiche: Titre humain du README.
        resume: Resume utilisateur du jeu.
        commandes_borne: Mapping borne prioritaire si renseigne.
        particularites: Points fonctionnels ou techniques distinctifs.
        notes_maintenance: Notes de maintenance a conserver.
    """

    nom: str
    titre_affiche: str
    resume: str
    commandes_borne: tuple[CommandeBorne, ...]
    particularites: tuple[str, ...]
    notes_maintenance: tuple[str, ...]


def afficher_erreur(message: str, action: str) -> None:
    """Affiche une erreur claire sur la sortie standard d erreur.

    Args:
        message: Message d erreur principal.
        action: Action recommandee a l utilisateur.

    Returns:
        Aucun.
    """

    print(f"ERREUR: {message}", file=sys.stderr)
    print(f"ACTION RECOMMANDEE: {action}", file=sys.stderr)


def charger_arguments() -> argparse.Namespace:
    """Charge les arguments de ligne de commande.

    Returns:
        Namespace argparse normalise.
    """

    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument(
        "--jeu",
        help="Nom logique d un jeu pour limiter la generation ou la verification.",
    )
    analyseur.add_argument(
        "--verifier",
        action="store_true",
        help="Verifie que les README generes sont deja a jour sans les reecrire.",
    )
    return analyseur.parse_args()


def charger_json(chemin: Path) -> dict[str, Any]:
    """Charge un fichier JSON et retourne son contenu.

    Args:
        chemin: Fichier JSON a charger.

    Returns:
        Contenu JSON deserialise.

    Raises:
        ValueError: si le fichier n existe pas ou si son contenu est invalide.
    """

    if not chemin.is_file():
        raise ValueError(f"Fichier introuvable: {chemin.relative_to(RACINE_PROJET)}")

    try:
        return json.loads(chemin.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exception:
        raise ValueError(
            f"JSON invalide dans {chemin.relative_to(RACINE_PROJET)}: {exception.msg}"
        ) from exception


def valider_chaine_obligatoire(valeur: Any, cle: str, chemin: Path) -> str:
    """Valide une chaine obligatoire.

    Args:
        valeur: Valeur a valider.
        cle: Cle en cours de validation.
        chemin: Fichier source du contenu.

    Returns:
        Chaine normalisee.

    Raises:
        ValueError: si la valeur est absente ou vide.
    """

    if not isinstance(valeur, str) or not valeur.strip():
        raise ValueError(
            f"Valeur `{cle}` absente ou vide dans {chemin.relative_to(RACINE_PROJET)}."
        )
    return valeur.strip()


def valider_liste_chaines(valeur: Any, cle: str, chemin: Path) -> list[str]:
    """Valide une liste de chaines non vides.

    Args:
        valeur: Valeur a valider.
        cle: Cle en cours de validation.
        chemin: Fichier source du contenu.

    Returns:
        Liste de chaines normalisees.

    Raises:
        ValueError: si la liste est invalide.
    """

    if not isinstance(valeur, list):
        raise ValueError(
            f"Valeur `{cle}` invalide dans {chemin.relative_to(RACINE_PROJET)}: liste attendue."
        )

    valeurs: list[str] = []
    for element in valeur:
        if not isinstance(element, str) or not element.strip():
            raise ValueError(
                f"Valeur vide detectee dans `{cle}` de {chemin.relative_to(RACINE_PROJET)}."
            )
        valeurs.append(element.strip())
    return valeurs


def charger_commandes_borne(valeur: Any, nom_jeu: str) -> tuple[CommandeBorne, ...]:
    """Charge la liste de commandes borne d un jeu.

    Args:
        valeur: Valeur brute issue du JSON.
        nom_jeu: Nom logique du jeu pour les messages d erreur.

    Returns:
        Tuple de commandes borne, possiblement vide si aucune n est declaree.

    Raises:
        ValueError: si la structure est invalide.
    """

    if valeur is None:
        return ()

    if not isinstance(valeur, list):
        raise ValueError(
            f"`commandes_borne` doit etre une liste pour {nom_jeu} dans "
            f"{CHEMIN_METADONNEES.relative_to(RACINE_PROJET)}."
        )

    commandes: list[CommandeBorne] = []
    for entree in valeur:
        if not isinstance(entree, dict):
            raise ValueError(f"Chaque commande borne doit etre un objet JSON pour {nom_jeu}.")
        commande = valider_chaine_obligatoire(entree.get("commande"), "commande", CHEMIN_METADONNEES)
        action = valider_chaine_obligatoire(entree.get("action"), "action", CHEMIN_METADONNEES)
        commandes.append(CommandeBorne(commande=commande, action=action))
    return tuple(commandes)


def charger_definitions_techniques() -> dict[str, DefinitionTechniqueJeu]:
    """Charge et valide les definitions techniques depuis la matrice.

    Returns:
        Dictionnaire `nom -> definition technique`.

    Raises:
        ValueError: si la matrice est invalide.
    """

    contenu = charger_json(CHEMIN_MATRICE)
    jeux = contenu.get("jeux")
    if not isinstance(jeux, list):
        raise ValueError(
            f"`jeux` doit etre une liste dans {CHEMIN_MATRICE.relative_to(RACINE_PROJET)}."
        )

    definitions: dict[str, DefinitionTechniqueJeu] = {}
    for entree in jeux:
        if not isinstance(entree, dict):
            raise ValueError("Chaque definition de jeu doit etre un objet JSON.")

        nom = valider_chaine_obligatoire(entree.get("nom"), "nom", CHEMIN_MATRICE)
        runtime = valider_chaine_obligatoire(entree.get("runtime"), "runtime", CHEMIN_MATRICE)
        dossier_relatif = valider_chaine_obligatoire(entree.get("dossier"), "dossier", CHEMIN_MATRICE)
        lanceur_relatif = valider_chaine_obligatoire(entree.get("lanceur"), "lanceur", CHEMIN_MATRICE)
        entree_principale = valider_chaine_obligatoire(entree.get("entree"), "entree", CHEMIN_MATRICE)
        commande_test_cible = valider_liste_chaines(
            entree.get("commande_test_cible"),
            "commande_test_cible",
            CHEMIN_MATRICE,
        )

        if nom in definitions:
            raise ValueError(f"Jeu duplique dans la matrice de tests: {nom}")

        definitions[nom] = DefinitionTechniqueJeu(
            nom=nom,
            runtime=runtime,
            dossier=RACINE_PROJET / dossier_relatif,
            lanceur=RACINE_PROJET / lanceur_relatif,
            entree=entree_principale,
            commande_test_cible=tuple(commande_test_cible),
        )

    return definitions


def charger_metadonnees_readme() -> dict[str, MetadonneesReadmeJeu]:
    """Charge et valide les metadonnees editoriales des README.

    Returns:
        Dictionnaire `nom -> metadonnees README`.

    Raises:
        ValueError: si les metadonnees sont invalides.
    """

    contenu = charger_json(CHEMIN_METADONNEES)
    jeux = contenu.get("jeux")
    if not isinstance(jeux, list):
        raise ValueError(
            f"`jeux` doit etre une liste dans {CHEMIN_METADONNEES.relative_to(RACINE_PROJET)}."
        )

    metadonnees: dict[str, MetadonneesReadmeJeu] = {}
    for entree in jeux:
        if not isinstance(entree, dict):
            raise ValueError("Chaque metadonnee README doit etre un objet JSON.")

        nom = valider_chaine_obligatoire(entree.get("nom"), "nom", CHEMIN_METADONNEES)
        titre_affiche = valider_chaine_obligatoire(
            entree.get("titre_affiche"),
            "titre_affiche",
            CHEMIN_METADONNEES,
        )
        resume = valider_chaine_obligatoire(entree.get("resume"), "resume", CHEMIN_METADONNEES)
        commandes = charger_commandes_borne(entree.get("commandes_borne"), nom)
        particularites = tuple(
            valider_liste_chaines(entree.get("particularites", []), "particularites", CHEMIN_METADONNEES)
        )
        notes_maintenance = tuple(
            valider_liste_chaines(
                entree.get("notes_maintenance", []),
                "notes_maintenance",
                CHEMIN_METADONNEES,
            )
        )

        if nom in metadonnees:
            raise ValueError(f"Jeu duplique dans les metadonnees README: {nom}")

        metadonnees[nom] = MetadonneesReadmeJeu(
            nom=nom,
            titre_affiche=titre_affiche,
            resume=resume,
            commandes_borne=commandes,
            particularites=particularites,
            notes_maintenance=notes_maintenance,
        )

    return metadonnees


def verifier_bijection(
    definitions: dict[str, DefinitionTechniqueJeu],
    metadonnees: dict[str, MetadonneesReadmeJeu],
) -> None:
    """Verifie que les deux sources couvrent exactement les memes jeux.

    Args:
        definitions: Definitions techniques par jeu.
        metadonnees: Metadonnees README par jeu.

    Returns:
        Aucun.

    Raises:
        ValueError: si un jeu manque dans une des deux sources.
    """

    noms_techniques = set(definitions)
    noms_editoriaux = set(metadonnees)

    manquants_dans_metadonnees = sorted(noms_techniques - noms_editoriaux)
    manquants_dans_matrice = sorted(noms_editoriaux - noms_techniques)

    if manquants_dans_metadonnees:
        raise ValueError(
            "Jeux absents de config/readme_jeux.json: " + ", ".join(manquants_dans_metadonnees)
        )
    if manquants_dans_matrice:
        raise ValueError(
            "Jeux absents de config/matrice_tests_jeux.json: " + ", ".join(manquants_dans_matrice)
        )


def charger_template() -> str:
    """Charge le template source des README.

    Returns:
        Contenu du template.

    Raises:
        ValueError: si le template est absent ou vide.
    """

    if not CHEMIN_TEMPLATE.is_file():
        raise ValueError(f"Template introuvable: {CHEMIN_TEMPLATE.relative_to(RACINE_PROJET)}")

    contenu = CHEMIN_TEMPLATE.read_text(encoding="utf-8")
    if not contenu.strip():
        raise ValueError(f"Template vide: {CHEMIN_TEMPLATE.relative_to(RACINE_PROJET)}")
    return retirer_commentaire_initial_template(contenu)


def retirer_commentaire_initial_template(contenu: str) -> str:
    """Retire le commentaire HTML d entete du template avant rendu.

    Args:
        contenu: Contenu brut du template.

    Returns:
        Template pret au rendu.
    """

    contenu_epure = contenu.lstrip()
    if not contenu_epure.startswith("<!--"):
        return contenu

    index_fin = contenu_epure.find("-->")
    if index_fin == -1:
        return contenu
    return contenu_epure[index_fin + 3 :].lstrip()


def filtrer_jeux(
    definitions: dict[str, DefinitionTechniqueJeu],
    metadonnees: dict[str, MetadonneesReadmeJeu],
    nom_jeu: str | None,
) -> list[tuple[DefinitionTechniqueJeu, MetadonneesReadmeJeu]]:
    """Filtre les jeux a traiter.

    Args:
        definitions: Definitions techniques par jeu.
        metadonnees: Metadonnees README par jeu.
        nom_jeu: Nom logique cible eventuel.

    Returns:
        Liste des paires technique/editorial a traiter.

    Raises:
        ValueError: si le jeu cible est inconnu.
    """

    if nom_jeu is not None:
        if nom_jeu not in definitions:
            raise ValueError(f"Jeu inconnu pour la generation de README: {nom_jeu}")
        return [(definitions[nom_jeu], metadonnees[nom_jeu])]

    return [
        (definitions[nom], metadonnees[nom])
        for nom in sorted(definitions, key=str.lower)
    ]


def remplacer_placeholders(template: str, contexte: dict[str, str]) -> str:
    """Remplace les placeholders `{{cle}}` dans un template.

    Args:
        template: Template source.
        contexte: Dictionnaire de remplacement.

    Returns:
        Texte rendu.

    Raises:
        ValueError: si un placeholder attendu est absent du contexte.
    """

    rendu = template
    for cle, valeur in contexte.items():
        rendu = rendu.replace(f"{{{{{cle}}}}}", valeur)

    placeholders_restants = extraire_placeholders_restants(rendu)
    if placeholders_restants:
        raise ValueError(
            "Placeholders non resolus dans le template: " + ", ".join(placeholders_restants)
        )
    return rendu


def extraire_placeholders_restants(texte: str) -> list[str]:
    """Extrait les placeholders restants d un texte rendu.

    Args:
        texte: Texte a analyser.

    Returns:
        Liste des placeholders encore presents.
    """

    restants: list[str] = []
    debut = 0
    while True:
        index_debut = texte.find("{{", debut)
        if index_debut == -1:
            return restants
        index_fin = texte.find("}}", index_debut + 2)
        if index_fin == -1:
            return restants
        restants.append(texte[index_debut:index_fin + 2])
        debut = index_fin + 2


def construire_section_runtime_et_lancement(definition: DefinitionTechniqueJeu) -> str:
    """Construit la section runtime et lancement.

    Args:
        definition: Definition technique du jeu.

    Returns:
        Bloc Markdown correspondant.
    """

    lignes = [
        f"- Runtime principal: `{LIBELLES_RUNTIME.get(definition.runtime, definition.runtime)}`.",
        f"- Point d entree: `{definition.entree}`.",
        f"- Lanceur borne: `{definition.lanceur.relative_to(RACINE_PROJET).as_posix()}`.",
        f"- Lancement depuis la racine: `./{definition.lanceur.relative_to(RACINE_PROJET).as_posix()}`.",
    ]

    chemin_requirements = definition.dossier / "requirements.txt"
    if chemin_requirements.is_file():
        lignes.append(
            "- Dependances Python locales: "
            f"`pip install -r {chemin_requirements.relative_to(RACINE_PROJET).as_posix()}`."
        )

    return "\n".join(lignes)


def lire_commandes_borne_depuis_fichier(dossier_jeu: Path) -> tuple[CommandeBorne, ...]:
    """Construit un fallback de commandes borne a partir de `bouton.txt`.

    Args:
        dossier_jeu: Dossier absolu du jeu.

    Returns:
        Tuple de commandes borne fallback.
    """

    fichier_boutons = dossier_jeu / "bouton.txt"
    if not fichier_boutons.is_file():
        return ()

    lignes = fichier_boutons.read_text(encoding="utf-8").splitlines()
    if not lignes:
        return ()

    champs = [champ.strip() for champ in lignes[0].split(":")]
    if not champs:
        return ()

    commandes: list[CommandeBorne] = []
    joystick = champs[0] if champs else ""
    if joystick:
        commandes.append(CommandeBorne("Joystick", normaliser_action_bouton(joystick)))

    for index, action in enumerate(champs[1:], start=1):
        if not action:
            continue
        commande = f"Bouton {index}" if index <= 6 else f"Commande supplementaire {index - 6}"
        commandes.append(CommandeBorne(commande, normaliser_action_bouton(action)))

    return tuple(commandes)


def normaliser_action_bouton(action: str) -> str:
    """Normalise une action issue de `bouton.txt` pour la rendre plus lisible.

    Args:
        action: Action brute.

    Returns:
        Action normalisee.
    """

    action_normalisee = " ".join(action.strip().split())
    if action_normalisee.lower() in IGNORER_ACTIONS:
        return "Aucun usage documente dans le mapping brut."
    if action_normalisee.endswith("."):
        return action_normalisee
    return action_normalisee + "."


def construire_section_commandes_borne(
    definition: DefinitionTechniqueJeu,
    metadonnees: MetadonneesReadmeJeu,
) -> str:
    """Construit la section commandes borne.

    Args:
        definition: Definition technique du jeu.
        metadonnees: Metadonnees du jeu.

    Returns:
        Tableau Markdown des commandes borne.
    """

    commandes = metadonnees.commandes_borne or lire_commandes_borne_depuis_fichier(definition.dossier)
    if not commandes:
        commandes = (
            CommandeBorne(
                "Reference",
                "Consulter `bouton.txt` pour le mapping brut du jeu.",
            ),
        )

    lignes = [
        "| Commande | Action |",
        "| --- | --- |",
    ]
    for commande in commandes:
        lignes.append(f"| {commande.commande} | {commande.action} |")
    return "\n".join(lignes)


def construire_section_fichiers_importants(definition: DefinitionTechniqueJeu) -> str:
    """Construit la section listant les fichiers importants.

    Args:
        definition: Definition technique du jeu.

    Returns:
        Liste Markdown des fichiers importants.
    """

    lignes: list[str] = []
    for nom_fichier, description in FICHIERS_IMPORTANTS_DE_BASE:
        lignes.append(f"- `{nom_fichier}`: {description}")

    chemin_requirements = definition.dossier / "requirements.txt"
    if chemin_requirements.is_file():
        lignes.append("- `requirements.txt`: dependances Python specifiques au jeu.")

    for chemin_json in sorted(definition.dossier.glob("*.json")):
        lignes.append(f"- `{chemin_json.name}`: configuration supplementaire du jeu.")

    if (definition.dossier / "tests").is_dir():
        lignes.append("- `tests/`: tests locaux du jeu.")

    for nom_doc in NOMS_DOCS_LOCALES:
        if (definition.dossier / nom_doc).is_file():
            lignes.append(f"- `{nom_doc}`: documentation locale complementaire.")

    autres_docs = sorted(
        chemin.name
        for chemin in definition.dossier.glob("*.md")
        if chemin.name not in {NOM_README_NORMALISE, NOM_README_MINUSCULE, *NOMS_DOCS_LOCALES}
    )
    for nom_doc in autres_docs:
        lignes.append(f"- `{nom_doc}`: documentation locale additionnelle.")

    return "\n".join(lignes)


def construire_section_tests_et_validation(definition: DefinitionTechniqueJeu) -> str:
    """Construit la section tests et validation.

    Args:
        definition: Definition technique du jeu.

    Returns:
        Liste Markdown des validations a executer.
    """

    commande_test = " ".join(definition.commande_test_cible)
    lignes = [
        f"- Test cible du jeu: `{commande_test}`.",
        "- Validation globale de la borne: "
        "`TEST_INSTALLATION_SIMULATION=1 TEST_DEPLOIEMENT_SIMULATION=1 BORNE_MODE_TEST=1 ./scripts/tests/lancer_suite.sh`.",
    ]
    return "\n".join(lignes)


def construire_notes_maintenance_automatiques(definition: DefinitionTechniqueJeu) -> list[str]:
    """Construit les notes de maintenance deduites du dossier de jeu.

    Args:
        definition: Definition technique du jeu.

    Returns:
        Liste de notes de maintenance automatiques.
    """

    lignes: list[str] = []
    if definition.runtime == "java":
        lignes.append(
            "- La compilation passe par `./borne_arcade/compilation.sh` et par le wrapper Java commun de la borne."
        )
    elif definition.runtime == "python":
        lignes.append(
            "- Le lancement borne passe par le wrapper Python commun et doit rester compatible avec `python3`."
        )
    elif definition.runtime == "lua":
        lignes.append(
            "- Le lancement borne passe par le wrapper LOVE2D commun et doit rester compatible avec l execution depuis le dossier du jeu."
        )

    if (definition.dossier / "requirements.txt").is_file():
        lignes.append("- Les dependances specifiques sont centralisees dans `requirements.txt`.")

    if (definition.dossier / "tests").is_dir():
        lignes.append("- Des tests locaux existent dans `tests/` et doivent etre maintenus a jour.")

    for chemin_json in sorted(definition.dossier.glob("*.json")):
        lignes.append(f"- Surveiller `{chemin_json.name}` pour toute evolution de configuration.")

    if any((definition.dossier / nom).is_file() for nom in NOMS_DOCS_LOCALES):
        lignes.append("- Maintenir synchronises le README et la documentation locale complementaire du jeu.")

    return lignes


def dedoublonner_lignes(lignes: list[str]) -> list[str]:
    """Supprime les doublons en preservant l ordre initial.

    Args:
        lignes: Liste de lignes eventuellement dupliquees.

    Returns:
        Liste dedoublonnee.
    """

    resultat: list[str] = []
    deja_vues: set[str] = set()
    for ligne in lignes:
        if ligne not in deja_vues:
            deja_vues.add(ligne)
            resultat.append(ligne)
    return resultat


def construire_section_maintenance(
    definition: DefinitionTechniqueJeu,
    metadonnees: MetadonneesReadmeJeu,
) -> str:
    """Construit la section maintenance et evolution.

    Args:
        definition: Definition technique du jeu.
        metadonnees: Metadonnees editoriales du jeu.

    Returns:
        Liste Markdown des points de maintenance.
    """

    lignes: list[str] = []
    for particularite in metadonnees.particularites:
        lignes.append(f"- {particularite}")

    lignes.extend(construire_notes_maintenance_automatiques(definition))

    for note in metadonnees.notes_maintenance:
        lignes.append(f"- {note}")

    lignes = dedoublonner_lignes(lignes)
    if not lignes:
        lignes.append("- Aucune note de maintenance supplementaire.")
    return "\n".join(lignes)


def chemin_relatif_markdown(dossier_source: Path, destination: Path) -> str:
    """Calcule un chemin relatif compatible Markdown.

    Args:
        dossier_source: Dossier source du lien.
        destination: Fichier cible du lien.

    Returns:
        Chemin relatif en notation POSIX.
    """

    return Path(os.path.relpath(destination, dossier_source)).as_posix()


def construire_section_liens_associes(definition: DefinitionTechniqueJeu) -> str:
    """Construit la section de liens associes.

    Args:
        definition: Definition technique du jeu.

    Returns:
        Liste Markdown des liens utiles.
    """

    lignes: list[str] = []
    for libelle, chemin in LIENS_DOCUMENTATION_COMMUNE:
        lignes.append(f"- [{libelle}]({chemin_relatif_markdown(definition.dossier, chemin)}).")

    for nom_doc in NOMS_DOCS_LOCALES:
        chemin_doc = definition.dossier / nom_doc
        if chemin_doc.is_file():
            lignes.append(f"- [{nom_doc}]({nom_doc}).")

    return "\n".join(lignes)


def rendre_readme(
    template: str,
    definition: DefinitionTechniqueJeu,
    metadonnees: MetadonneesReadmeJeu,
) -> str:
    """Rend le contenu complet d un README de jeu.

    Args:
        template: Template source.
        definition: Definition technique du jeu.
        metadonnees: Metadonnees editoriales du jeu.

    Returns:
        README final normalise.
    """

    contexte = {
        "titre_affiche": metadonnees.titre_affiche,
        "objectif": metadonnees.resume,
        "runtime_et_lancement": construire_section_runtime_et_lancement(definition),
        "commandes_borne": construire_section_commandes_borne(definition, metadonnees),
        "fichiers_importants": construire_section_fichiers_importants(definition),
        "tests_et_validation": construire_section_tests_et_validation(definition),
        "maintenance_et_evolution": construire_section_maintenance(definition, metadonnees),
        "liens_associes": construire_section_liens_associes(definition),
    }
    return remplacer_placeholders(template, contexte).rstrip() + "\n"


def trouver_entree_exacte(dossier: Path, nom_fichier: str) -> Path | None:
    """Retourne une entree dont le nom respecte exactement la casse demandee.

    Args:
        dossier: Dossier a analyser.
        nom_fichier: Nom de fichier exact attendu.

    Returns:
        Chemin exact trouve, sinon `None`.
    """

    if not dossier.is_dir():
        return None

    for chemin in dossier.iterdir():
        if chemin.name == nom_fichier:
            return chemin
    return None


def normaliser_nom_readme(definition: DefinitionTechniqueJeu) -> None:
    """Renomme un `readme.md` minuscule vers `README.md` si necessaire.

    Args:
        definition: Definition technique du jeu.

    Returns:
        Aucun.
    """

    chemin_minuscule = trouver_entree_exacte(definition.dossier, NOM_README_MINUSCULE)
    chemin_normalise = trouver_entree_exacte(definition.dossier, NOM_README_NORMALISE)
    if chemin_minuscule is None:
        return

    if chemin_normalise is not None:
        chemin_minuscule.unlink()
        return

    chemin_temporaire = definition.dossier / "__tmp_readme_borne__.md"
    chemin_minuscule.rename(chemin_temporaire)
    chemin_temporaire.rename(definition.dossier / NOM_README_NORMALISE)


def verifier_ou_ecrire_readme(
    definition: DefinitionTechniqueJeu,
    contenu_attendu: str,
    mode_verification: bool,
) -> None:
    """Verifie ou ecrit un README genere.

    Args:
        definition: Definition technique du jeu.
        contenu_attendu: README rendu.
        mode_verification: `True` pour verifier sans ecrire.

    Returns:
        Aucun.

    Raises:
        ValueError: si le README n est pas conforme en mode verification.
    """

    chemin_readme = definition.dossier / NOM_README_NORMALISE
    chemin_readme_minuscule = trouver_entree_exacte(definition.dossier, NOM_README_MINUSCULE)
    chemin_readme_exact = trouver_entree_exacte(definition.dossier, NOM_README_NORMALISE)

    if mode_verification:
        if chemin_readme_minuscule is not None:
            raise ValueError(
                f"README non normalise en minuscule pour {definition.nom}: "
                f"{chemin_readme_minuscule.relative_to(RACINE_PROJET)}"
            )
        if chemin_readme_exact is None or not chemin_readme.is_file():
            raise ValueError(
                f"README absent pour {definition.nom}: {chemin_readme.relative_to(RACINE_PROJET)}"
            )
        contenu_existant = chemin_readme.read_text(encoding="utf-8")
        if contenu_existant != contenu_attendu:
            diff = "\n".join(
                difflib.unified_diff(
                    contenu_existant.splitlines(),
                    contenu_attendu.splitlines(),
                    fromfile=str(chemin_readme.relative_to(RACINE_PROJET)),
                    tofile=f"{chemin_readme.relative_to(RACINE_PROJET)} (genere)",
                    lineterm="",
                )
            )
            raise ValueError(f"README non a jour pour {definition.nom}.\n{diff}")
        return

    normaliser_nom_readme(definition)
    chemin_readme.write_text(contenu_attendu, encoding="utf-8")


def traiter_readmes(arguments: argparse.Namespace) -> int:
    """Execute la generation ou la verification des README.

    Args:
        arguments: Arguments de ligne de commande.

    Returns:
        Code retour du programme.
    """

    definitions = charger_definitions_techniques()
    metadonnees = charger_metadonnees_readme()
    verifier_bijection(definitions, metadonnees)
    template = charger_template()

    jeux = filtrer_jeux(definitions, metadonnees, arguments.jeu)
    for definition, metadonnees_jeu in jeux:
        contenu = rendre_readme(template, definition, metadonnees_jeu)
        verifier_ou_ecrire_readme(definition, contenu, arguments.verifier)

    if arguments.verifier:
        print("README jeux verifies: OK")
    else:
        print(f"README jeux generes: {len(jeux)}")
    return 0


def main() -> int:
    """Point d entree principal du script.

    Returns:
        Code retour du programme.
    """

    arguments = charger_arguments()
    try:
        return traiter_readmes(arguments)
    except ValueError as exception:
        afficher_erreur(
            str(exception),
            "Corrigez les metadonnees ou regenerez les README avec "
            "`python3 scripts/docs/generer_readme_jeux.py` puis relancez la verification.",
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
