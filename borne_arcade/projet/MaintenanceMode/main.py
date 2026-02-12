"""Interface pygame du mode maintenance de la borne arcade."""

from __future__ import annotations

import queue
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

import pygame

from operations import (
    charger_configuration,
    creer_fichier_verrouillage,
    executer_operation,
    lister_operations,
)


TAILLES_PAR_DEFAUT = {
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
}

THEME_PAR_DEFAUT = {
    "fond_haut": (7, 14, 30),
    "fond_bas": (2, 6, 16),
    "panneau": (16, 24, 44),
    "panneau_bord": (56, 94, 140),
    "texte_principal": (233, 239, 255),
    "texte_secondaire": (174, 190, 226),
    "accent": (0, 208, 154),
    "erreur": (241, 98, 98),
    "succes": (106, 210, 134),
    "info": (88, 184, 255),
    "selection": (24, 48, 86),
}


@dataclass
class EtatInterface:
    """Conserve l etat mutable de l interface maintenance."""

    index_selection: int = 0
    message_statut: str = "Pret: selectionnez une operation puis appuyez sur F."
    succes_operation: bool = True
    operation_en_cours: bool = False
    titre_operation_en_cours: str = ""
    journal_visible: List[str] = field(default_factory=list)
    thread_operation: threading.Thread | None = None


def charger_parametres() -> Dict[str, object]:
    """Charge la configuration locale du mode maintenance.

    Args:
        Aucun.

    Returns:
        Dictionnaire de configuration fusionne avec les valeurs par defaut.
    """

    chemin_configuration = Path(__file__).resolve().parent / "config_maintenance.json"
    return charger_configuration(chemin_configuration)


def extraire_entier(section: Dict[str, object], cle: str, valeur_par_defaut: int) -> int:
    """Lit un entier de configuration en appliquant une valeur de secours.

    Args:
        section: Dictionnaire source.
        cle: Cle cible.
        valeur_par_defaut: Valeur de repli.

    Returns:
        Entier valide.
    """

    valeur = section.get(cle, valeur_par_defaut)
    try:
        return int(valeur)
    except (TypeError, ValueError):
        return valeur_par_defaut


def extraire_couleur(
    section_theme: Dict[str, object],
    cle: str,
    valeur_par_defaut: tuple[int, int, int],
) -> tuple[int, int, int]:
    """Lit une couleur RGB depuis la configuration.

    Args:
        section_theme: Dictionnaire theme.
        cle: Cle de la couleur.
        valeur_par_defaut: Couleur de repli.

    Returns:
        Tuple RGB valide.
    """

    valeur = section_theme.get(cle, valeur_par_defaut)
    if not isinstance(valeur, list) or len(valeur) != 3:
        return valeur_par_defaut

    composantes: List[int] = []
    for composante in valeur:
        try:
            entier = int(composante)
        except (TypeError, ValueError):
            return valeur_par_defaut
        composantes.append(max(0, min(255, entier)))
    return (composantes[0], composantes[1], composantes[2])


def charger_tailles_interface(configuration: Dict[str, object]) -> Dict[str, int]:
    """Charge les tailles d interface depuis la configuration.

    Args:
        configuration: Configuration chargee.

    Returns:
        Dictionnaire des tailles utilisees par l interface.
    """

    section_interface = configuration.get("interface", {})
    if not isinstance(section_interface, dict):
        section_interface = {}

    tailles: Dict[str, int] = {}
    for cle, valeur_par_defaut in TAILLES_PAR_DEFAUT.items():
        tailles[cle] = extraire_entier(section_interface, cle, valeur_par_defaut)
    return tailles


def charger_theme(configuration: Dict[str, object]) -> Dict[str, tuple[int, int, int]]:
    """Charge le theme graphique depuis la configuration.

    Args:
        configuration: Configuration chargee.

    Returns:
        Palette de couleurs RGB.
    """

    section_theme = configuration.get("theme", {})
    if not isinstance(section_theme, dict):
        section_theme = {}

    theme: Dict[str, tuple[int, int, int]] = {}
    for cle, valeur_par_defaut in THEME_PAR_DEFAUT.items():
        theme[cle] = extraire_couleur(section_theme, cle, valeur_par_defaut)
    return theme


