import os

import pygame
import pygame.font

MODE_AFFICHAGE_FENETRE = "fenetre"
MODE_AFFICHAGE_FENETRE_SANS_BORDURE = "fenetre_sans_bordure"
MODE_AFFICHAGE_PLEIN_ECRAN = "plein_ecran"


def lire_entier_environnement(nom_variable, valeur_par_defaut):
    """Lit un entier depuis l environnement.

    Args:
        nom_variable: Variable d environnement a lire.
        valeur_par_defaut: Valeur de repli.

    Returns:
        Entier valide.
    """

    try:
        return int(os.environ.get(nom_variable, valeur_par_defaut))
    except (TypeError, ValueError):
        return valeur_par_defaut


def determiner_mode_affichage():
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


def determiner_drapeaux_affichage(mode_affichage):
    """Construit les drapeaux pygame adaptes au mode d affichage.

    Args:
        mode_affichage: Mode d affichage normalise.

    Returns:
        Drapeaux pygame pour `set_mode`.
    """

    if mode_affichage == MODE_AFFICHAGE_PLEIN_ECRAN:
        return pygame.FULLSCREEN
    if mode_affichage == MODE_AFFICHAGE_FENETRE_SANS_BORDURE:
        return pygame.NOFRAME
    return 0


# Screen dimensions
MODE_AFFICHAGE = determiner_mode_affichage()
SCREEN_WIDTH = lire_entier_environnement("BORNE_RESOLUTION_X", 1280)
SCREEN_HEIGHT = lire_entier_environnement("BORNE_RESOLUTION_Y", 1024)
DISPLAY_FLAGS = determiner_drapeaux_affichage(MODE_AFFICHAGE)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

PLAYER_SPEED = 10

BALL_SPEED_X = 2
BALL_SPEED_FALL = 0.15
BALL_TOP_BOUNCE = -17
BALL_BOTTOM_BOUNCE = -14
BALL_EQUIVALENT = 14
FIRERATE = 7

pygame.font.init()

# Fonts
FONT = pygame.font.SysFont("Comic Sans MS", 30)
FONT_SCORE = pygame.font.SysFont("Comic Sans MS", 18)
