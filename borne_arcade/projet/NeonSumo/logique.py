"""Logique pure du jeu Neon Sumo.

Ce module ne depend pas de pygame afin de faciliter les tests unitaires.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import sqrt
from typing import Dict, Tuple


Vecteur = Tuple[float, float]
SEUIL_NORME_CARREE = 1e-18
SEUIL_PROJECTION_BUMP = 0.1


@dataclass
class ParametresCombat:
    """Regroupe les parametres physiques et gameplay d une manche.

    Attributes:
        acceleration: Acceleration appliquee par le joystick.
        friction_base: Coefficient de friction normal.
        friction_frein: Coefficient de friction pendant le freinage.
        vitesse_max: Vitesse maximale de deplacement.
        impulsion_dash: Impulsion de dash.
        impulsion_bump: Impulsion de bump sur la cible.
        rayon_bump: Portee du bump.
        multiplicateur_bouclier: Reduction de knockback sous bouclier.
        duree_bouclier: Duree d activation du bouclier en secondes.
        cooldown_dash: Delai entre deux dashs.
        cooldown_bump: Delai entre deux bumps.
        cooldown_bouclier: Delai entre deux boucliers.
        cooldown_taunt: Delai entre deux taunts.
        gain_ultime_par_seconde: Charge passive de la jauge ultime.
        gain_ultime_par_impact: Gain de jauge lors d un impact.
        rayon_ultime: Portee de l onde ultime.
        impulsion_ultime: Impulsion appliquee par l onde ultime.
        delai_sortie_arene: Temps en dehors de l arene avant elimination.
    """

    acceleration: float
    friction_base: float
    friction_frein: float
    vitesse_max: float
    impulsion_dash: float
    impulsion_bump: float
    rayon_bump: float
    multiplicateur_bouclier: float
    duree_bouclier: float
    cooldown_dash: float
    cooldown_bump: float
    cooldown_bouclier: float
    cooldown_taunt: float
    gain_ultime_par_seconde: float
    gain_ultime_par_impact: float
    rayon_ultime: float
    impulsion_ultime: float
    delai_sortie_arene: float


@dataclass
class Joueur:
    """Represente l etat dynamique d un joueur.

    Attributes:
        identifiant: Nom logique du joueur.
        position_x: Position X dans l arene.
        position_y: Position Y dans l arene.
        vitesse_x: Vitesse courante sur l axe X.
        vitesse_y: Vitesse courante sur l axe Y.
        rayon: Rayon de la capsule.
        direction_x: Direction principale pour dash et bump.
        direction_y: Direction principale pour dash et bump.
        jauge_ultime: Valeur de jauge ultime entre 0 et 1.
        actif_bouclier: Indique si le bouclier est actif.
        temps_restant_bouclier: Temps restant de bouclier.
        temps_hors_arene: Temps cumule hors de la zone.
        cooldowns: Dictionnaire des cooldowns restants.
    """

    identifiant: str
    position_x: float
    position_y: float
    vitesse_x: float
    vitesse_y: float
    rayon: float
    direction_x: float
    direction_y: float
    jauge_ultime: float = 0.0
    actif_bouclier: bool = False
    temps_restant_bouclier: float = 0.0
    temps_hors_arene: float = 0.0
    cooldowns: Dict[str, float] = field(default_factory=dict)


def normaliser(vecteur_x: float, vecteur_y: float) -> Vecteur:
    """Normalise un vecteur 2D.

    Args:
        vecteur_x: Composante X.
        vecteur_y: Composante Y.

    Returns:
        Le vecteur normalise. Retourne (0, 0) si norme nulle.
    """

    norme_carre = vecteur_x * vecteur_x + vecteur_y * vecteur_y
    if norme_carre <= SEUIL_NORME_CARREE:
        return 0.0, 0.0
    inverse_norme = 1.0 / sqrt(norme_carre)
    return vecteur_x * inverse_norme, vecteur_y * inverse_norme


def limiter_vitesse(vitesse_x: float, vitesse_y: float, vitesse_max: float) -> Vecteur:
    """Limite la norme de la vitesse.

    Args:
        vitesse_x: Vitesse X.
        vitesse_y: Vitesse Y.
        vitesse_max: Norme maximale autorisee.

    Returns:
        Le vecteur de vitesse eventuellement reduit.
    """

    norme_carre = vitesse_x * vitesse_x + vitesse_y * vitesse_y
    vitesse_max_carre = vitesse_max * vitesse_max
    if norme_carre <= vitesse_max_carre or norme_carre <= SEUIL_NORME_CARREE:
        return vitesse_x, vitesse_y
    facteur = vitesse_max / sqrt(norme_carre)
    return vitesse_x * facteur, vitesse_y * facteur


def appliquer_deplacement_inertiel(
    joueur: Joueur,
    entree_x: float,
    entree_y: float,
    frein_actif: bool,
    delta_temps: float,
    parametres: ParametresCombat,
) -> None:
    """Met a jour la position/vitesse d un joueur avec inertie.

    Args:
        joueur: Joueur a mettre a jour.
        entree_x: Axe horizontal du joystick.
        entree_y: Axe vertical du joystick.
        frein_actif: Indique si le frein est maintenu.
        delta_temps: Pas de simulation en secondes.
        parametres: Parametres physiques du combat.

    Returns:
        None.
    """

    direction_x, direction_y = normaliser(entree_x, entree_y)
    acceleration = parametres.acceleration * delta_temps
    joueur.vitesse_x += direction_x * acceleration
    joueur.vitesse_y += direction_y * acceleration

    if direction_x != 0.0 or direction_y != 0.0:
        joueur.direction_x = direction_x
        joueur.direction_y = direction_y

    friction = parametres.friction_frein if frein_actif else parametres.friction_base
    multiplicateur = max(0.0, 1.0 - friction * delta_temps)
    joueur.vitesse_x *= multiplicateur
    joueur.vitesse_y *= multiplicateur

    joueur.vitesse_x, joueur.vitesse_y = limiter_vitesse(
        joueur.vitesse_x,
        joueur.vitesse_y,
        parametres.vitesse_max,
    )

    joueur.position_x += joueur.vitesse_x * delta_temps
    joueur.position_y += joueur.vitesse_y * delta_temps


def decrementer_cooldowns(joueur: Joueur, delta_temps: float) -> None:
    """Decremente l ensemble des cooldowns d un joueur.

    Args:
        joueur: Joueur concerne.
        delta_temps: Delta temps en secondes.

    Returns:
        None.
    """

    cooldowns = joueur.cooldowns
    for cle_cooldown in cooldowns:
        cooldown_restant = cooldowns[cle_cooldown] - delta_temps
        cooldowns[cle_cooldown] = cooldown_restant if cooldown_restant > 0.0 else 0.0


def cooldown_pret(joueur: Joueur, nom_action: str) -> bool:
    """Indique si une action est prete a etre utilisee.

    Args:
        joueur: Joueur concerne.
        nom_action: Nom de l action.

    Returns:
        True si le cooldown est a zero, sinon False.
    """

    return joueur.cooldowns.get(nom_action, 0.0) <= 0.0


def demarrer_cooldown(joueur: Joueur, nom_action: str, duree: float) -> None:
    """Demarre un cooldown sur une action.

    Args:
        joueur: Joueur concerne.
        nom_action: Nom de l action.
        duree: Duree du cooldown.

    Returns:
        None.
    """

    joueur.cooldowns[nom_action] = max(0.0, duree)


def activer_dash(joueur: Joueur, parametres: ParametresCombat) -> bool:
    """Declenche un dash si le cooldown le permet.

    Args:
        joueur: Joueur qui dash.
        parametres: Parametres de combat.

    Returns:
        True si le dash est effectue, sinon False.
    """

    if not cooldown_pret(joueur, "dash"):
        return False

    direction_x, direction_y = normaliser(joueur.direction_x, joueur.direction_y)
    if direction_x == 0.0 and direction_y == 0.0:
        direction_x = 1.0

    joueur.vitesse_x += direction_x * parametres.impulsion_dash
    joueur.vitesse_y += direction_y * parametres.impulsion_dash
    joueur.vitesse_x, joueur.vitesse_y = limiter_vitesse(
        joueur.vitesse_x,
        joueur.vitesse_y,
        parametres.vitesse_max * 1.8,
    )
    demarrer_cooldown(joueur, "dash", parametres.cooldown_dash)
    return True


def executer_bump(
    attaquant: Joueur,
    defenseur: Joueur,
    parametres: ParametresCombat,
) -> bool:
    """Applique un bump frontal si la cible est dans la portee.

    Args:
        attaquant: Joueur a l origine du bump.
        defenseur: Joueur cible.
        parametres: Parametres du combat.

    Returns:
        True si impact valide, sinon False.
    """

    if not cooldown_pret(attaquant, "bump"):
        return False

    difference_x = defenseur.position_x - attaquant.position_x
    difference_y = defenseur.position_y - attaquant.position_y
    distance_carre = difference_x * difference_x + difference_y * difference_y
    portee = parametres.rayon_bump + attaquant.rayon + defenseur.rayon
    if distance_carre > portee * portee:
        return False

    direction_att_x, direction_att_y = normaliser(attaquant.direction_x, attaquant.direction_y)
    if distance_carre <= SEUIL_NORME_CARREE:
        return False

    inverse_distance = 1.0 / sqrt(distance_carre)
    vers_cible_x = difference_x * inverse_distance
    vers_cible_y = difference_y * inverse_distance
    projection = direction_att_x * vers_cible_x + direction_att_y * vers_cible_y
    if projection < SEUIL_PROJECTION_BUMP:
        return False

    facteur = parametres.multiplicateur_bouclier if defenseur.actif_bouclier else 1.0
    defenseur.vitesse_x += vers_cible_x * parametres.impulsion_bump * facteur
    defenseur.vitesse_y += vers_cible_y * parametres.impulsion_bump * facteur
    attaquant.jauge_ultime = min(1.0, attaquant.jauge_ultime + parametres.gain_ultime_par_impact)
    demarrer_cooldown(attaquant, "bump", parametres.cooldown_bump)
    return True


def activer_bouclier(joueur: Joueur, parametres: ParametresCombat) -> bool:
    """Active le bouclier temporaire si possible.

    Args:
        joueur: Joueur concerne.
        parametres: Parametres du combat.

    Returns:
        True si le bouclier est active, sinon False.
    """

    if not cooldown_pret(joueur, "bouclier"):
        return False

    joueur.actif_bouclier = True
    joueur.temps_restant_bouclier = parametres.duree_bouclier
    demarrer_cooldown(joueur, "bouclier", parametres.cooldown_bouclier)
    return True


def mettre_a_jour_bouclier(joueur: Joueur, delta_temps: float) -> None:
    """Met a jour la duree restante du bouclier.

    Args:
        joueur: Joueur concerne.
        delta_temps: Delta temps en secondes.

    Returns:
        None.
    """

    if not joueur.actif_bouclier:
        return

    joueur.temps_restant_bouclier = max(0.0, joueur.temps_restant_bouclier - delta_temps)
    if joueur.temps_restant_bouclier <= 0.0:
        joueur.actif_bouclier = False


def charger_ultime(joueur: Joueur, delta_temps: float, parametres: ParametresCombat) -> None:
    """Recharge passivement la jauge ultime.

    Args:
        joueur: Joueur concerne.
        delta_temps: Delta temps en secondes.
        parametres: Parametres de combat.

    Returns:
        None.
    """

    joueur.jauge_ultime = min(
        1.0,
        joueur.jauge_ultime + parametres.gain_ultime_par_seconde * delta_temps,
    )


def activer_ultime(
    attaquant: Joueur,
    defenseur: Joueur,
    parametres: ParametresCombat,
) -> bool:
    """Declenche une onde ultime si la jauge est pleine.

    Args:
        attaquant: Joueur lanceur.
        defenseur: Joueur cible potentielle.
        parametres: Parametres de combat.

    Returns:
        True si l ultime est lancee, sinon False.
    """

    if attaquant.jauge_ultime < 1.0:
        return False

    difference_x = defenseur.position_x - attaquant.position_x
    difference_y = defenseur.position_y - attaquant.position_y
    distance_carre = difference_x * difference_x + difference_y * difference_y
    portee = parametres.rayon_ultime + defenseur.rayon
    if distance_carre <= portee * portee:
        if distance_carre <= SEUIL_NORME_CARREE:
            direction_x = 0.0
            direction_y = 0.0
        else:
            inverse_distance = 1.0 / sqrt(distance_carre)
            direction_x = difference_x * inverse_distance
            direction_y = difference_y * inverse_distance
        facteur = parametres.multiplicateur_bouclier if defenseur.actif_bouclier else 1.0
        defenseur.vitesse_x += direction_x * parametres.impulsion_ultime * facteur
        defenseur.vitesse_y += direction_y * parametres.impulsion_ultime * facteur

    attaquant.jauge_ultime = 0.0
    return True


def verifier_sortie_arene(
    joueur: Joueur,
    centre_x: float,
    centre_y: float,
    rayon_arene: float,
    delta_temps: float,
    parametres: ParametresCombat,
) -> bool:
    """Verifie si un joueur est elimine hors de l arene.

    Args:
        joueur: Joueur a verifier.
        centre_x: Centre X de l arene.
        centre_y: Centre Y de l arene.
        rayon_arene: Rayon actuel de l arene.
        delta_temps: Delta temps en secondes.
        parametres: Parametres de combat.

    Returns:
        True si le joueur est elimine, sinon False.
    """

    difference_x = joueur.position_x - centre_x
    difference_y = joueur.position_y - centre_y
    distance_centre_carre = difference_x * difference_x + difference_y * difference_y
    if distance_centre_carre <= rayon_arene * rayon_arene:
        joueur.temps_hors_arene = 0.0
        return False

    joueur.temps_hors_arene += delta_temps
    return joueur.temps_hors_arene >= parametres.delai_sortie_arene


__all__ = [
    "ParametresCombat",
    "Joueur",
    "normaliser",
    "limiter_vitesse",
    "appliquer_deplacement_inertiel",
    "decrementer_cooldowns",
    "cooldown_pret",
    "demarrer_cooldown",
    "activer_dash",
    "executer_bump",
    "activer_bouclier",
    "mettre_a_jour_bouclier",
    "charger_ultime",
    "activer_ultime",
    "verifier_sortie_arene",
]