def initialiser_fenetre(configuration: Dict[str, object]) -> pygame.Surface:
    """Initialise la fenetre pygame du mode maintenance.

    Args:
        configuration: Configuration chargee du mode maintenance.

    Returns:
        Surface principale de rendu.
    """

    section_fenetre = configuration.get("fenetre", {})
    if not isinstance(section_fenetre, dict):
        section_fenetre = {}

    largeur = extraire_entier(section_fenetre, "largeur", 1280)
    hauteur = extraire_entier(section_fenetre, "hauteur", 720)
    fenetre = pygame.display.set_mode((largeur, hauteur))
    pygame.display.set_caption("Mode maintenance borne")
    return fenetre


def initialiser_polices(tailles: Dict[str, int]) -> Dict[str, pygame.font.Font]:
    """Initialise les polices de l interface.

    Args:
        tailles: Parametres de tailles d interface.

    Returns:
        Dictionnaire de polices pygame.
    """

    return {
        "titre": pygame.font.SysFont("dejavusans", tailles["taille_police_titre"], bold=True),
        "texte": pygame.font.SysFont("dejavusans", tailles["taille_police_texte"]),
        "journal": pygame.font.SysFont("dejavusansmono", tailles["taille_police_journal"]),
    }


def creer_fond_degrade(
    dimension: tuple[int, int],
    couleur_haut: tuple[int, int, int],
    couleur_bas: tuple[int, int, int],
) -> pygame.Surface:
    """Genere une surface de fond avec degrade vertical.

    Args:
        dimension: Largeur et hauteur de la fenetre.
        couleur_haut: Couleur du haut.
        couleur_bas: Couleur du bas.

    Returns:
        Surface de fond pre-rendue.
    """

    largeur, hauteur = dimension
    surface = pygame.Surface((largeur, hauteur))
    hauteur_max = max(1, hauteur - 1)

    for ordonnee in range(hauteur):
        ratio = ordonnee / hauteur_max
        rouge = int(couleur_haut[0] * (1 - ratio) + couleur_bas[0] * ratio)
        vert = int(couleur_haut[1] * (1 - ratio) + couleur_bas[1] * ratio)
        bleu = int(couleur_haut[2] * (1 - ratio) + couleur_bas[2] * ratio)
        pygame.draw.line(surface, (rouge, vert, bleu), (0, ordonnee), (largeur, ordonnee))

    return surface


def dessiner_panneau(
    fenetre: pygame.Surface,
    rectangle: pygame.Rect,
    couleur_fond: tuple[int, int, int],
    couleur_bord: tuple[int, int, int],
    rayon_bordure: int,
) -> None:
    """Dessine un panneau arrondi avec bordure.

    Args:
        fenetre: Surface principale de rendu.
        rectangle: Zone du panneau.
        couleur_fond: Couleur interne.
        couleur_bord: Couleur de bordure.
        rayon_bordure: Rayon des angles.

    Returns:
        Aucun.
    """

    pygame.draw.rect(fenetre, couleur_fond, rectangle, border_radius=rayon_bordure)
    pygame.draw.rect(
        fenetre,
        couleur_bord,
        rectangle,
        width=2,
        border_radius=rayon_bordure,
    )


def tronquer_texte(police: pygame.font.Font, texte: str, largeur_max: int) -> str:
    """Tronque un texte pour respecter une largeur maximale.

    Args:
        police: Police utilisee pour le calcul.
        texte: Texte source.
        largeur_max: Largeur cible en pixels.

    Returns:
        Texte tronque si necessaire.
    """

    if police.size(texte)[0] <= largeur_max:
        return texte

    suffixe = "..."
    texte_actuel = texte
    while texte_actuel and police.size(texte_actuel + suffixe)[0] > largeur_max:
        texte_actuel = texte_actuel[:-1]
    return texte_actuel + suffixe


