"""Jeu Neon Sumo pour la borne arcade.

Boucle complete: ecran titre -> match BO3 -> resultat -> retour menu.
"""

from __future__ import annotations

import json
import os
import random
from dataclasses import dataclass
from math import sqrt
from pathlib import Path
from typing import Dict, Tuple

from logique import (
    Joueur,
    ParametresCombat,
    activer_bouclier,
    activer_dash,
    activer_ultime,
    appliquer_deplacement_inertiel,
    charger_ultime,
    decrementer_cooldowns,
    executer_bump,
    mettre_a_jour_bouclier,
    verifier_sortie_arene,
)


RACINE_JEU = Path(__file__).resolve().parent
FICHIER_CONFIG = RACINE_JEU / "config_jeu.json"
FICHIER_HIGHSCORE = RACINE_JEU / "highscore"
VARIABLE_ENV_MODE_TEST = "NEON_SUMO_MODE_TEST"
VALEUR_MODE_TEST_ACTIF = "1"
COULEUR_BLANC = (255, 255, 255)
COULEUR_JAUGE_FOND = (40, 40, 40)
COULEUR_JAUGE_REMPLISSAGE = (0, 255, 255)
LARGEUR_JAUGE_ULTIME = 200
HAUTEUR_JAUGE_ULTIME = 14
MARGE_JAUGE_GAUCHE = 40
MARGE_JAUGE_DROITE = 240
MARGE_BASSE_JAUGE = 36
HAUTEUR_LIBELLE_JAUGE = 10
pygame = None


@dataclass
class EntreeJoueur:
    """Mappe les controles borne vers les actions du jeu.

    Attributes:
        haut: Touche monter.
        bas: Touche descendre.
        gauche: Touche gauche.
        droite: Touche droite.
        dash: Touche dash.
        frein: Touche frein.
        bump: Touche bump.
        bouclier: Touche bouclier.
        taunt: Touche taunt.
        ultime: Touche ultime.
    """

    haut: int
    bas: int
    gauche: int
    droite: int
    dash: int
    frein: int
    bump: int
    bouclier: int
    taunt: int
    ultime: int


def mode_test_actif() -> bool:
    """Indique si un mode smoke test non interactif est active.

    Args:
        aucun.

    Returns:
        True si le mode test est actif, sinon False.
    """

    return os.environ.get(VARIABLE_ENV_MODE_TEST, "0") == VALEUR_MODE_TEST_ACTIF


def importer_pygame():
    """Charge pygame a la demande.

    Args:
        aucun.

    Returns:
        Module pygame charge.
    """

    try:
        import pygame as module_pygame
    except ModuleNotFoundError as erreur:
        raise RuntimeError("pygame est requis pour lancer Neon Sumo.") from erreur
    return module_pygame


def charger_configuration() -> Dict[str, object]:
    """Charge la configuration du jeu depuis un fichier JSON.

    Returns:
        Dictionnaire de configuration.
    """

    with FICHIER_CONFIG.open("r", encoding="utf-8") as flux:
        return json.load(flux)


def construire_parametres_combat(configuration: Dict[str, object]) -> ParametresCombat:
    """Construit les parametres de combat depuis la configuration.

    Args:
        configuration: Dictionnaire de configuration globale.

    Returns:
        Instance de ParametresCombat.
    """

    physique = configuration["physique"]
    gameplay = configuration["gameplay"]
    cooldowns = configuration["cooldowns"]
    ulti = configuration["ultime"]

    return ParametresCombat(
        acceleration=float(physique["acceleration"]),
        friction_base=float(physique["friction_base"]),
        friction_frein=float(physique["friction_frein"]),
        vitesse_max=float(physique["vitesse_max"]),
        impulsion_dash=float(gameplay["impulsion_dash"]),
        impulsion_bump=float(gameplay["impulsion_bump"]),
        rayon_bump=float(gameplay["rayon_bump"]),
        multiplicateur_bouclier=float(gameplay["reduction_knockback_bouclier"]),
        duree_bouclier=float(gameplay["duree_bouclier"]),
        cooldown_dash=float(cooldowns["dash"]),
        cooldown_bump=float(cooldowns["bump"]),
        cooldown_bouclier=float(cooldowns["bouclier"]),
        cooldown_taunt=float(cooldowns["taunt"]),
        gain_ultime_par_seconde=float(ulti["gain_par_seconde"]),
        gain_ultime_par_impact=float(ulti["gain_par_impact"]),
        rayon_ultime=float(ulti["rayon"]),
        impulsion_ultime=float(ulti["impulsion"]),
        delai_sortie_arene=float(gameplay["delai_sortie_arene"]),
    )


