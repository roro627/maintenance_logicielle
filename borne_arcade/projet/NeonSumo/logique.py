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
FACTEUR_PARTAGE_COLLISION = 0.5
MULTIPLICATEUR_LIMITE_VITESSE_COLLISION = 1.8


@dataclass
class ParametresCombat:
    """Regroupe les parametres physiques et gameplay d une manche.

    Attributes:
        acceleration: Acceleration appliquee par le joystick.
        friction_base: Coefficient de friction normal.
        friction_frein: Coefficient de friction pendant le freinage.
        vitesse_max: Vitesse maximale de deplacement.
        coefficient_rebond_collision: Coefficient de rebond sur collision passive.
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
    coefficient_rebond_collision: float
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


@dataclass
class ParametresStyle:
    """Regroupe les parametres du systeme de style.

    Attributes:
        fenetre_combo: Duree de maintien du combo.
        bonus_combo_par_niveau: Bonus ajoute par niveau de combo.
        points_impact: Points de base sur un impact offensif.
        points_esquive: Points de base sur une esquive proche.
        points_sauvetage: Points de base sur un retour du bord danger.
        distance_esquive: Marge supplementaire pour considerer une esquive proche.
        cooldown_esquive: Delai anti spam d une esquive proche.
        marge_sauvetage: Marge de retour en zone sure pour valider un sauvetage.
        duree_affichage_action: Duree d affichage du message de style.
    """

    fenetre_combo: float
    bonus_combo_par_niveau: int
    points_impact: int
    points_esquive: int
    points_sauvetage: int
    distance_esquive: float
    cooldown_esquive: float
    marge_sauvetage: float
    duree_affichage_action: float


@dataclass
class EtatStyleJoueur:
    """Represente l etat style d un joueur.

    Attributes:
        score_total: Score style cumule.
        combo_courant: Niveau de combo courant.
        temps_combo_restant: Temps restant avant expiration du combo.
        cooldown_esquive_restant: Delai restant avant nouvelle esquive proche.
        dans_zone_danger: Indique si le joueur etait dans la zone danger.
        dernier_message: Dernier libelle de gain style.
        temps_message_restant: Temps restant d affichage du dernier message.
    """

    score_total: int = 0
    combo_courant: int = 0
    temps_combo_restant: float = 0.0
    cooldown_esquive_restant: float = 0.0
    dans_zone_danger: bool = False
    dernier_message: str = ""
    temps_message_restant: float = 0.0


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


def resoudre_collision_capsules(
    joueur_1: Joueur,
    joueur_2: Joueur,
    parametres: ParametresCombat,
) -> bool:
    """Resout la collision passive entre deux capsules.

    La resolution applique:
    - une correction de penetration pour eviter le chevauchement,
    - une impulsion de rebond basee sur la vitesse relative.

    Args:
        joueur_1: Premier joueur.
        joueur_2: Second joueur.
        parametres: Parametres physiques du combat.

    Returns:
        True si une collision a ete resolue, sinon False.
    """

    difference_x = joueur_2.position_x - joueur_1.position_x
    difference_y = joueur_2.position_y - joueur_1.position_y
    distance_carre = difference_x * difference_x + difference_y * difference_y
    distance_minimale = joueur_1.rayon + joueur_2.rayon
    distance_minimale_carre = distance_minimale * distance_minimale
    if distance_carre >= distance_minimale_carre:
        return False

    if distance_carre <= SEUIL_NORME_CARREE:
        vitesse_relative_x = joueur_2.vitesse_x - joueur_1.vitesse_x
        vitesse_relative_y = joueur_2.vitesse_y - joueur_1.vitesse_y
        normale_x, normale_y = normaliser(vitesse_relative_x, vitesse_relative_y)
        if normale_x == 0.0 and normale_y == 0.0:
            normale_x, normale_y = 1.0, 0.0
        distance = 0.0
    else:
        distance = sqrt(distance_carre)
        inverse_distance = 1.0 / distance
        normale_x = difference_x * inverse_distance
        normale_y = difference_y * inverse_distance

    penetration = max(0.0, distance_minimale - distance)
    correction = penetration * FACTEUR_PARTAGE_COLLISION
    joueur_1.position_x -= normale_x * correction
    joueur_1.position_y -= normale_y * correction
    joueur_2.position_x += normale_x * correction
    joueur_2.position_y += normale_y * correction

    vitesse_relative_x = joueur_2.vitesse_x - joueur_1.vitesse_x
    vitesse_relative_y = joueur_2.vitesse_y - joueur_1.vitesse_y
    vitesse_normale = vitesse_relative_x * normale_x + vitesse_relative_y * normale_y
    if vitesse_normale >= 0.0:
        return True

    coefficient_rebond = max(0.0, min(1.0, parametres.coefficient_rebond_collision))
    impulsion = -(1.0 + coefficient_rebond) * vitesse_normale * FACTEUR_PARTAGE_COLLISION
    joueur_1.vitesse_x -= normale_x * impulsion
    joueur_1.vitesse_y -= normale_y * impulsion
    joueur_2.vitesse_x += normale_x * impulsion
    joueur_2.vitesse_y += normale_y * impulsion

    vitesse_limite = parametres.vitesse_max * MULTIPLICATEUR_LIMITE_VITESSE_COLLISION
    joueur_1.vitesse_x, joueur_1.vitesse_y = limiter_vitesse(
        joueur_1.vitesse_x,
        joueur_1.vitesse_y,
        vitesse_limite,
    )
    joueur_2.vitesse_x, joueur_2.vitesse_y = limiter_vitesse(
        joueur_2.vitesse_x,
        joueur_2.vitesse_y,
        vitesse_limite,
    )
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


def reinitialiser_etat_style(etat_style: EtatStyleJoueur) -> None:
    """Reinitialise un etat style joueur.

    Args:
        etat_style: Etat style a remettre a zero.

    Returns:
        None.
    """

    etat_style.score_total = 0
    etat_style.combo_courant = 0
    etat_style.temps_combo_restant = 0.0
    etat_style.cooldown_esquive_restant = 0.0
    etat_style.dans_zone_danger = False
    etat_style.dernier_message = ""
    etat_style.temps_message_restant = 0.0


def mettre_a_jour_etat_style(etat_style: EtatStyleJoueur, delta_temps: float) -> None:
    """Met a jour les timers du style d un joueur.

    Args:
        etat_style: Etat style a mettre a jour.
        delta_temps: Delta temps en secondes.

    Returns:
        None.
    """

    etat_style.temps_combo_restant = max(0.0, etat_style.temps_combo_restant - delta_temps)
    if etat_style.temps_combo_restant <= 0.0:
        etat_style.combo_courant = 0

    etat_style.cooldown_esquive_restant = max(0.0, etat_style.cooldown_esquive_restant - delta_temps)
    etat_style.temps_message_restant = max(0.0, etat_style.temps_message_restant - delta_temps)
    if etat_style.temps_message_restant <= 0.0:
        etat_style.dernier_message = ""


def ajouter_points_style(
    etat_style: EtatStyleJoueur,
    parametres_style: ParametresStyle,
    points_base: int,
    libelle_action: str,
) -> int:
    """Ajoute des points style en tenant compte du combo.

    Args:
        etat_style: Etat style du joueur.
        parametres_style: Parametres globaux style.
        points_base: Valeur de base a ajouter.
        libelle_action: Nom court de l action.

    Returns:
        Gain reel applique au score style.
    """

    if etat_style.temps_combo_restant > 0.0:
        etat_style.combo_courant += 1
    else:
        etat_style.combo_courant = 1

    bonus_combo = max(0, etat_style.combo_courant - 1) * max(0, parametres_style.bonus_combo_par_niveau)
    gain = max(0, points_base) + bonus_combo
    etat_style.score_total += gain
    etat_style.temps_combo_restant = max(0.0, parametres_style.fenetre_combo)
    etat_style.dernier_message = f"{libelle_action} +{gain}"
    etat_style.temps_message_restant = max(0.0, parametres_style.duree_affichage_action)
    return gain


def enregistrer_impact_style(
    etat_style: EtatStyleJoueur,
    parametres_style: ParametresStyle,
) -> int:
    """Ajoute des points style pour un impact reussi.

    Args:
        etat_style: Etat style du joueur attaquant.
        parametres_style: Parametres globaux style.

    Returns:
        Gain style applique.
    """

    return ajouter_points_style(
        etat_style,
        parametres_style,
        parametres_style.points_impact,
        "CHAIN",
    )


def tenter_esquive_proche(
    joueur: Joueur,
    adversaire: Joueur,
    etat_style: EtatStyleJoueur,
    parametres_style: ParametresStyle,
) -> bool:
    """Tente de valider une esquive proche.

    Args:
        joueur: Joueur potentiellement auteur de l esquive.
        adversaire: Joueur opposant.
        etat_style: Etat style du joueur.
        parametres_style: Parametres globaux style.

    Returns:
        True si une esquive proche est validee, sinon False.
    """

    if etat_style.cooldown_esquive_restant > 0.0:
        return False

    difference_x = adversaire.position_x - joueur.position_x
    difference_y = adversaire.position_y - joueur.position_y
    distance_carre = difference_x * difference_x + difference_y * difference_y
    distance_minimale = joueur.rayon + adversaire.rayon
    distance_maximale = distance_minimale + max(0.0, parametres_style.distance_esquive)
    if distance_carre < distance_minimale * distance_minimale:
        return False
    if distance_carre > distance_maximale * distance_maximale:
        return False

    vitesse_relative_x = joueur.vitesse_x - adversaire.vitesse_x
    vitesse_relative_y = joueur.vitesse_y - adversaire.vitesse_y
    projection = vitesse_relative_x * difference_x + vitesse_relative_y * difference_y
    if projection >= 0.0:
        return False

    ajouter_points_style(
        etat_style,
        parametres_style,
        parametres_style.points_esquive,
        "ESQUIVE",
    )
    etat_style.cooldown_esquive_restant = max(0.0, parametres_style.cooldown_esquive)
    return True


def mettre_a_jour_sauvetage_bord(
    joueur: Joueur,
    etat_style: EtatStyleJoueur,
    parametres_style: ParametresStyle,
    centre_x: float,
    centre_y: float,
    rayon_arene: float,
    largeur_danger: float,
) -> bool:
    """Met a jour la logique de sauvetage depuis la zone danger.

    Args:
        joueur: Joueur a suivre.
        etat_style: Etat style associe au joueur.
        parametres_style: Parametres globaux style.
        centre_x: Centre X de l arene.
        centre_y: Centre Y de l arene.
        rayon_arene: Rayon courant de l arene.
        largeur_danger: Largeur de la couronne danger.

    Returns:
        True si un bonus de sauvetage est attribue, sinon False.
    """

    difference_x = joueur.position_x - centre_x
    difference_y = joueur.position_y - centre_y
    distance = sqrt(difference_x * difference_x + difference_y * difference_y)

    limite_danger = max(0.0, rayon_arene - largeur_danger)
    limite_securite = max(0.0, limite_danger - max(0.0, parametres_style.marge_sauvetage))

    if distance >= limite_danger:
        etat_style.dans_zone_danger = True
        return False

    if etat_style.dans_zone_danger and distance <= limite_securite:
        etat_style.dans_zone_danger = False
        ajouter_points_style(
            etat_style,
            parametres_style,
            parametres_style.points_sauvetage,
            "SAVE",
        )
        return True

    if distance <= limite_securite:
        etat_style.dans_zone_danger = False
    return False


__all__ = [
    "ParametresCombat",
    "ParametresStyle",
    "Joueur",
    "EtatStyleJoueur",
    "normaliser",
    "limiter_vitesse",
    "appliquer_deplacement_inertiel",
    "decrementer_cooldowns",
    "cooldown_pret",
    "demarrer_cooldown",
    "activer_dash",
    "executer_bump",
    "resoudre_collision_capsules",
    "activer_bouclier",
    "mettre_a_jour_bouclier",
    "charger_ultime",
    "activer_ultime",
    "verifier_sortie_arene",
    "reinitialiser_etat_style",
    "mettre_a_jour_etat_style",
    "ajouter_points_style",
    "enregistrer_impact_style",
    "tenter_esquive_proche",
    "mettre_a_jour_sauvetage_bord",
]