def recuperer_indicateur_animation(intervalle_ms: int) -> str:
    """Retourne un caractere d animation cyclique.

    Args:
        intervalle_ms: Duree d une frame d animation.

    Returns:
        Caractere representant l animation courante.
    """

    sequence = ["|", "/", "-", "\\"]
    index = (pygame.time.get_ticks() // max(50, intervalle_ms)) % len(sequence)
    return sequence[index]


def dessiner_entete(
    fenetre: pygame.Surface,
    rectangle: pygame.Rect,
    polices: Dict[str, pygame.font.Font],
    theme: Dict[str, tuple[int, int, int]],
    tailles: Dict[str, int],
    etat: EtatInterface,
) -> None:
    """Dessine l entete principal avec l etat d execution.

    Args:
        fenetre: Surface principale.
        rectangle: Zone de l entete.
        polices: Polices chargees.
        theme: Palette graphique.
        tailles: Tailles d interface.
        etat: Etat courant.

    Returns:
        Aucun.
    """

    dessiner_panneau(fenetre, rectangle, theme["panneau"], theme["panneau_bord"], tailles["rayon_bordure"])

    titre = polices["titre"].render("Mode maintenance borne", True, theme["texte_principal"])
    fenetre.blit(titre, (rectangle.x + 18, rectangle.y + 10))

    sous_titre = "Operations systeme executees en arriere-plan avec journal temps reel"
    rendu_sous_titre = polices["texte"].render(sous_titre, True, theme["texte_secondaire"])
    fenetre.blit(rendu_sous_titre, (rectangle.x + 18, rectangle.y + 60))

    if etat.operation_en_cours:
        indicateur = recuperer_indicateur_animation(tailles["intervalle_animation_ms"])
        texte_etat = f"{indicateur} EN COURS: {etat.titre_operation_en_cours}"
        couleur_etat = theme["info"]
    else:
        texte_etat = "PRET"
        couleur_etat = theme["succes"]

    rendu_etat = polices["texte"].render(texte_etat, True, couleur_etat)
    position_x = rectangle.right - rendu_etat.get_width() - 24
    fenetre.blit(rendu_etat, (position_x, rectangle.y + 36))


def dessiner_colonne_operations(
    fenetre: pygame.Surface,
    rectangle: pygame.Rect,
    polices: Dict[str, pygame.font.Font],
    theme: Dict[str, tuple[int, int, int]],
    tailles: Dict[str, int],
    operations: List[Dict[str, str]],
    etat: EtatInterface,
) -> None:
    """Dessine la colonne de selection des operations.

    Args:
        fenetre: Surface principale.
        rectangle: Zone operations.
        polices: Polices chargees.
        theme: Palette graphique.
        tailles: Tailles d interface.
        operations: Liste des operations.
        etat: Etat courant.

    Returns:
        Aucun.
    """

    dessiner_panneau(fenetre, rectangle, theme["panneau"], theme["panneau_bord"], tailles["rayon_bordure"])
    titre = polices["texte"].render("Operations", True, theme["accent"])
    fenetre.blit(titre, (rectangle.x + 16, rectangle.y + 12))

    zone_texte_x = rectangle.x + 16
    zone_texte_largeur = rectangle.width - 32
    base_y = rectangle.y + 54

    for index, operation in enumerate(operations):
        position_y = base_y + index * tailles["hauteur_ligne_operation"]
        ligne_rect = pygame.Rect(
            rectangle.x + 10,
            position_y - 4,
            rectangle.width - 20,
            tailles["hauteur_ligne_operation"] - 4,
        )

        if index == etat.index_selection:
            pygame.draw.rect(
                fenetre,
                theme["selection"],
                ligne_rect,
                border_radius=max(4, tailles["rayon_bordure"] - 6),
            )

        etiquette = f"[{index + 1}] {operation['titre']}"
        description = operation["description"]

        etiquette = tronquer_texte(polices["texte"], etiquette, zone_texte_largeur)
        description = tronquer_texte(polices["journal"], description, zone_texte_largeur)

        couleur_etiquette = theme["texte_principal"] if index == etat.index_selection else theme["texte_secondaire"]
        rendu_etiquette = polices["texte"].render(etiquette, True, couleur_etiquette)
        rendu_description = polices["journal"].render(description, True, theme["texte_secondaire"])

        fenetre.blit(rendu_etiquette, (zone_texte_x, position_y))
        fenetre.blit(rendu_description, (zone_texte_x, position_y + 24))


def dessiner_zone_journal(
    fenetre: pygame.Surface,
    rectangle: pygame.Rect,
    polices: Dict[str, pygame.font.Font],
    theme: Dict[str, tuple[int, int, int]],
    tailles: Dict[str, int],
    etat: EtatInterface,
) -> None:
    """Dessine la zone de journal temps reel.

    Args:
        fenetre: Surface principale.
        rectangle: Zone du journal.
        polices: Polices chargees.
        theme: Palette graphique.
        tailles: Tailles d interface.
        etat: Etat courant.

    Returns:
        Aucun.
    """

    dessiner_panneau(fenetre, rectangle, theme["panneau"], theme["panneau_bord"], tailles["rayon_bordure"])
    titre = polices["texte"].render("Journal temps reel", True, theme["accent"])
    fenetre.blit(titre, (rectangle.x + 16, rectangle.y + 12))

    nombre_lignes = max(1, tailles["nombre_lignes_journal"])
    lignes = etat.journal_visible[-nombre_lignes:]
    base_y = rectangle.y + 50

    for index, ligne in enumerate(lignes):
        largeur_disponible = rectangle.width - 28
        ligne_affichable = tronquer_texte(polices["journal"], ligne, largeur_disponible)
        rendu = polices["journal"].render(ligne_affichable, True, theme["texte_principal"])
        fenetre.blit(rendu, (rectangle.x + 14, base_y + index * tailles["hauteur_ligne_journal"]))


def dessiner_pied(
    fenetre: pygame.Surface,
    rectangle: pygame.Rect,
    polices: Dict[str, pygame.font.Font],
    theme: Dict[str, tuple[int, int, int]],
    tailles: Dict[str, int],
    etat: EtatInterface,
) -> None:
    """Dessine la barre de statut et les controles utilisateur.

    Args:
        fenetre: Surface principale.
        rectangle: Zone pied.
        polices: Polices chargees.
        theme: Palette graphique.
        tailles: Tailles d interface.
        etat: Etat courant.

    Returns:
        Aucun.
    """

    dessiner_panneau(fenetre, rectangle, theme["panneau"], theme["panneau_bord"], tailles["rayon_bordure"])
    controles = "Haut/Bas: selection | F: executer | H: reverrouiller+quitter | Echap: quitter"
    rendu_controles = polices["journal"].render(controles, True, theme["texte_secondaire"])
    fenetre.blit(rendu_controles, (rectangle.x + 14, rectangle.y + 10))

    couleur_statut = theme["succes"] if etat.succes_operation else theme["erreur"]
    largeur_max = rectangle.width - 28
    texte_statut = tronquer_texte(polices["texte"], etat.message_statut, largeur_max)
    rendu_statut = polices["texte"].render(texte_statut, True, couleur_statut)
    fenetre.blit(rendu_statut, (rectangle.x + 14, rectangle.y + 34))


def dessiner_interface(
    fenetre: pygame.Surface,
    fond: pygame.Surface,
    polices: Dict[str, pygame.font.Font],
    theme: Dict[str, tuple[int, int, int]],
    tailles: Dict[str, int],
    operations: List[Dict[str, str]],
    etat: EtatInterface,
) -> None:
    """Dessine la page principale du mode maintenance.

    Args:
        fenetre: Surface principale.
        fond: Surface de fond pre-rendue.
        polices: Polices chargees.
        theme: Palette graphique.
        tailles: Tailles d interface.
        operations: Liste des operations disponibles.
        etat: Etat courant.

    Returns:
        Aucun.
    """

    fenetre.blit(fond, (0, 0))
    largeur_fenetre, hauteur_fenetre = fenetre.get_size()

    marge_horizontale = tailles["marge_horizontale"]
    marge_verticale = tailles["marge_verticale"]
    hauteur_entete = tailles["hauteur_entete"]
    hauteur_pied = tailles["hauteur_pied"]
    espacement_colonnes = tailles["espacement_colonnes"]
    largeur_colonne_operations = tailles["largeur_colonne_operations"]

    largeur_zone = largeur_fenetre - 2 * marge_horizontale
    hauteur_zone = hauteur_fenetre - 2 * marge_verticale

    rectangle_entete = pygame.Rect(marge_horizontale, marge_verticale, largeur_zone, hauteur_entete)
    y_contenu = marge_verticale + hauteur_entete + espacement_colonnes
    hauteur_contenu = max(
        120,
        hauteur_zone - hauteur_entete - hauteur_pied - 2 * espacement_colonnes,
    )

    largeur_colonne_operations = min(largeur_colonne_operations, largeur_zone - 160)
    largeur_colonne_journal = largeur_zone - largeur_colonne_operations - espacement_colonnes

    rectangle_operations = pygame.Rect(
        marge_horizontale,
        y_contenu,
        largeur_colonne_operations,
        hauteur_contenu,
    )
    rectangle_journal = pygame.Rect(
        marge_horizontale + largeur_colonne_operations + espacement_colonnes,
        y_contenu,
        largeur_colonne_journal,
        hauteur_contenu,
    )
    rectangle_pied = pygame.Rect(
        marge_horizontale,
        hauteur_fenetre - marge_verticale - hauteur_pied,
        largeur_zone,
        hauteur_pied,
    )

    dessiner_entete(fenetre, rectangle_entete, polices, theme, tailles, etat)
    dessiner_colonne_operations(fenetre, rectangle_operations, polices, theme, tailles, operations, etat)
    dessiner_zone_journal(fenetre, rectangle_journal, polices, theme, tailles, etat)
    dessiner_pied(fenetre, rectangle_pied, polices, theme, tailles, etat)


def ajouter_ligne_journal(etat: EtatInterface, ligne: str, limite_lignes: int) -> None:
    """Ajoute une ligne au journal affiche en conservant une taille maximale.

    Args:
        etat: Etat courant de l interface.
        ligne: Ligne de journal a ajouter.
        limite_lignes: Nombre maximal de lignes conservees.

    Returns:
        Aucun.
    """

    etat.journal_visible.append(ligne)
    excedent = len(etat.journal_visible) - limite_lignes
    if excedent > 0:
        del etat.journal_visible[:excedent]


def executer_operation_en_arriere_plan(
    operation_id: str,
    configuration: Dict[str, object],
    file_journal: queue.Queue[str],
    file_resultat: queue.Queue[tuple[bool, str, Path]],
) -> None:
    """Execute une operation dans un thread dedie.

    Args:
        operation_id: Identifiant operation a executer.
        configuration: Configuration chargee.
        file_journal: File des lignes de log temps reel.
        file_resultat: File du resultat final.

    Returns:
        Aucun.
    """

    def pousser_ligne(message: str) -> None:
        """Alimente la file de logs depuis le worker.

        Args:
            message: Ligne de log issue de l operation.

        Returns:
            Aucun.
        """

        file_journal.put(message)

    succes, message, chemin_journal = executer_operation(operation_id, configuration, pousser_ligne)
    file_resultat.put((succes, message, chemin_journal))


def lancer_operation_asynchrone(
    operations: List[Dict[str, str]],
    configuration: Dict[str, object],
    etat: EtatInterface,
    file_journal: queue.Queue[str],
    file_resultat: queue.Queue[tuple[bool, str, Path]],
    limite_lignes: int,
) -> None:
    """Demarre l operation selectionnee en execution non bloquante.

    Args:
        operations: Liste des operations disponibles.
        configuration: Configuration chargee.
        etat: Etat courant.
        file_journal: File des logs temps reel.
        file_resultat: File de resultat.
        limite_lignes: Taille max du journal visible.

    Returns:
        Aucun.
    """

    if etat.operation_en_cours:
        etat.succes_operation = False
        etat.message_statut = "Une operation est deja en cours. Patientez avant d en lancer une nouvelle."
        return

    operation = operations[etat.index_selection]
    etat.operation_en_cours = True
    etat.titre_operation_en_cours = operation["titre"]
    etat.succes_operation = True
    etat.message_statut = f"Operation lancee: {operation['titre']}"
    ajouter_ligne_journal(etat, f"[INFO] Demarrage operation: {operation['titre']}", limite_lignes)

    thread_operation = threading.Thread(
        target=executer_operation_en_arriere_plan,
        args=(operation["id"], configuration, file_journal, file_resultat),
        daemon=True,
    )
    etat.thread_operation = thread_operation
    thread_operation.start()


def traiter_flux_asynchrones(
    etat: EtatInterface,
    file_journal: queue.Queue[str],
    file_resultat: queue.Queue[tuple[bool, str, Path]],
    limite_lignes: int,
) -> None:
    """Vide les files de logs/resultats vers l interface.

    Args:
        etat: Etat courant.
        file_journal: File de logs.
        file_resultat: File de resultats finaux.
        limite_lignes: Taille max du journal visible.

    Returns:
        Aucun.
    """

    while not file_journal.empty():
        ajouter_ligne_journal(etat, file_journal.get_nowait(), limite_lignes)

    while not file_resultat.empty():
        succes, message, chemin_journal = file_resultat.get_nowait()
        etat.operation_en_cours = False
        etat.titre_operation_en_cours = ""
        etat.succes_operation = succes
        etat.message_statut = f"{message} Journal: {chemin_journal}"


def gerer_evenement_touche(
    evenement: pygame.event.Event,
    operations: List[Dict[str, str]],
    configuration: Dict[str, object],
    etat: EtatInterface,
    file_journal: queue.Queue[str],
    file_resultat: queue.Queue[tuple[bool, str, Path]],
    limite_lignes: int,
) -> bool:
    """Traite les touches clavier du mode maintenance.

    Args:
        evenement: Evenement clavier recu.
        operations: Liste des operations disponibles.
        configuration: Configuration chargee.
        etat: Etat courant.
        file_journal: File des logs.
        file_resultat: File des resultats.
        limite_lignes: Taille max du journal visible.

    Returns:
        True si la boucle doit quitter, False sinon.
    """

    if evenement.key == pygame.K_UP:
        etat.index_selection = (etat.index_selection - 1) % len(operations)
        etat.message_statut = "Selection mise a jour."
        etat.succes_operation = True
        return False

    if evenement.key == pygame.K_DOWN:
        etat.index_selection = (etat.index_selection + 1) % len(operations)
        etat.message_statut = "Selection mise a jour."
        etat.succes_operation = True
        return False

    if evenement.key == pygame.K_f:
        lancer_operation_asynchrone(
            operations,
            configuration,
            etat,
            file_journal,
            file_resultat,
            limite_lignes,
        )
        return False

    if evenement.key == pygame.K_h:
        if etat.operation_en_cours:
            etat.succes_operation = False
            etat.message_statut = "Impossible de reverrouiller pendant une operation en cours."
            return False

        chemin = creer_fichier_verrouillage(configuration)
        etat.message_statut = f"Mode maintenance reverrouille ({chemin.name})."
        etat.succes_operation = True
        return True

    if evenement.key == pygame.K_ESCAPE:
        if etat.operation_en_cours:
            etat.succes_operation = False
            etat.message_statut = "Operation en cours: finissez-la avant de quitter."
            return False

        etat.message_statut = "Sortie du mode maintenance."
        etat.succes_operation = True
        return True

    etat.succes_operation = False
    etat.message_statut = "Touche non associee."
    return False


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
    if not isinstance(section_fenetre, dict):
        section_fenetre = {}
    fps = extraire_entier(section_fenetre, "fps", 30)

    tailles = charger_tailles_interface(configuration)
    theme = charger_theme(configuration)
    polices = initialiser_polices(tailles)
    fond = creer_fond_degrade(fenetre.get_size(), theme["fond_haut"], theme["fond_bas"])

    section_journal = configuration.get("journal", {})
    if not isinstance(section_journal, dict):
        section_journal = {}
    limite_lignes = max(40, extraire_entier(section_journal, "taille_max_lignes_interface", 240))

    operations = lister_operations()
    etat = EtatInterface()
    etat.journal_visible = ["Pret: F pour executer une operation, H pour reverrouiller."]

    file_journal: queue.Queue[str] = queue.Queue()
    file_resultat: queue.Queue[tuple[bool, str, Path]] = queue.Queue()

    en_cours = True
    while en_cours:
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                if etat.operation_en_cours:
                    etat.succes_operation = False
                    etat.message_statut = "Operation en cours: finissez-la avant de fermer la fenetre."
                    continue
                en_cours = False
                break

            if evenement.type == pygame.KEYDOWN:
                quitter = gerer_evenement_touche(
                    evenement,
                    operations,
                    configuration,
                    etat,
                    file_journal,
                    file_resultat,
                    limite_lignes,
                )
                if quitter:
                    en_cours = False
                    break

        traiter_flux_asynchrones(etat, file_journal, file_resultat, limite_lignes)
        dessiner_interface(fenetre, fond, polices, theme, tailles, operations, etat)
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