def creer_joueurs(configuration: Dict[str, object], largeur: int, hauteur: int) -> Tuple[Joueur, Joueur]:
    """Cree les deux joueurs en position de depart.

    Args:
        configuration: Configuration globale.
        largeur: Largeur de la fenetre.
        hauteur: Hauteur de la fenetre.

    Returns:
        Tuple (joueur_1, joueur_2).
    """

    rayon = float(configuration["physique"]["rayon_capsule"])
    distance_depart = float(configuration["physique"]["distance_depart"])
    centre_x = largeur / 2.0
    centre_y = hauteur / 2.0

    joueur_1 = Joueur(
        identifiant="J1",
        position_x=centre_x - distance_depart,
        position_y=centre_y,
        vitesse_x=0.0,
        vitesse_y=0.0,
        rayon=rayon,
        direction_x=1.0,
        direction_y=0.0,
        cooldowns={"dash": 0.0, "bump": 0.0, "bouclier": 0.0, "taunt": 0.0},
    )
    joueur_2 = Joueur(
        identifiant="J2",
        position_x=centre_x + distance_depart,
        position_y=centre_y,
        vitesse_x=0.0,
        vitesse_y=0.0,
        rayon=rayon,
        direction_x=-1.0,
        direction_y=0.0,
        cooldowns={"dash": 0.0, "bump": 0.0, "bouclier": 0.0, "taunt": 0.0},
    )
    return joueur_1, joueur_2


def charger_son(chemin_fichier: Path) -> pygame.mixer.Sound | None:
    """Charge un son de maniere tolerante aux erreurs.

    Args:
        chemin_fichier: Chemin du fichier audio.

    Returns:
        Un objet Sound si chargeable, sinon None.
    """

    if not chemin_fichier.exists() or chemin_fichier.stat().st_size == 0:
        return None
    try:
        return pygame.mixer.Sound(str(chemin_fichier))
    except pygame.error:
        return None


def jouer_son(son: pygame.mixer.Sound | None) -> None:
    """Joue un son optionnel.

    Args:
        son: Son charge, possiblement None.

    Returns:
        None.
    """

    if son is not None:
        son.play()


def lire_etat_touches(touches: pygame.key.ScancodeWrapper, entree: EntreeJoueur) -> Tuple[float, float]:
    """Convertit l etat clavier en direction normalisee.

    Args:
        touches: Etat courant des touches pygame.
        entree: Mapping des touches du joueur.

    Returns:
        Vecteur (x, y) de controle.
    """

    axe_x = 0.0
    axe_y = 0.0
    if touches[entree.gauche]:
        axe_x -= 1.0
    if touches[entree.droite]:
        axe_x += 1.0
    if touches[entree.haut]:
        axe_y -= 1.0
    if touches[entree.bas]:
        axe_y += 1.0
    return axe_x, axe_y


def dessiner_texte(
    surface: pygame.Surface,
    police: pygame.font.Font,
    texte: str,
    couleur: Tuple[int, int, int],
    position: Tuple[float, float],
    centrer: bool = True,
) -> None:
    """Dessine un texte avec alignement optionnel centre.

    Args:
        surface: Surface cible.
        police: Police a utiliser.
        texte: Contenu texte.
        couleur: Couleur RGB.
        position: Position cible.
        centrer: Active le centrage.

    Returns:
        None.
    """

    rendu = police.render(texte, True, couleur)
    rectangle = rendu.get_rect()
    if centrer:
        rectangle.center = (int(position[0]), int(position[1]))
    else:
        rectangle.topleft = (int(position[0]), int(position[1]))
    surface.blit(rendu, rectangle)


