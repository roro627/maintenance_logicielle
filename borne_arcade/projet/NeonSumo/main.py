"""Jeu Neon Sumo pour la borne arcade.

Boucle complete: ecran titre -> match BO3 -> resultat -> retour menu.
"""

from __future__ import annotations

import json
import os
import random
from dataclasses import dataclass
from math import atan2, cos, pi, sin, sqrt
from pathlib import Path
from typing import Dict, Tuple

from logique import (
    EtatStyleJoueur,
    Joueur,
    ParametresCombat,
    ParametresStyle,
    activer_bouclier,
    activer_dash,
    activer_ultime,
    appliquer_deplacement_inertiel,
    charger_ultime,
    decrementer_cooldowns,
    enregistrer_impact_style,
    executer_bump,
    mettre_a_jour_etat_style,
    mettre_a_jour_sauvetage_bord,
    mettre_a_jour_bouclier,
    reinitialiser_etat_style,
    resoudre_collision_capsules,
    tenter_esquive_proche,
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
SEUIL_NORME_DIRECTION = 1e-18
DUREE_GEL_IMPACT_SECONDES = 0.04
DUREE_FLASH_IMPACT_SECONDES = 0.12
INTENSITE_FLASH_DASH = 85
INTENSITE_FLASH_BUMP = 130
INTENSITE_FLASH_ULTIME = 170
NOMBRE_PARTICULES_DASH = 10
NOMBRE_PARTICULES_BUMP = 16
NOMBRE_PARTICULES_ULTIME = 24
VITESSE_PARTICULE_MIN = 130.0
VITESSE_PARTICULE_MAX = 360.0
DUREE_PARTICULE_MIN_SECONDES = 0.12
DUREE_PARTICULE_MAX_SECONDES = 0.28
TAILLE_PARTICULE_MIN = 2
TAILLE_PARTICULE_MAX = 5
ANGLE_PARTICULE_DEMI_OUVERTURE = 0.45
FREINAGE_PARTICULES = 5.0
LARGEUR_INDICATEUR_COMPETENCE = 56
HAUTEUR_INDICATEUR_COMPETENCE = 18
MARGE_INTERIEURE_INDICATEUR = 2
ESPACEMENT_INDICATEUR_COMPETENCE = 10
DECALAGE_VERTICAL_INDICATEURS = 68
COULEUR_INDICATEUR_FOND = (30, 30, 40)
COULEUR_INDICATEUR_TEXTE = (240, 240, 248)
COULEUR_INDICATEUR_DASH = (0, 220, 255)
COULEUR_INDICATEUR_BUMP = (255, 100, 130)
COULEUR_INDICATEUR_BOUCLIER = (255, 220, 110)
COULEUR_FLASH_DASH = (160, 255, 255)
COULEUR_FLASH_BUMP = (255, 170, 170)
COULEUR_FLASH_ULTIME = (255, 255, 255)
COULEUR_PARTICULE_DASH = (80, 245, 255)
COULEUR_PARTICULE_BUMP = (255, 130, 130)
COULEUR_PARTICULE_ULTIME = (255, 235, 160)
COULEUR_STYLE_J1 = (40, 220, 255)
COULEUR_STYLE_J2 = (255, 120, 235)
COULEUR_STYLE_FOND = (18, 18, 28, 170)
COULEUR_STYLE_MESSAGE = (255, 245, 170)
COULEUR_STYLE_COMBO = (255, 140, 80)
RAYON_MINI_PULSE_STYLE = 6
RAYON_MAX_PULSE_STYLE = 12
EPAISSEUR_PULSE_STYLE = 2
OPACITE_GLOW_NEON_MAX = 190
EPAISSEUR_GLOW_NEON = 3
NOMBRE_COUCHES_GLOW_NEON = 5
LARGEUR_PANNEAU_STYLE = 280
HAUTEUR_PANNEAU_STYLE = 86
MARGE_HAUTE_PANNEAU_STYLE = 82
MARGE_LATERALE_PANNEAU_STYLE = 28
EPAISSEUR_BORD_PANNEAU_STYLE = 2
ESPACEMENT_LIGNES_ELECTRIQUES = 2.0
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


@dataclass
class ParticuleImpact:
    """Represente une particule de feedback visuel.

    Attributes:
        position_x: Position X de la particule.
        position_y: Position Y de la particule.
        vitesse_x: Vitesse X de la particule.
        vitesse_y: Vitesse Y de la particule.
        duree_totale: Duree de vie initiale.
        temps_restant: Duree de vie restante.
        taille: Rayon de rendu.
        couleur: Couleur RGB de base.
    """

    position_x: float
    position_y: float
    vitesse_x: float
    vitesse_y: float
    duree_totale: float
    temps_restant: float
    taille: int
    couleur: Tuple[int, int, int]


@dataclass
class EtatFeedbackCombat:
    """Contient les effets temporaires de hit feedback.

    Attributes:
        gel_restant: Duree de freeze frame restante.
        flash_restant: Duree de flash ecran restante.
        flash_intensite_max: Intensite alpha maximale du flash.
        couleur_flash: Couleur RGB du flash.
    """

    gel_restant: float = 0.0
    flash_restant: float = 0.0
    flash_intensite_max: float = 0.0
    couleur_flash: Tuple[int, int, int] = COULEUR_FLASH_ULTIME


@dataclass
class ParametresAreneNeon:
    """Regroupe les parametres visuels de l arene neon.

    Attributes:
        vitesse_oscillation: Vitesse de pulsation du glow.
        vitesse_rotation_lignes: Vitesse de rotation des lignes electriques.
        intensite_glow_base: Intensite de base du glow.
        intensite_glow_impact: Sur-intensite appliquee apres impact.
        opacite_lignes_base: Opacite de base des lignes electriques.
        opacite_lignes_impact: Sur-opacite des lignes sur impact.
        nombre_lignes_electriques: Nombre de lignes electriques.
        longueur_lignes_min: Longueur minimale d une ligne.
        longueur_lignes_max: Longueur maximale d une ligne.
        amplitude_jitter_lignes: Jitter transversal des lignes.
        decroissance_energie_impact: Vitesse de retour au calme apres impact.
        gain_impact_dash: Gain energie arene sur dash.
        gain_impact_bump: Gain energie arene sur bump.
        gain_impact_ultime: Gain energie arene sur ultime.
    """

    vitesse_oscillation: float
    vitesse_rotation_lignes: float
    intensite_glow_base: float
    intensite_glow_impact: float
    opacite_lignes_base: float
    opacite_lignes_impact: float
    nombre_lignes_electriques: int
    longueur_lignes_min: float
    longueur_lignes_max: float
    amplitude_jitter_lignes: float
    decroissance_energie_impact: float
    gain_impact_dash: float
    gain_impact_bump: float
    gain_impact_ultime: float


@dataclass
class EtatAreneNeon:
    """Contient l etat temporel de l arene neon.

    Attributes:
        phase_animation: Phase continue des animations.
        energie_impact: Energie residuelle des impacts (0..1).
    """

    phase_animation: float = 0.0
    energie_impact: float = 0.0


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
        coefficient_rebond_collision=float(physique.get("coefficient_rebond_collision", 0.65)),
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


def construire_parametres_style(configuration: Dict[str, object]) -> ParametresStyle:
    """Construit les parametres du systeme de style.

    Args:
        configuration: Dictionnaire de configuration globale.

    Returns:
        ParametresStyle initialises.
    """

    style = configuration.get("style", {})
    return ParametresStyle(
        fenetre_combo=float(style.get("fenetre_combo", 2.4)),
        bonus_combo_par_niveau=int(style.get("bonus_combo_par_niveau", 4)),
        points_impact=int(style.get("points_impact", 16)),
        points_esquive=int(style.get("points_esquive", 20)),
        points_sauvetage=int(style.get("points_sauvetage", 24)),
        distance_esquive=float(style.get("distance_esquive", 70.0)),
        cooldown_esquive=float(style.get("cooldown_esquive", 1.0)),
        marge_sauvetage=float(style.get("marge_sauvetage", 20.0)),
        duree_affichage_action=float(style.get("duree_affichage_action", 1.1)),
    )


def construire_parametres_arene_neon(configuration: Dict[str, object]) -> ParametresAreneNeon:
    """Construit les parametres visuels de l arene neon.

    Args:
        configuration: Dictionnaire de configuration globale.

    Returns:
        ParametresAreneNeon initialises.
    """

    effets = configuration.get("effets_arene", {})
    return ParametresAreneNeon(
        vitesse_oscillation=float(effets.get("vitesse_oscillation", 4.6)),
        vitesse_rotation_lignes=float(effets.get("vitesse_rotation_lignes", 1.4)),
        intensite_glow_base=float(effets.get("intensite_glow_base", 0.48)),
        intensite_glow_impact=float(effets.get("intensite_glow_impact", 0.8)),
        opacite_lignes_base=float(effets.get("opacite_lignes_base", 0.45)),
        opacite_lignes_impact=float(effets.get("opacite_lignes_impact", 0.4)),
        nombre_lignes_electriques=int(effets.get("nombre_lignes_electriques", 18)),
        longueur_lignes_min=float(effets.get("longueur_lignes_min", 8.0)),
        longueur_lignes_max=float(effets.get("longueur_lignes_max", 24.0)),
        amplitude_jitter_lignes=float(effets.get("amplitude_jitter_lignes", 6.0)),
        decroissance_energie_impact=float(effets.get("decroissance_energie_impact", 1.2)),
        gain_impact_dash=float(effets.get("gain_impact_dash", 0.1)),
        gain_impact_bump=float(effets.get("gain_impact_bump", 0.18)),
        gain_impact_ultime=float(effets.get("gain_impact_ultime", 0.28)),
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


def normaliser_direction(direction_x: float, direction_y: float) -> Tuple[float, float]:
    """Normalise une direction 2D.

    Args:
        direction_x: Composante X.
        direction_y: Composante Y.

    Returns:
        Tuple (x, y) normalise, ou (1, 0) si la direction est nulle.
    """

    norme_carre = direction_x * direction_x + direction_y * direction_y
    if norme_carre <= SEUIL_NORME_DIRECTION:
        return 1.0, 0.0
    inverse_norme = 1.0 / sqrt(norme_carre)
    return direction_x * inverse_norme, direction_y * inverse_norme


def ajouter_particules_directionnelles(
    particules: list[ParticuleImpact],
    origine_x: float,
    origine_y: float,
    direction_x: float,
    direction_y: float,
    couleur: Tuple[int, int, int],
    nombre: int,
    multiplicateur_vitesse: float = 1.0,
) -> None:
    """Ajoute des particules projetees selon une direction.

    Args:
        particules: Liste de particules a enrichir.
        origine_x: Origine X des particules.
        origine_y: Origine Y des particules.
        direction_x: Direction principale X.
        direction_y: Direction principale Y.
        couleur: Couleur RGB de la gerbe.
        nombre: Nombre de particules a creer.
        multiplicateur_vitesse: Facteur de vitesse applique a la gerbe.

    Returns:
        None.
    """

    direction_x, direction_y = normaliser_direction(direction_x, direction_y)
    angle_central = atan2(direction_y, direction_x)
    for _ in range(nombre):
        angle = angle_central + random.uniform(-ANGLE_PARTICULE_DEMI_OUVERTURE, ANGLE_PARTICULE_DEMI_OUVERTURE)
        vitesse = random.uniform(VITESSE_PARTICULE_MIN, VITESSE_PARTICULE_MAX) * multiplicateur_vitesse
        duree = random.uniform(DUREE_PARTICULE_MIN_SECONDES, DUREE_PARTICULE_MAX_SECONDES)
        particules.append(
            ParticuleImpact(
                position_x=origine_x,
                position_y=origine_y,
                vitesse_x=cos(angle) * vitesse,
                vitesse_y=sin(angle) * vitesse,
                duree_totale=duree,
                temps_restant=duree,
                taille=random.randint(TAILLE_PARTICULE_MIN, TAILLE_PARTICULE_MAX),
                couleur=couleur,
            )
        )


def declencher_feedback_impact(
    etat_feedback: EtatFeedbackCombat,
    particules: list[ParticuleImpact],
    origine_x: float,
    origine_y: float,
    direction_x: float,
    direction_y: float,
    couleur_particule: Tuple[int, int, int],
    couleur_flash: Tuple[int, int, int],
    intensite_flash: float,
    nombre_particules: int,
    multiplicateur_vitesse: float = 1.0,
) -> None:
    """Declenche un feedback visuel d impact.

    Args:
        etat_feedback: Etat temporaire des effets combat.
        particules: Liste des particules actives.
        origine_x: Origine X de l effet.
        origine_y: Origine Y de l effet.
        direction_x: Direction principale de projection.
        direction_y: Direction principale de projection.
        couleur_particule: Couleur RGB des particules.
        couleur_flash: Couleur RGB du flash ecran.
        intensite_flash: Intensite alpha du flash.
        nombre_particules: Nombre de particules a creer.
        multiplicateur_vitesse: Facteur de vitesse des particules.

    Returns:
        None.
    """

    etat_feedback.gel_restant = max(etat_feedback.gel_restant, DUREE_GEL_IMPACT_SECONDES)
    etat_feedback.flash_restant = DUREE_FLASH_IMPACT_SECONDES
    etat_feedback.flash_intensite_max = max(etat_feedback.flash_intensite_max, intensite_flash)
    etat_feedback.couleur_flash = couleur_flash
    ajouter_particules_directionnelles(
        particules,
        origine_x,
        origine_y,
        direction_x,
        direction_y,
        couleur_particule,
        nombre_particules,
        multiplicateur_vitesse,
    )


def mettre_a_jour_particules(particules: list[ParticuleImpact], delta_temps: float) -> None:
    """Met a jour la simulation des particules actives.

    Args:
        particules: Liste des particules.
        delta_temps: Pas de simulation en secondes.

    Returns:
        None.
    """

    particules_vivantes: list[ParticuleImpact] = []
    multiplicateur_freinage = max(0.0, 1.0 - FREINAGE_PARTICULES * delta_temps)
    for particule in particules:
        particule.temps_restant -= delta_temps
        if particule.temps_restant <= 0.0:
            continue
        particule.vitesse_x *= multiplicateur_freinage
        particule.vitesse_y *= multiplicateur_freinage
        particule.position_x += particule.vitesse_x * delta_temps
        particule.position_y += particule.vitesse_y * delta_temps
        particules_vivantes.append(particule)
    particules[:] = particules_vivantes


def dessiner_particules(surface: pygame.Surface, particules: list[ParticuleImpact]) -> None:
    """Dessine les particules d impact actives.

    Args:
        surface: Surface cible.
        particules: Liste des particules a afficher.

    Returns:
        None.
    """

    if not particules:
        return

    calque = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    for particule in particules:
        ratio = max(0.0, min(1.0, particule.temps_restant / particule.duree_totale))
        alpha = int(255 * ratio)
        rayon = max(1, int(particule.taille * (0.6 + 0.4 * ratio)))
        pygame.draw.circle(
            calque,
            (particule.couleur[0], particule.couleur[1], particule.couleur[2], alpha),
            (int(particule.position_x), int(particule.position_y)),
            rayon,
        )
    surface.blit(calque, (0, 0))


def appliquer_flash_ecran(surface: pygame.Surface, etat_feedback: EtatFeedbackCombat) -> None:
    """Applique un flash ecran decroissant.

    Args:
        surface: Surface cible.
        etat_feedback: Etat des effets de combat.

    Returns:
        None.
    """

    if etat_feedback.flash_restant <= 0.0 or etat_feedback.flash_intensite_max <= 0.0:
        return

    ratio = etat_feedback.flash_restant / DUREE_FLASH_IMPACT_SECONDES
    alpha = int(max(0.0, min(255.0, etat_feedback.flash_intensite_max * ratio)))
    if alpha <= 0:
        return

    calque = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    calque.fill(
        (
            etat_feedback.couleur_flash[0],
            etat_feedback.couleur_flash[1],
            etat_feedback.couleur_flash[2],
            alpha,
        )
    )
    surface.blit(calque, (0, 0))


def mettre_a_jour_feedback_combat(etat_feedback: EtatFeedbackCombat, delta_temps: float) -> None:
    """Met a jour les timers des effets temporaires de combat.

    Args:
        etat_feedback: Etat des feedbacks.
        delta_temps: Delta temps en secondes.

    Returns:
        None.
    """

    etat_feedback.gel_restant = max(0.0, etat_feedback.gel_restant - delta_temps)
    etat_feedback.flash_restant = max(0.0, etat_feedback.flash_restant - delta_temps)
    if etat_feedback.flash_restant <= 0.0:
        etat_feedback.flash_intensite_max = 0.0


def vider_feedback_combat(etat_feedback: EtatFeedbackCombat, particules: list[ParticuleImpact]) -> None:
    """Reinitialise tous les feedbacks visuels de combat.

    Args:
        etat_feedback: Etat des feedbacks.
        particules: Liste des particules.

    Returns:
        None.
    """

    etat_feedback.gel_restant = 0.0
    etat_feedback.flash_restant = 0.0
    etat_feedback.flash_intensite_max = 0.0
    particules.clear()


def reinitialiser_etat_arene_neon(etat_arene: EtatAreneNeon) -> None:
    """Remet a zero l etat anime de l arene neon.

    Args:
        etat_arene: Etat visuel de l arene.

    Returns:
        None.
    """

    etat_arene.phase_animation = 0.0
    etat_arene.energie_impact = 0.0


def reinitialiser_style_pour_manche(etat_style: EtatStyleJoueur) -> None:
    """Reinitialise l etat style volatile au debut d une manche.

    Args:
        etat_style: Etat style du joueur.

    Returns:
        None.
    """

    etat_style.combo_courant = 0
    etat_style.temps_combo_restant = 0.0
    etat_style.cooldown_esquive_restant = 0.0
    etat_style.dans_zone_danger = False
    etat_style.dernier_message = ""
    etat_style.temps_message_restant = 0.0


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


def declencher_reaction_arene_neon(etat_arene: EtatAreneNeon, gain_energie: float) -> None:
    """Augmente temporairement l energie d impact de l arene.

    Args:
        etat_arene: Etat visuel courant de l arene.
        gain_energie: Gain d energie a appliquer.

    Returns:
        None.
    """

    etat_arene.energie_impact = max(0.0, min(1.0, etat_arene.energie_impact + max(0.0, gain_energie)))


def mettre_a_jour_arene_neon(
    etat_arene: EtatAreneNeon,
    parametres_arene: ParametresAreneNeon,
    delta_temps: float,
) -> None:
    """Met a jour l animation temporelle de l arene neon.

    Args:
        etat_arene: Etat visuel courant.
        parametres_arene: Parametres visuels de l arene.
        delta_temps: Delta temps en secondes.

    Returns:
        None.
    """

    etat_arene.phase_animation += delta_temps * parametres_arene.vitesse_oscillation
    etat_arene.energie_impact = max(
        0.0,
        etat_arene.energie_impact - delta_temps * parametres_arene.decroissance_energie_impact,
    )


def dessiner_effets_arene_neon(
    surface: pygame.Surface,
    centre_x: float,
    centre_y: float,
    rayon: float,
    couleur_bord: Tuple[int, int, int],
    etat_arene: EtatAreneNeon,
    parametres_arene: ParametresAreneNeon,
) -> None:
    """Dessine un faux glow neon et des lignes electriques animees.

    Args:
        surface: Surface de rendu.
        centre_x: Centre X de l arene.
        centre_y: Centre Y de l arene.
        rayon: Rayon courant de l arene.
        couleur_bord: Couleur neon principale.
        etat_arene: Etat d animation de l arene.
        parametres_arene: Parametres visuels de l arene.

    Returns:
        None.
    """

    centre = (int(centre_x), int(centre_y))
    calque = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    oscillation = 0.5 + 0.5 * sin(etat_arene.phase_animation)
    intensite = parametres_arene.intensite_glow_base + etat_arene.energie_impact * parametres_arene.intensite_glow_impact
    intensite = max(0.0, min(1.0, intensite))

    for index_couche in range(NOMBRE_COUCHES_GLOW_NEON):
        ratio = 1.0 - (index_couche / max(1, NOMBRE_COUCHES_GLOW_NEON))
        alpha = int(OPACITE_GLOW_NEON_MAX * intensite * ratio * (0.65 + 0.35 * oscillation))
        epaisseur = EPAISSEUR_GLOW_NEON + index_couche * 2
        if alpha <= 0:
            continue
        pygame.draw.circle(
            calque,
            (couleur_bord[0], couleur_bord[1], couleur_bord[2], alpha),
            centre,
            int(rayon + index_couche * 2),
            epaisseur,
        )

    nombre_lignes = max(0, parametres_arene.nombre_lignes_electriques)
    for index_ligne in range(nombre_lignes):
        ratio_ligne = index_ligne / max(1, nombre_lignes)
        angle = (
            ratio_ligne * 2.0 * pi
            + etat_arene.phase_animation * parametres_arene.vitesse_rotation_lignes
            + sin(index_ligne * ESPACEMENT_LIGNES_ELECTRIQUES + etat_arene.phase_animation * 0.9) * 0.15
        )
        longueur_ratio = 0.5 + 0.5 * sin(etat_arene.phase_animation * 2.3 + index_ligne * 1.7)
        longueur = parametres_arene.longueur_lignes_min + (
            parametres_arene.longueur_lignes_max - parametres_arene.longueur_lignes_min
        ) * longueur_ratio * (1.0 + 0.5 * etat_arene.energie_impact)
        rayon_debut = rayon + 2.0
        rayon_fin = rayon_debut + longueur
        point_debut_x = centre_x + cos(angle) * rayon_debut
        point_debut_y = centre_y + sin(angle) * rayon_debut
        point_fin_x = centre_x + cos(angle) * rayon_fin
        point_fin_y = centre_y + sin(angle) * rayon_fin
        normale_x = -sin(angle)
        normale_y = cos(angle)
        jitter = (
            sin(etat_arene.phase_animation * 5.2 + index_ligne * 2.9)
            * parametres_arene.amplitude_jitter_lignes
            * (0.4 + 0.6 * etat_arene.energie_impact)
        )
        point_milieu_x = (point_debut_x + point_fin_x) * 0.5 + normale_x * jitter
        point_milieu_y = (point_debut_y + point_fin_y) * 0.5 + normale_y * jitter
        opacite = parametres_arene.opacite_lignes_base + etat_arene.energie_impact * parametres_arene.opacite_lignes_impact
        alpha_ligne = int(255.0 * max(0.0, min(1.0, opacite)))
        couleur_ligne = (couleur_bord[0], couleur_bord[1], couleur_bord[2], alpha_ligne)
        pygame.draw.line(
            calque,
            couleur_ligne,
            (int(point_debut_x), int(point_debut_y)),
            (int(point_milieu_x), int(point_milieu_y)),
            2,
        )
        pygame.draw.line(
            calque,
            couleur_ligne,
            (int(point_milieu_x), int(point_milieu_y)),
            (int(point_fin_x), int(point_fin_y)),
            2,
        )

    surface.blit(calque, (0, 0))


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


def calculer_progression_cooldown(cooldown_restant: float, cooldown_total: float) -> float:
    """Calcule la progression visuelle d une competence.

    Args:
        cooldown_restant: Cooldown restant en secondes.
        cooldown_total: Cooldown complet en secondes.

    Returns:
        Progression normalisee entre 0 (vide) et 1 (pret).
    """

    if cooldown_total <= 0.0:
        return 1.0
    ratio = 1.0 - (cooldown_restant / cooldown_total)
    return max(0.0, min(1.0, ratio))


def dessiner_indicateur_competence(
    surface: pygame.Surface,
    police: pygame.font.Font,
    position_x: int,
    position_y: int,
    label: str,
    progression: float,
    couleur_remplissage: Tuple[int, int, int],
) -> None:
    """Dessine un indicateur de cooldown de competence.

    Args:
        surface: Surface cible.
        police: Police d affichage du label.
        position_x: Position X du bloc.
        position_y: Position Y du bloc.
        label: Label court (B1, B3, B4).
        progression: Progression normalisee de recharge.
        couleur_remplissage: Couleur de remplissage.

    Returns:
        None.
    """

    progression_normalisee = max(0.0, min(1.0, progression))
    bloc = pygame.Rect(position_x, position_y, LARGEUR_INDICATEUR_COMPETENCE, HAUTEUR_INDICATEUR_COMPETENCE)
    pygame.draw.rect(surface, COULEUR_INDICATEUR_FOND, bloc)

    largeur_interieure = LARGEUR_INDICATEUR_COMPETENCE - 2 * MARGE_INTERIEURE_INDICATEUR
    largeur_remplissage = int(largeur_interieure * progression_normalisee)
    if largeur_remplissage > 0:
        pygame.draw.rect(
            surface,
            couleur_remplissage,
            pygame.Rect(
                position_x + MARGE_INTERIEURE_INDICATEUR,
                position_y + MARGE_INTERIEURE_INDICATEUR,
                largeur_remplissage,
                HAUTEUR_INDICATEUR_COMPETENCE - 2 * MARGE_INTERIEURE_INDICATEUR,
            ),
        )

    pygame.draw.rect(surface, COULEUR_BLANC, bloc, 2)
    dessiner_texte(
        surface,
        police,
        label,
        COULEUR_INDICATEUR_TEXTE,
        (position_x + LARGEUR_INDICATEUR_COMPETENCE / 2, position_y + HAUTEUR_INDICATEUR_COMPETENCE / 2),
    )


def dessiner_indicateurs_competences_joueur(
    surface: pygame.Surface,
    police: pygame.font.Font,
    joueur: Joueur,
    parametres: ParametresCombat,
    position_x: int,
    position_y: int,
) -> None:
    """Dessine les indicateurs B1/B3/B4 pour un joueur.

    Args:
        surface: Surface cible.
        police: Police du HUD.
        joueur: Joueur concerne.
        parametres: Parametres de combat.
        position_x: Position X de la zone de jauge associee.
        position_y: Position Y des blocs.

    Returns:
        None.
    """

    cooldown_dash_restant = joueur.cooldowns.get("dash", 0.0)
    cooldown_bump_restant = joueur.cooldowns.get("bump", 0.0)
    cooldown_bouclier_restant = joueur.cooldowns.get("bouclier", 0.0)
    progression_dash = calculer_progression_cooldown(cooldown_dash_restant, parametres.cooldown_dash)
    progression_bump = calculer_progression_cooldown(cooldown_bump_restant, parametres.cooldown_bump)
    progression_bouclier = calculer_progression_cooldown(cooldown_bouclier_restant, parametres.cooldown_bouclier)

    largeur_totale = 3 * LARGEUR_INDICATEUR_COMPETENCE + 2 * ESPACEMENT_INDICATEUR_COMPETENCE
    depart_x = int(position_x + (LARGEUR_JAUGE_ULTIME - largeur_totale) / 2)

    dessiner_indicateur_competence(
        surface,
        police,
        depart_x,
        position_y,
        "B1",
        progression_dash,
        COULEUR_INDICATEUR_DASH,
    )
    dessiner_indicateur_competence(
        surface,
        police,
        depart_x + LARGEUR_INDICATEUR_COMPETENCE + ESPACEMENT_INDICATEUR_COMPETENCE,
        position_y,
        "B3",
        progression_bump,
        COULEUR_INDICATEUR_BUMP,
    )
    dessiner_indicateur_competence(
        surface,
        police,
        depart_x + 2 * (LARGEUR_INDICATEUR_COMPETENCE + ESPACEMENT_INDICATEUR_COMPETENCE),
        position_y,
        "B4",
        progression_bouclier,
        COULEUR_INDICATEUR_BOUCLIER,
    )


def dessiner_panneau_style_joueur(
    surface: pygame.Surface,
    police: pygame.font.Font,
    petite_police: pygame.font.Font,
    position_x: int,
    position_y: int,
    largeur: int,
    hauteur: int,
    couleur_principale: Tuple[int, int, int],
    titre: str,
    etat_style: EtatStyleJoueur,
    temps_animation: float,
) -> None:
    """Dessine un panneau HUD style anime pour un joueur.

    Args:
        surface: Surface de rendu.
        police: Police principale.
        petite_police: Police secondaire.
        position_x: Position X du panneau.
        position_y: Position Y du panneau.
        largeur: Largeur du panneau.
        hauteur: Hauteur du panneau.
        couleur_principale: Couleur neon du joueur.
        titre: Titre du panneau (J1 ou J2).
        etat_style: Etat style du joueur.
        temps_animation: Temps global pour les pulsations.

    Returns:
        None.
    """

    panneau = pygame.Surface((largeur, hauteur), pygame.SRCALPHA)
    panneau.fill(COULEUR_STYLE_FOND)
    pygame.draw.rect(
        panneau,
        (couleur_principale[0], couleur_principale[1], couleur_principale[2], 220),
        pygame.Rect(0, 0, largeur, hauteur),
        EPAISSEUR_BORD_PANNEAU_STYLE,
    )

    score_texte = police.render(f"{titre} STYLE {etat_style.score_total}", True, couleur_principale)
    panneau.blit(score_texte, (14, 10))

    couleur_combo = COULEUR_STYLE_COMBO if etat_style.combo_courant > 1 else COULEUR_INDICATEUR_TEXTE
    combo_texte = petite_police.render(f"Combo x{max(1, etat_style.combo_courant)}", True, couleur_combo)
    panneau.blit(combo_texte, (14, 44))

    message = etat_style.dernier_message if etat_style.dernier_message else "-"
    message_texte = petite_police.render(message, True, COULEUR_STYLE_MESSAGE)
    panneau.blit(message_texte, (130, 44))

    if etat_style.combo_courant > 1:
        pulsation = 0.5 + 0.5 * sin(temps_animation * 7.2)
        rayon = int(RAYON_MINI_PULSE_STYLE + (RAYON_MAX_PULSE_STYLE - RAYON_MINI_PULSE_STYLE) * pulsation)
        alpha = int(120 + 110 * pulsation)
        pygame.draw.circle(
            panneau,
            (couleur_principale[0], couleur_principale[1], couleur_principale[2], alpha),
            (largeur - 28, 24),
            rayon,
            EPAISSEUR_PULSE_STYLE,
        )

    surface.blit(panneau, (position_x, position_y))


def dessiner_interface(
    surface: pygame.Surface,
    police: pygame.font.Font,
    petite_police: pygame.font.Font,
    largeur_surface: int,
    hauteur_surface: int,
    couleur_ui: Tuple[int, int, int],
    parametres: ParametresCombat,
    style_j1: EtatStyleJoueur,
    style_j2: EtatStyleJoueur,
    temps_animation: float,
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
        parametres: Parametres de combat.
        style_j1: Etat style du joueur 1.
        style_j2: Etat style du joueur 2.
        temps_animation: Temps global d animation HUD.
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
    position_y_competences = hauteur_surface - DECALAGE_VERTICAL_INDICATEURS
    dessiner_indicateurs_competences_joueur(
        surface,
        petite_police,
        joueur_1,
        parametres,
        MARGE_JAUGE_GAUCHE,
        position_y_competences,
    )
    dessiner_indicateurs_competences_joueur(
        surface,
        petite_police,
        joueur_2,
        parametres,
        largeur_surface - MARGE_JAUGE_DROITE,
        position_y_competences,
    )
    dessiner_panneau_style_joueur(
        surface,
        petite_police,
        petite_police,
        MARGE_LATERALE_PANNEAU_STYLE,
        MARGE_HAUTE_PANNEAU_STYLE,
        LARGEUR_PANNEAU_STYLE,
        HAUTEUR_PANNEAU_STYLE,
        COULEUR_STYLE_J1,
        "J1",
        style_j1,
        temps_animation,
    )
    dessiner_panneau_style_joueur(
        surface,
        petite_police,
        petite_police,
        largeur_surface - MARGE_LATERALE_PANNEAU_STYLE - LARGEUR_PANNEAU_STYLE,
        MARGE_HAUTE_PANNEAU_STYLE,
        LARGEUR_PANNEAU_STYLE,
        HAUTEUR_PANNEAU_STYLE,
        COULEUR_STYLE_J2,
        "J2",
        style_j2,
        temps_animation,
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
    parametres_style = construire_parametres_style(configuration)
    parametres_arene_neon = construire_parametres_arene_neon(configuration)

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
    style_j1 = EtatStyleJoueur()
    style_j2 = EtatStyleJoueur()
    reinitialiser_style_pour_manche(style_j1)
    reinitialiser_style_pour_manche(style_j2)
    dernier_vainqueur_manche = ""
    feedback_combat = EtatFeedbackCombat()
    particules_impact: list[ParticuleImpact] = []
    etat_arene_neon = EtatAreneNeon()
    temps_animation_hud = 0.0

    while True:
        delta_temps = horloge.tick(fps_cible) / 1000.0
        temps_animation_hud += delta_temps
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

        simulation_gelee = feedback_combat.gel_restant > 0.0
        delta_simulation = 0.0 if simulation_gelee else delta_temps
        if not simulation_gelee:
            mettre_a_jour_particules(particules_impact, delta_temps)
        mettre_a_jour_arene_neon(etat_arene_neon, parametres_arene_neon, delta_temps)
        mettre_a_jour_etat_style(style_j1, delta_temps)
        mettre_a_jour_etat_style(style_j2, delta_temps)

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
                reinitialiser_etat_style(style_j1)
                reinitialiser_etat_style(style_j2)
                joueur_1, joueur_2, temps_restant, countdown, rayon_arene = reinitialiser_manche(
                    configuration,
                    largeur,
                    hauteur,
                    duree_manche,
                    compte_a_rebours_initial,
                    rayon_depart,
                )
                reinitialiser_style_pour_manche(style_j1)
                reinitialiser_style_pour_manche(style_j2)
                vider_feedback_combat(feedback_combat, particules_impact)
                reinitialiser_etat_arene_neon(etat_arene_neon)
                etat = "compte_a_rebours"

            if appui_ultime_global:
                pygame.quit()
                return 0

            if inactif >= delai_attract:
                score_j1 = 0
                score_j2 = 0
                reinitialiser_etat_style(style_j1)
                reinitialiser_etat_style(style_j2)
                joueur_1, joueur_2, temps_restant, countdown, rayon_arene = reinitialiser_manche(
                    configuration,
                    largeur,
                    hauteur,
                    duree_manche,
                    compte_a_rebours_initial,
                    rayon_depart,
                )
                reinitialiser_style_pour_manche(style_j1)
                reinitialiser_style_pour_manche(style_j2)
                countdown = countdown_attract_initial
                vider_feedback_combat(feedback_combat, particules_impact)
                reinitialiser_etat_arene_neon(etat_arene_neon)
                etat = "attract"

        elif etat in {"compte_a_rebours", "attract", "manche"}:
            if etat == "compte_a_rebours":
                countdown -= delta_simulation
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
                countdown -= delta_simulation
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
                    reinitialiser_etat_style(style_j1)
                    reinitialiser_etat_style(style_j2)
                    joueur_1, joueur_2, temps_restant, countdown, rayon_arene = reinitialiser_manche(
                        configuration,
                        largeur,
                        hauteur,
                        duree_manche,
                        compte_a_rebours_initial,
                        rayon_depart,
                    )
                    reinitialiser_style_pour_manche(style_j1)
                    reinitialiser_style_pour_manche(style_j2)
                    vider_feedback_combat(feedback_combat, particules_impact)
                    reinitialiser_etat_arene_neon(etat_arene_neon)
                    etat = "compte_a_rebours"
                    continue
                if countdown <= 0.0:
                    etat = "manche"

            if etat in {"manche", "attract"}:
                en_manche = etat == "manche"
                if en_manche:
                    if simulation_gelee:
                        axe_j1 = (0.0, 0.0)
                        axe_j2 = (0.0, 0.0)
                    else:
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
                    delta_simulation,
                    parametres,
                )
                appliquer_deplacement_inertiel(
                    joueur_2,
                    axe_j2[0],
                    axe_j2[1],
                    frein_j2,
                    delta_simulation,
                    parametres,
                )
                resoudre_collision_capsules(joueur_1, joueur_2, parametres)

                decrementer_cooldowns(joueur_1, delta_simulation)
                decrementer_cooldowns(joueur_2, delta_simulation)
                mettre_a_jour_bouclier(joueur_1, delta_simulation)
                mettre_a_jour_bouclier(joueur_2, delta_simulation)
                charger_ultime(joueur_1, delta_simulation, parametres)
                charger_ultime(joueur_2, delta_simulation, parametres)

                if en_manche and not simulation_gelee:
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
                        declencher_feedback_impact(
                            feedback_combat,
                            particules_impact,
                            joueur_1.position_x - joueur_1.direction_x * joueur_1.rayon * 0.6,
                            joueur_1.position_y - joueur_1.direction_y * joueur_1.rayon * 0.6,
                            -joueur_1.direction_x,
                            -joueur_1.direction_y,
                            COULEUR_PARTICULE_DASH,
                            COULEUR_FLASH_DASH,
                            INTENSITE_FLASH_DASH,
                            NOMBRE_PARTICULES_DASH,
                        )
                        declencher_reaction_arene_neon(etat_arene_neon, parametres_arene_neon.gain_impact_dash)
                        if tenter_esquive_proche(joueur_1, joueur_2, style_j1, parametres_style):
                            declencher_feedback_impact(
                                feedback_combat,
                                particules_impact,
                                joueur_1.position_x,
                                joueur_1.position_y,
                                joueur_1.vitesse_x,
                                joueur_1.vitesse_y,
                                COULEUR_PARTICULE_DASH,
                                COULEUR_FLASH_DASH,
                                INTENSITE_FLASH_DASH * 0.8,
                                NOMBRE_PARTICULES_DASH,
                            )
                    if j2_dash_presse and activer_dash(joueur_2, parametres):
                        jouer_son(sons["dash"])
                        declencher_feedback_impact(
                            feedback_combat,
                            particules_impact,
                            joueur_2.position_x - joueur_2.direction_x * joueur_2.rayon * 0.6,
                            joueur_2.position_y - joueur_2.direction_y * joueur_2.rayon * 0.6,
                            -joueur_2.direction_x,
                            -joueur_2.direction_y,
                            COULEUR_PARTICULE_DASH,
                            COULEUR_FLASH_DASH,
                            INTENSITE_FLASH_DASH,
                            NOMBRE_PARTICULES_DASH,
                        )
                        declencher_reaction_arene_neon(etat_arene_neon, parametres_arene_neon.gain_impact_dash)
                        if tenter_esquive_proche(joueur_2, joueur_1, style_j2, parametres_style):
                            declencher_feedback_impact(
                                feedback_combat,
                                particules_impact,
                                joueur_2.position_x,
                                joueur_2.position_y,
                                joueur_2.vitesse_x,
                                joueur_2.vitesse_y,
                                COULEUR_PARTICULE_DASH,
                                COULEUR_FLASH_DASH,
                                INTENSITE_FLASH_DASH * 0.8,
                                NOMBRE_PARTICULES_DASH,
                            )

                    if j1_bump_presse and executer_bump(joueur_1, joueur_2, parametres):
                        jouer_son(sons["bump"])
                        enregistrer_impact_style(style_j1, parametres_style)
                        declencher_feedback_impact(
                            feedback_combat,
                            particules_impact,
                            joueur_2.position_x,
                            joueur_2.position_y,
                            joueur_2.position_x - joueur_1.position_x,
                            joueur_2.position_y - joueur_1.position_y,
                            COULEUR_PARTICULE_BUMP,
                            COULEUR_FLASH_BUMP,
                            INTENSITE_FLASH_BUMP,
                            NOMBRE_PARTICULES_BUMP,
                        )
                        declencher_reaction_arene_neon(etat_arene_neon, parametres_arene_neon.gain_impact_bump)
                    if j2_bump_presse and executer_bump(joueur_2, joueur_1, parametres):
                        jouer_son(sons["bump"])
                        enregistrer_impact_style(style_j2, parametres_style)
                        declencher_feedback_impact(
                            feedback_combat,
                            particules_impact,
                            joueur_1.position_x,
                            joueur_1.position_y,
                            joueur_1.position_x - joueur_2.position_x,
                            joueur_1.position_y - joueur_2.position_y,
                            COULEUR_PARTICULE_BUMP,
                            COULEUR_FLASH_BUMP,
                            INTENSITE_FLASH_BUMP,
                            NOMBRE_PARTICULES_BUMP,
                        )
                        declencher_reaction_arene_neon(etat_arene_neon, parametres_arene_neon.gain_impact_bump)

                    if j1_bouclier_presse and activer_bouclier(joueur_1, parametres):
                        jouer_son(sons["bouclier"])
                    if j2_bouclier_presse and activer_bouclier(joueur_2, parametres):
                        jouer_son(sons["bouclier"])

                    vitesse_j2_avant_ultime_x = joueur_2.vitesse_x
                    vitesse_j2_avant_ultime_y = joueur_2.vitesse_y
                    if j1_ultime_presse and activer_ultime(joueur_1, joueur_2, parametres):
                        jouer_son(sons["ultime"])
                        impact_ultime_j1 = (
                            abs(joueur_2.vitesse_x - vitesse_j2_avant_ultime_x) > SEUIL_NORME_DIRECTION
                            or abs(joueur_2.vitesse_y - vitesse_j2_avant_ultime_y) > SEUIL_NORME_DIRECTION
                        )
                        declencher_feedback_impact(
                            feedback_combat,
                            particules_impact,
                            joueur_1.position_x,
                            joueur_1.position_y,
                            joueur_2.position_x - joueur_1.position_x,
                            joueur_2.position_y - joueur_1.position_y,
                            COULEUR_PARTICULE_ULTIME,
                            COULEUR_FLASH_ULTIME,
                            INTENSITE_FLASH_ULTIME,
                            NOMBRE_PARTICULES_ULTIME,
                            multiplicateur_vitesse=1.2,
                        )
                        declencher_reaction_arene_neon(etat_arene_neon, parametres_arene_neon.gain_impact_ultime)
                        if impact_ultime_j1:
                            enregistrer_impact_style(style_j1, parametres_style)

                    vitesse_j1_avant_ultime_x = joueur_1.vitesse_x
                    vitesse_j1_avant_ultime_y = joueur_1.vitesse_y
                    if j2_ultime_presse and activer_ultime(joueur_2, joueur_1, parametres):
                        jouer_son(sons["ultime"])
                        impact_ultime_j2 = (
                            abs(joueur_1.vitesse_x - vitesse_j1_avant_ultime_x) > SEUIL_NORME_DIRECTION
                            or abs(joueur_1.vitesse_y - vitesse_j1_avant_ultime_y) > SEUIL_NORME_DIRECTION
                        )
                        declencher_feedback_impact(
                            feedback_combat,
                            particules_impact,
                            joueur_2.position_x,
                            joueur_2.position_y,
                            joueur_1.position_x - joueur_2.position_x,
                            joueur_1.position_y - joueur_2.position_y,
                            COULEUR_PARTICULE_ULTIME,
                            COULEUR_FLASH_ULTIME,
                            INTENSITE_FLASH_ULTIME,
                            NOMBRE_PARTICULES_ULTIME,
                            multiplicateur_vitesse=1.2,
                        )
                        declencher_reaction_arene_neon(etat_arene_neon, parametres_arene_neon.gain_impact_ultime)
                        if impact_ultime_j2:
                            enregistrer_impact_style(style_j2, parametres_style)

                    if j1_taunt_presse:
                        jouer_son(sons["taunt"])
                    if j2_taunt_presse:
                        jouer_son(sons["taunt"])

                temps_restant -= delta_simulation
                multiplicateur = multiplicateur_sudden_death if temps_restant <= 0.0 else 1.0
                rayon_arene = max(rayon_min, rayon_arene - vitesse_retrecissement * multiplicateur * delta_simulation)
                if en_manche:
                    bonus_save_j1 = mettre_a_jour_sauvetage_bord(
                        joueur_1,
                        style_j1,
                        parametres_style,
                        centre_x,
                        centre_y,
                        rayon_arene,
                        largeur_danger,
                    )
                    bonus_save_j2 = mettre_a_jour_sauvetage_bord(
                        joueur_2,
                        style_j2,
                        parametres_style,
                        centre_x,
                        centre_y,
                        rayon_arene,
                        largeur_danger,
                    )
                    if bonus_save_j1:
                        declencher_feedback_impact(
                            feedback_combat,
                            particules_impact,
                            joueur_1.position_x,
                            joueur_1.position_y,
                            centre_x - joueur_1.position_x,
                            centre_y - joueur_1.position_y,
                            COULEUR_PARTICULE_ULTIME,
                            COULEUR_FLASH_DASH,
                            INTENSITE_FLASH_DASH,
                            NOMBRE_PARTICULES_DASH,
                        )
                        declencher_reaction_arene_neon(etat_arene_neon, parametres_arene_neon.gain_impact_bump)
                    if bonus_save_j2:
                        declencher_feedback_impact(
                            feedback_combat,
                            particules_impact,
                            joueur_2.position_x,
                            joueur_2.position_y,
                            centre_x - joueur_2.position_x,
                            centre_y - joueur_2.position_y,
                            COULEUR_PARTICULE_ULTIME,
                            COULEUR_FLASH_DASH,
                            INTENSITE_FLASH_DASH,
                            NOMBRE_PARTICULES_DASH,
                        )
                        declencher_reaction_arene_neon(etat_arene_neon, parametres_arene_neon.gain_impact_bump)

                elimine_j1 = verifier_sortie_arene(joueur_1, centre_x, centre_y, rayon_arene, delta_simulation, parametres)
                elimine_j2 = verifier_sortie_arene(joueur_2, centre_x, centre_y, rayon_arene, delta_simulation, parametres)

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
                dessiner_effets_arene_neon(
                    ecran,
                    centre_x,
                    centre_y,
                    rayon_arene,
                    couleur_arene_bord,
                    etat_arene_neon,
                    parametres_arene_neon,
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
                    parametres,
                    style_j1,
                    style_j2,
                    temps_animation_hud,
                    score_j1,
                    score_j2,
                    joueur_1,
                    joueur_2,
                    temps_restant,
                )

                if elimine_j1 or elimine_j2:
                    jouer_son(sons["elimination"])
                    declencher_reaction_arene_neon(etat_arene_neon, parametres_arene_neon.gain_impact_ultime)
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
            countdown -= delta_simulation
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
                reinitialiser_style_pour_manche(style_j1)
                reinitialiser_style_pour_manche(style_j2)
                vider_feedback_combat(feedback_combat, particules_impact)
                reinitialiser_etat_arene_neon(etat_arene_neon)
                etat = "compte_a_rebours"

        elif etat == "fin_match":
            countdown -= delta_simulation
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
                reinitialiser_etat_style(style_j1)
                reinitialiser_etat_style(style_j2)
                joueur_1, joueur_2, temps_restant, countdown, rayon_arene = reinitialiser_manche(
                    configuration,
                    largeur,
                    hauteur,
                    duree_manche,
                    compte_a_rebours_initial,
                    rayon_depart,
                )
                reinitialiser_style_pour_manche(style_j1)
                reinitialiser_style_pour_manche(style_j2)
                vider_feedback_combat(feedback_combat, particules_impact)
                reinitialiser_etat_arene_neon(etat_arene_neon)
                etat = "compte_a_rebours"
            if appui_ultime_global:
                vider_feedback_combat(feedback_combat, particules_impact)
                reinitialiser_etat_arene_neon(etat_arene_neon)
                etat = "titre"
            if countdown <= 0.0:
                vider_feedback_combat(feedback_combat, particules_impact)
                reinitialiser_etat_arene_neon(etat_arene_neon)
                etat = "titre"

        dessiner_particules(ecran, particules_impact)
        appliquer_flash_ecran(ecran, feedback_combat)
        pygame.display.flip()
        mettre_a_jour_feedback_combat(feedback_combat, delta_temps)


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
