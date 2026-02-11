"""Interface pygame du mode maintenance de la borne arcade."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Tuple

import pygame

from operations import (
    charger_configuration,
    creer_fichier_verrouillage,
    executer_operation,
    lister_operations,
)


COULEUR_FOND = (8, 12, 24)
COULEUR_TEXTE = (233, 239, 255)
COULEUR_SELECTION = (0, 191, 136)
COULEUR_ERREUR = (241, 98, 98)
COULEUR_SUCCES = (86, 193, 115)
MARGE_GAUCHE = 60
MARGE_HAUT = 40
ESPACEMENT_LIGNE = 42


def charger_parametres() -> Dict[str, object]:
    """Charge la configuration locale du mode maintenance.

    Args:
        Aucun.

    Returns:
        Dictionnaire de configuration fusionne avec les valeurs par defaut.
    """

    chemin_configuration = Path(__file__).resolve().parent / "config_maintenance.json"
    return charger_configuration(chemin_configuration)


def initialiser_fenetre(configuration: Dict[str, object]) -> pygame.Surface:
    """Initialise la fenetre pygame du mode maintenance.

    Args:
        configuration: Configuration chargee du mode maintenance.

    Returns:
        Surface principale de rendu.
    """

    section_fenetre = configuration.get("fenetre", {})
    largeur = int(section_fenetre.get("largeur", 1280))
    hauteur = int(section_fenetre.get("hauteur", 720))
    fenetre = pygame.display.set_mode((largeur, hauteur))
    pygame.display.set_caption("Mode maintenance borne")
    return fenetre


def dessiner_interface(
    fenetre: pygame.Surface,
    police_titre: pygame.font.Font,
    police_texte: pygame.font.Font,
    operations: List[Dict[str, str]],
    index_selection: int,
    message_statut: str,
    succes_operation: bool,
) -> None:
    """Dessine la page principale du mode maintenance.

    Args:
        fenetre: Surface principale.
        police_titre: Police du titre.
        police_texte: Police du contenu.
        operations: Liste des operations disponibles.
        index_selection: Index de l operation selectionnee.
        message_statut: Message de retour utilisateur.
        succes_operation: Etat de la derniere operation.

    Returns:
        Aucun.
    """

    fenetre.fill(COULEUR_FOND)

    titre = police_titre.render("Mode maintenance borne", True, COULEUR_TEXTE)
    fenetre.blit(titre, (MARGE_GAUCHE, MARGE_HAUT))

    aide = [
        "Joystick haut/bas: changer d operation",
        "Bouton J1A (touche F): executer",
        "Bouton J1C (touche H): verrouiller et quitter",
        "Echap: quitter sans reverrouillage",
    ]

    for index, ligne in enumerate(aide):
        rendu = police_texte.render(ligne, True, COULEUR_TEXTE)
        fenetre.blit(rendu, (MARGE_GAUCHE, MARGE_HAUT + 60 + index * 24))

    base_operations_y = MARGE_HAUT + 180
    for index, operation in enumerate(operations):
        couleur = COULEUR_SELECTION if index == index_selection else COULEUR_TEXTE
        etiquette = f"[{index + 1}] {operation['titre']} - {operation['description']}"
        rendu = police_texte.render(etiquette, True, couleur)
        fenetre.blit(rendu, (MARGE_GAUCHE, base_operations_y + index * ESPACEMENT_LIGNE))

    couleur_message = COULEUR_SUCCES if succes_operation else COULEUR_ERREUR
    rendu_message = police_texte.render(message_statut, True, couleur_message)
    fenetre.blit(rendu_message, (MARGE_GAUCHE, base_operations_y + len(operations) * ESPACEMENT_LIGNE + 30))


def gerer_evenement_touche(
    evenement: pygame.event.Event,
    operations: List[Dict[str, str]],
    index_selection: int,
    configuration: Dict[str, object],
) -> Tuple[int, str, bool, bool]:
    """Traite les touches clavier du mode maintenance.

    Args:
        evenement: Evenement clavier recu.
        operations: Liste des operations disponibles.
        index_selection: Index actuellement selectionne.
        configuration: Configuration chargee.

    Returns:
        Tuple (nouvel index, message, succes, quitter).
    """

    if evenement.key == pygame.K_UP:
        return (index_selection - 1) % len(operations), "Selection mise a jour.", True, False

    if evenement.key == pygame.K_DOWN:
        return (index_selection + 1) % len(operations), "Selection mise a jour.", True, False

    if evenement.key == pygame.K_f:
        operation = operations[index_selection]
        succes, message, journal = executer_operation(operation["id"], configuration)
        message_final = f"{message} Journal: {journal}"
        return index_selection, message_final, succes, False

    if evenement.key == pygame.K_h:
        chemin = creer_fichier_verrouillage(configuration)
        message = f"Mode maintenance reverrouille ({chemin.name})."
        return index_selection, message, True, True

    if evenement.key == pygame.K_ESCAPE:
        return index_selection, "Sortie du mode maintenance.", True, True

    return index_selection, "Touche non associee.", False, False


def boucle_principale(configuration: Dict[str, object]) -> int:
    """Execute la boucle principale pygame du mode maintenance.

    Args:
        configuration: Configuration chargee.

    Returns:
        Code de sortie processus (0 si succes).
    """

    pygame.init()
    fenetre = initialiser_fenetre(configuration)
    clock = pygame.time.Clock()

    section_fenetre = configuration.get("fenetre", {})
    fps = int(section_fenetre.get("fps", 30))

    police_titre = pygame.font.SysFont("dejavusans", 44)
    police_texte = pygame.font.SysFont("dejavusans", 24)

    operations = lister_operations()
    index_selection = 0
    message_statut = "Mode maintenance verrouillable avec H."
    succes_operation = True

    en_cours = True
    while en_cours:
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                en_cours = False
                break

            if evenement.type == pygame.KEYDOWN:
                index_selection, message_statut, succes_operation, quitter = gerer_evenement_touche(
                    evenement,
                    operations,
                    index_selection,
                    configuration,
                )
                if quitter:
                    en_cours = False
                    break

        dessiner_interface(
            fenetre,
            police_titre,
            police_texte,
            operations,
            index_selection,
            message_statut,
            succes_operation,
        )
        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()
    return 0


def main() -> int:
    """Point d entree principal du mode maintenance.

    Args:
        Aucun.

    Returns:
        Code de sortie shell.
    """

    configuration = charger_parametres()
    return boucle_principale(configuration)


if __name__ == "__main__":
    raise SystemExit(main())