def dessiner_arene(
    surface: pygame.Surface,
    centre_x: float,
    centre_y: float,
    rayon: float,
    largeur_danger: float,
    couleur_interieur: Tuple[int, int, int],
    couleur_bord: Tuple[int, int, int],
    couleur_danger: Tuple[int, int, int],
) -> None:
    """Dessine l arene et la zone danger.

    Args:
        surface: Surface cible.
        centre_x: Centre X de l arene.
        centre_y: Centre Y de l arene.
        rayon: Rayon principal de l arene.
        largeur_danger: Largeur de la couronne danger.
        couleur_interieur: Couleur du disque interieur.
        couleur_bord: Couleur du contour principal.
        couleur_danger: Couleur de la zone danger.

    Returns:
        None.
    """

    centre = (int(centre_x), int(centre_y))
    rayon_entier = int(rayon)
    pygame.draw.circle(surface, couleur_interieur, centre, rayon_entier)
    pygame.draw.circle(surface, couleur_bord, centre, rayon_entier, 6)
    rayon_danger = max(8.0, rayon - largeur_danger)
    pygame.draw.circle(surface, couleur_danger, centre, int(rayon_danger), 3)


def dessiner_joueur(
    surface: pygame.Surface,
    joueur: Joueur,
    couleur_principale: Tuple[int, int, int],
    couleur_bouclier: Tuple[int, int, int],
) -> None:
    """Dessine une capsule de joueur.

    Args:
        surface: Surface cible.
        joueur: Joueur a dessiner.
        couleur_principale: Couleur de base.
        couleur_bouclier: Couleur du halo bouclier.

    Returns:
        None.
    """

    centre = (int(joueur.position_x), int(joueur.position_y))
    pygame.draw.circle(surface, couleur_principale, centre, int(joueur.rayon))
    pygame.draw.circle(surface, COULEUR_BLANC, centre, int(joueur.rayon), 2)

    if joueur.actif_bouclier:
        pygame.draw.circle(surface, couleur_bouclier, centre, int(joueur.rayon + 8), 3)


def dessiner_jauge(
    surface: pygame.Surface,
    petite_police: pygame.font.Font,
    couleur_ui: Tuple[int, int, int],
    position_x: int,
    position_y: int,
    valeur: float,
    label: str,
) -> None:
    """Dessine une jauge rectangulaire standard.

    Args:
        surface: Surface cible.
        petite_police: Police secondaire.
        couleur_ui: Couleur des libelles.
        position_x: Position X du coin haut-gauche.
        position_y: Position Y du coin haut-gauche.
        valeur: Valeur normalisee entre 0 et 1.
        label: Texte associe a la jauge.

    Returns:
        None.
    """

    valeur_normalisee = max(0.0, min(1.0, valeur))
    pygame.draw.rect(
        surface,
        COULEUR_JAUGE_FOND,
        pygame.Rect(position_x, position_y, LARGEUR_JAUGE_ULTIME, HAUTEUR_JAUGE_ULTIME),
    )
    pygame.draw.rect(
        surface,
        COULEUR_JAUGE_REMPLISSAGE,
        pygame.Rect(
            position_x,
            position_y,
            int(LARGEUR_JAUGE_ULTIME * valeur_normalisee),
            HAUTEUR_JAUGE_ULTIME,
        ),
    )
    pygame.draw.rect(
        surface,
        COULEUR_BLANC,
        pygame.Rect(position_x, position_y, LARGEUR_JAUGE_ULTIME, HAUTEUR_JAUGE_ULTIME),
        2,
    )
    dessiner_texte(
        surface,
        petite_police,
        label,
        couleur_ui,
        (position_x + LARGEUR_JAUGE_ULTIME / 2, position_y - HAUTEUR_LIBELLE_JAUGE),
    )


