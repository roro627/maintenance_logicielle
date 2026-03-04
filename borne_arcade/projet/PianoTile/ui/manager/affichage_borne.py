"""Utilitaires purs de configuration d affichage pour PianoTile."""

from __future__ import annotations

import os

import pygame

MODE_AFFICHAGE_FENETRE = "fenetre"
MODE_AFFICHAGE_FENETRE_SANS_BORDURE = "fenetre_sans_bordure"
MODE_AFFICHAGE_PLEIN_ECRAN = "plein_ecran"


def lire_entier_environnement(nom_variable: str, valeur_par_defaut: int) -> int:
    """Lit un entier depuis l environnement.

    Args:
        nom_variable: Variable a lire.
        valeur_par_defaut: Valeur de repli.

    Returns:
        Entier valide.
    """

    try:
        return int(os.environ.get(nom_variable, valeur_par_defaut))
    except (TypeError, ValueError):
        return valeur_par_defaut


def determiner_mode_affichage() -> str:
    """Retourne le mode d affichage demande par la borne.

    Args:
        Aucun.

    Returns:
        Mode d affichage normalise.
    """

    mode = os.environ.get("BORNE_MODE_AFFICHAGE", MODE_AFFICHAGE_FENETRE_SANS_BORDURE)
    if mode not in {
        MODE_AFFICHAGE_FENETRE,
        MODE_AFFICHAGE_FENETRE_SANS_BORDURE,
        MODE_AFFICHAGE_PLEIN_ECRAN,
    }:
        return MODE_AFFICHAGE_FENETRE_SANS_BORDURE
    return mode


def determiner_drapeaux_fenetre(mode_affichage: str) -> int:
    """Construit les drapeaux pygame selon le mode d affichage.

    Args:
        mode_affichage: Mode d affichage normalise.

    Returns:
        Drapeaux pygame a transmettre a `set_mode`.
    """

    drapeaux = pygame.DOUBLEBUF
    if mode_affichage == MODE_AFFICHAGE_PLEIN_ECRAN:
        drapeaux |= pygame.FULLSCREEN
    elif mode_affichage == MODE_AFFICHAGE_FENETRE_SANS_BORDURE:
        drapeaux |= pygame.NOFRAME
    return drapeaux


def determiner_resolution_borne() -> tuple[int, int]:
    """Retourne la resolution cible de la borne.

    Args:
        Aucun.

    Returns:
        Tuple `(largeur, hauteur)`.
    """

    largeur = lire_entier_environnement("BORNE_RESOLUTION_X", 1280)
    hauteur = lire_entier_environnement("BORNE_RESOLUTION_Y", 1024)
    return max(640, largeur), max(480, hauteur)