def dessiner_interface(
    surface: pygame.Surface,
    police: pygame.font.Font,
    petite_police: pygame.font.Font,
    largeur_surface: int,
    hauteur_surface: int,
    couleur_ui: Tuple[int, int, int],
    score_j1: int,
    score_j2: int,
    joueur_1: Joueur,
    joueur_2: Joueur,
    temps_restant: float,
) -> None:
    """Dessine l interface HUD.

    Args:
        surface: Surface cible.
        police: Police principale.
        petite_police: Police secondaire.
        largeur_surface: Largeur de la fenetre.
        hauteur_surface: Hauteur de la fenetre.
        couleur_ui: Couleur principale de l interface.
        score_j1: Score de manches J1.
        score_j2: Score de manches J2.
        joueur_1: Etat joueur 1.
        joueur_2: Etat joueur 2.
        temps_restant: Temps restant de manche.

    Returns:
        None.
    """

    dessiner_texte(surface, police, f"J1 {score_j1} - {score_j2} J2", couleur_ui, (largeur_surface / 2, 30))
    dessiner_texte(
        surface,
        petite_police,
        f"Temps: {max(0, int(temps_restant))}s",
        couleur_ui,
        (largeur_surface / 2, 58),
    )
    dessiner_jauge(
        surface,
        petite_police,
        couleur_ui,
        MARGE_JAUGE_GAUCHE,
        hauteur_surface - MARGE_BASSE_JAUGE,
        joueur_1.jauge_ultime,
        "Ultime J1",
    )
    dessiner_jauge(
        surface,
        petite_police,
        couleur_ui,
        largeur_surface - MARGE_JAUGE_DROITE,
        hauteur_surface - MARGE_BASSE_JAUGE,
        joueur_2.jauge_ultime,
        "Ultime J2",
    )


def incrementer_highscore(vainqueur: str) -> None:
    """Met a jour le fichier highscore local.

    Args:
        vainqueur: Identifiant du vainqueur final (J1 ou J2).

    Returns:
        None.
    """

    scores = {"J1": 0, "J2": 0}
    if FICHIER_HIGHSCORE.exists():
        for ligne in FICHIER_HIGHSCORE.read_text(encoding="utf-8").splitlines():
            if "-" not in ligne:
                continue
            nom, valeur = ligne.split("-", 1)
            if nom in scores:
                try:
                    scores[nom] = int(valeur)
                except ValueError:
                    scores[nom] = 0

    scores[vainqueur] += 1
    contenu = f"J1-{scores['J1']}\nJ2-{scores['J2']}\nAAA-0\n"
    FICHIER_HIGHSCORE.write_text(contenu, encoding="utf-8")


def gerer_entree_borne() -> Tuple[EntreeJoueur, EntreeJoueur]:
    """Construit les mappings de commandes borne pour les deux joueurs.

    Returns:
        Tuple des mappings (J1, J2).
    """

    j1 = EntreeJoueur(
        haut=pygame.K_UP,
        bas=pygame.K_DOWN,
        gauche=pygame.K_LEFT,
        droite=pygame.K_RIGHT,
        dash=pygame.K_f,
        frein=pygame.K_g,
        bump=pygame.K_h,
        bouclier=pygame.K_r,
        taunt=pygame.K_t,
        ultime=pygame.K_y,
    )
    j2 = EntreeJoueur(
        haut=pygame.K_o,
        bas=pygame.K_l,
        gauche=pygame.K_k,
        droite=pygame.K_m,
        dash=pygame.K_q,
        frein=pygame.K_s,
        bump=pygame.K_d,
        bouclier=pygame.K_a,
        taunt=pygame.K_z,
        ultime=pygame.K_e,
    )
    return j1, j2


def calculer_ia_attract(joueur: Joueur, centre_x: float, centre_y: float, rayon: float) -> Tuple[float, float]:
    """Calcule une direction simple d IA pour le mode attract.

    Args:
        joueur: Joueur pilote automatiquement.
        centre_x: Centre X arene.
        centre_y: Centre Y arene.
        rayon: Rayon courant arene.

    Returns:
        Direction (x, y) a appliquer.
    """

    vers_centre_x = centre_x - joueur.position_x
    vers_centre_y = centre_y - joueur.position_y
    distance_centre = sqrt(vers_centre_x * vers_centre_x + vers_centre_y * vers_centre_y)
    facteur_bord = 1.0 if distance_centre > rayon * 0.75 else 0.3
    alea_x = random.uniform(-0.7, 0.7)
    alea_y = random.uniform(-0.7, 0.7)
    return vers_centre_x * 0.01 * facteur_bord + alea_x, vers_centre_y * 0.01 * facteur_bord + alea_y


def reinitialiser_manche(
    configuration: Dict[str, object],
    largeur: int,
    hauteur: int,
    duree_manche: float,
    compte_a_rebours: float,
    rayon_depart: float,
) -> Tuple[Joueur, Joueur, float, float, float]:
    """Reinitialise les donnees dynamiques d une manche.

    Args:
        configuration: Configuration globale du jeu.
        largeur: Largeur fenetre.
        hauteur: Hauteur fenetre.
        duree_manche: Duree maximale d une manche.
        compte_a_rebours: Valeur de countdown initiale.
        rayon_depart: Rayon initial de l arene.

    Returns:
        Tuple (joueur_1, joueur_2, temps_restant, countdown, rayon_arene).
    """

    joueur_1, joueur_2 = creer_joueurs(configuration, largeur, hauteur)
    return joueur_1, joueur_2, duree_manche, compte_a_rebours, rayon_depart


def boucle_jeu() -> int:
    """Execute la boucle principale de Neon Sumo.

    Returns:
        Code de sortie du programme.
    """

    global pygame
    pygame = importer_pygame()
    configuration = charger_configuration()
    parametres = construire_parametres_combat(configuration)

    pygame.init()
    pygame.display.set_caption("Neon Sumo")

    largeur = int(configuration["ecran"]["largeur"])
    hauteur = int(configuration["ecran"]["hauteur"])
    plein_ecran = bool(configuration["ecran"]["plein_ecran"])
    flags = pygame.FULLSCREEN if plein_ecran else 0
    ecran = pygame.display.set_mode((largeur, hauteur), flags)

    horloge = pygame.time.Clock()
    fps_cible = int(configuration["performance"]["fps"])

    police = pygame.font.SysFont("DejaVu Sans", 32)
    petite_police = pygame.font.SysFont("DejaVu Sans", 20)

    j1_controles, j2_controles = gerer_entree_borne()

    try:
        pygame.mixer.init()
    except pygame.error:
        pass

    sons = {
        "dash": charger_son(RACINE_JEU / "assets/sons/dash.mp3"),
        "bump": charger_son(RACINE_JEU / "assets/sons/bump.mp3"),
        "bouclier": charger_son(RACINE_JEU / "assets/sons/bouclier.mp3"),
        "taunt": charger_son(RACINE_JEU / "assets/sons/taunt.mp3"),
        "ultime": charger_son(RACINE_JEU / "assets/sons/ultime.mp3"),
        "elimination": charger_son(RACINE_JEU / "assets/sons/elimination.mp3"),
    }

    etat = "titre"
    inactif = 0.0
    score_j1 = 0
    score_j2 = 0
    vainqueur_match = ""

    couleurs = configuration["couleurs"]
    couleur_fond = tuple(couleurs["fond"])
    couleur_ui = tuple(couleurs["ui"])
    couleur_titre = (0, 255, 255)
    couleur_texte_information = COULEUR_BLANC
    couleur_texte_secondaire = (190, 190, 190)
    couleur_texte_attract = (255, 255, 0)
    couleur_arene_interieur = tuple(couleurs["arene_interieur"])
    couleur_arene_bord = tuple(couleurs["arene_bord"])
    couleur_arene_danger = tuple(couleurs["arene_danger"])
    couleur_joueur_1 = tuple(couleurs["joueur_1"])
    couleur_joueur_2 = tuple(couleurs["joueur_2"])
    couleur_bouclier = tuple(couleurs["bouclier"])

    match = configuration["match"]
    arene = configuration["arene"]
    ux = configuration["ux"]
    duree_manche = float(match["duree_max_manche"])
    victoires_pour_gagner = int(match["victoires_pour_gagner"])
    compte_a_rebours_initial = float(match["compte_a_rebours"])
    duree_ecran_resultat = float(match["duree_ecran_resultat"])
    duree_ecran_fin = float(match["duree_ecran_fin"])
    delai_attract = float(ux["delai_attract"])
    countdown_attract_initial = 1.5

    centre_x = largeur / 2.0
    centre_y = hauteur / 2.0
    rayon_depart = float(arene["rayon_depart"])
    rayon_min = float(arene["rayon_min"])
    vitesse_retrecissement = float(arene["vitesse_retrecissement"])
    multiplicateur_sudden_death = float(arene["multiplicateur_sudden_death"])
    largeur_danger = float(arene["largeur_zone_danger"])

    joueur_1, joueur_2, temps_restant, countdown, rayon_arene = reinitialiser_manche(
        configuration,
        largeur,
        hauteur,
        duree_manche,
        compte_a_rebours_initial,
        rayon_depart,
    )
    dernier_vainqueur_manche = ""

    while True:
        delta_temps = horloge.tick(fps_cible) / 1000.0
        quitter = False
        touches_juste_appuyees: set[int] = set()
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                quitter = True
            elif evenement.type == pygame.KEYDOWN:
                touches_juste_appuyees.add(evenement.key)

        if quitter:
            pygame.quit()
            return 0

        touches = pygame.key.get_pressed()

        if touches_juste_appuyees:
            inactif = 0.0
        else:
            inactif += delta_temps

        ecran.fill(couleur_fond)
        appui_dash_global = (j1_controles.dash in touches_juste_appuyees) or (j2_controles.dash in touches_juste_appuyees)
        appui_ultime_global = (j1_controles.ultime in touches_juste_appuyees) or (j2_controles.ultime in touches_juste_appuyees)

        if etat == "titre":
            dessiner_texte(ecran, police, "NEON SUMO", couleur_titre, (centre_x, hauteur * 0.33))
            dessiner_texte(
                ecran,
                petite_police,
                "B1: Start | B6: Retour menu",
                couleur_texte_information,
                (centre_x, hauteur * 0.43),
            )
            dessiner_texte(
                ecran,
                petite_police,
                "Mode attract auto en 30s",
                couleur_texte_secondaire,
                (centre_x, hauteur * 0.48),
            )

            if appui_dash_global:
                score_j1 = 0
                score_j2 = 0
                joueur_1, joueur_2, temps_restant, countdown, rayon_arene = reinitialiser_manche(
                    configuration,
                    largeur,
                    hauteur,
                    duree_manche,
                    compte_a_rebours_initial,
                    rayon_depart,
                )
                etat = "compte_a_rebours"

            if appui_ultime_global:
                pygame.quit()
                return 0

            if inactif >= delai_attract:
                score_j1 = 0
                score_j2 = 0
                joueur_1, joueur_2, temps_restant, countdown, rayon_arene = reinitialiser_manche(
                    configuration,
                    largeur,
                    hauteur,
                    duree_manche,
                    compte_a_rebours_initial,
                    rayon_depart,
                )
                countdown = countdown_attract_initial
                etat = "attract"

        elif etat in {"compte_a_rebours", "attract", "manche"}:
            if etat == "compte_a_rebours":
                countdown -= delta_temps
                dessiner_texte(
                    ecran,
                    police,
                    f"{max(1, int(countdown) + 1)}",
                    couleur_texte_information,
                    (centre_x, hauteur * 0.2),
                )
                if countdown <= 0.0:
                    etat = "manche"

            if etat == "attract":
                countdown -= delta_temps
                dessiner_texte(
                    ecran,
                    petite_police,
                    "MODE ATTRACT - B1 pour jouer",
                    couleur_texte_attract,
                    (centre_x, 28),
                )
                if appui_dash_global:
                    score_j1 = 0
                    score_j2 = 0
                    joueur_1, joueur_2, temps_restant, countdown, rayon_arene = reinitialiser_manche(
                        configuration,
                        largeur,
                        hauteur,
                        duree_manche,
                        compte_a_rebours_initial,
                        rayon_depart,
                    )
                    etat = "compte_a_rebours"
                    continue
                if countdown <= 0.0:
                    etat = "manche"

            if etat in {"manche", "attract"}:
                en_manche = etat == "manche"
                if en_manche:
                    axe_j1 = lire_etat_touches(touches, j1_controles)
                    axe_j2 = lire_etat_touches(touches, j2_controles)
                else:
                    axe_j1 = calculer_ia_attract(joueur_1, centre_x, centre_y, rayon_arene)
                    axe_j2 = calculer_ia_attract(joueur_2, centre_x, centre_y, rayon_arene)

                frein_j1 = bool(touches[j1_controles.frein]) if en_manche else False
                frein_j2 = bool(touches[j2_controles.frein]) if en_manche else False

                appliquer_deplacement_inertiel(
                    joueur_1,
                    axe_j1[0],
                    axe_j1[1],
                    frein_j1,
                    delta_temps,
                    parametres,
                )
                appliquer_deplacement_inertiel(
                    joueur_2,
                    axe_j2[0],
                    axe_j2[1],
                    frein_j2,
                    delta_temps,
                    parametres,
                )

                decrementer_cooldowns(joueur_1, delta_temps)
                decrementer_cooldowns(joueur_2, delta_temps)
                mettre_a_jour_bouclier(joueur_1, delta_temps)
                mettre_a_jour_bouclier(joueur_2, delta_temps)
                charger_ultime(joueur_1, delta_temps, parametres)
                charger_ultime(joueur_2, delta_temps, parametres)

                if en_manche:
                    j1_dash_presse = j1_controles.dash in touches_juste_appuyees
                    j2_dash_presse = j2_controles.dash in touches_juste_appuyees
                    j1_bump_presse = j1_controles.bump in touches_juste_appuyees
                    j2_bump_presse = j2_controles.bump in touches_juste_appuyees
                    j1_bouclier_presse = j1_controles.bouclier in touches_juste_appuyees
                    j2_bouclier_presse = j2_controles.bouclier in touches_juste_appuyees
                    j1_ultime_presse = j1_controles.ultime in touches_juste_appuyees
                    j2_ultime_presse = j2_controles.ultime in touches_juste_appuyees
                    j1_taunt_presse = j1_controles.taunt in touches_juste_appuyees
                    j2_taunt_presse = j2_controles.taunt in touches_juste_appuyees

                    if j1_dash_presse and activer_dash(joueur_1, parametres):
                        jouer_son(sons["dash"])
                    if j2_dash_presse and activer_dash(joueur_2, parametres):
                        jouer_son(sons["dash"])

                    if j1_bump_presse and executer_bump(joueur_1, joueur_2, parametres):
                        jouer_son(sons["bump"])
                    if j2_bump_presse and executer_bump(joueur_2, joueur_1, parametres):
                        jouer_son(sons["bump"])

                    if j1_bouclier_presse and activer_bouclier(joueur_1, parametres):
                        jouer_son(sons["bouclier"])
                    if j2_bouclier_presse and activer_bouclier(joueur_2, parametres):
                        jouer_son(sons["bouclier"])

                    if j1_ultime_presse and activer_ultime(joueur_1, joueur_2, parametres):
                        jouer_son(sons["ultime"])
                    if j2_ultime_presse and activer_ultime(joueur_2, joueur_1, parametres):
                        jouer_son(sons["ultime"])

                    if j1_taunt_presse:
                        jouer_son(sons["taunt"])
                    if j2_taunt_presse:
                        jouer_son(sons["taunt"])

                temps_restant -= delta_temps
                multiplicateur = multiplicateur_sudden_death if temps_restant <= 0.0 else 1.0
                rayon_arene = max(rayon_min, rayon_arene - vitesse_retrecissement * multiplicateur * delta_temps)

                elimine_j1 = verifier_sortie_arene(joueur_1, centre_x, centre_y, rayon_arene, delta_temps, parametres)
                elimine_j2 = verifier_sortie_arene(joueur_2, centre_x, centre_y, rayon_arene, delta_temps, parametres)

                dessiner_arene(
                    ecran,
                    centre_x,
                    centre_y,
                    rayon_arene,
                    largeur_danger,
                    couleur_arene_interieur,
                    couleur_arene_bord,
                    couleur_arene_danger,
                )
                dessiner_joueur(
                    ecran,
                    joueur_1,
                    couleur_joueur_1,
                    couleur_bouclier,
                )
                dessiner_joueur(
                    ecran,
                    joueur_2,
                    couleur_joueur_2,
                    couleur_bouclier,
                )
                dessiner_interface(
                    ecran,
                    police,
                    petite_police,
                    largeur,
                    hauteur,
                    couleur_ui,
                    score_j1,
                    score_j2,
                    joueur_1,
                    joueur_2,
                    temps_restant,
                )

                if elimine_j1 or elimine_j2:
                    jouer_son(sons["elimination"])
                    if elimine_j1 and not elimine_j2:
                        score_j2 += 1
                        vainqueur_manche = "J2"
                    elif elimine_j2 and not elimine_j1:
                        score_j1 += 1
                        vainqueur_manche = "J1"
                    else:
                        vainqueur_manche = "Egalite"

                    if score_j1 >= victoires_pour_gagner:
                        vainqueur_match = "J1"
                        incrementer_highscore(vainqueur_match)
                        etat = "fin_match"
                        countdown = duree_ecran_fin
                    elif score_j2 >= victoires_pour_gagner:
                        vainqueur_match = "J2"
                        incrementer_highscore(vainqueur_match)
                        etat = "fin_match"
                        countdown = duree_ecran_fin
                    else:
                        etat = "resultat_manche"
                        countdown = duree_ecran_resultat
                    dernier_vainqueur_manche = vainqueur_manche

        elif etat == "resultat_manche":
            countdown -= delta_temps
            dessiner_texte(
                ecran,
                police,
                f"Manche: {dernier_vainqueur_manche}",
                couleur_texte_information,
                (centre_x, hauteur * 0.4),
            )
            dessiner_texte(
                ecran,
                petite_police,
                f"Score {score_j1}-{score_j2}",
                couleur_texte_information,
                (centre_x, hauteur * 0.5),
            )
            if countdown <= 0.0:
                joueur_1, joueur_2, temps_restant, countdown, rayon_arene = reinitialiser_manche(
                    configuration,
                    largeur,
                    hauteur,
                    duree_manche,
                    compte_a_rebours_initial,
                    rayon_depart,
                )
                etat = "compte_a_rebours"

        elif etat == "fin_match":
            countdown -= delta_temps
            dessiner_texte(ecran, police, f"Victoire {vainqueur_match}", couleur_titre, (centre_x, hauteur * 0.35))
            dessiner_texte(
                ecran,
                petite_police,
                "B1: Revanche  |  B6: Menu",
                couleur_texte_information,
                (centre_x, hauteur * 0.47),
            )
            if appui_dash_global:
                score_j1 = 0
                score_j2 = 0
                joueur_1, joueur_2, temps_restant, countdown, rayon_arene = reinitialiser_manche(
                    configuration,
                    largeur,
                    hauteur,
                    duree_manche,
                    compte_a_rebours_initial,
                    rayon_depart,
                )
                etat = "compte_a_rebours"
            if appui_ultime_global:
                etat = "titre"
            if countdown <= 0.0:
                etat = "titre"

        pygame.display.flip()


def main() -> None:
    """Point d entree du jeu Neon Sumo.

    Args:
        aucun.

    Returns:
        None.
    """

    if mode_test_actif():
        raise SystemExit(0)
    code = boucle_jeu()
    raise SystemExit(code)


if __name__ == "__main__":
    main()
