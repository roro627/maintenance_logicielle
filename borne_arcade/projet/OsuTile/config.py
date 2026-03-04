# config.py

import os

import pygame

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

    mode = os.environ.get("BORNE_MODE_AFFICHAGE", MODE_AFFICHAGE_PLEIN_ECRAN)
    if mode not in {
        MODE_AFFICHAGE_FENETRE,
        MODE_AFFICHAGE_FENETRE_SANS_BORDURE,
        MODE_AFFICHAGE_PLEIN_ECRAN,
    }:
        return MODE_AFFICHAGE_PLEIN_ECRAN
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


# === Fenetre ===
MODE_AFFICHAGE = determiner_mode_affichage()
SCREEN_WIDTH = lire_entier_environnement("BORNE_RESOLUTION_X", 1280)
SCREEN_HEIGHT = lire_entier_environnement("BORNE_RESOLUTION_Y", 1024)
FPS = 60
FULLSCREEN = MODE_AFFICHAGE == MODE_AFFICHAGE_PLEIN_ECRAN
DISPLAY_FLAGS = determiner_drapeaux_affichage(MODE_AFFICHAGE)

# === Affichage ===
BACKGROUND_COLOR = (0, 0, 0)
LANE_COLOR = (200, 200, 200)
TEXT_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (255, 255, 0)

# === Jeu ===
LANE_COUNT = 4
TILE_COLOR = (0, 150, 255)
HIT_LINE_Y = 800
FALL_TIME = 1.5
TILE_HEIGHT = 50
HIT_BOX_PIXEL = 30

# === Controles ===
KEY_MAPPING = {0: pygame.K_t, 1: pygame.K_y, 2: pygame.K_a, 3: pygame.K_z}
PAUSE_KEY = pygame.K_f

# Controles de navigation dans les menus
MENU_UP_KEY = pygame.K_UP
MENU_DOWN_KEY = pygame.K_DOWN
MENU_SELECT_KEY = pygame.K_g
MENU_BACK_KEY = pygame.K_h

# Controles pour les menus (pause, fin)
MENU_RESUME_KEY = pygame.K_g
MENU_QUIT_KEY = pygame.K_h
MENU_BACK_TO_MENU_KEY = pygame.K_s
MENU_RETRY_KEY = pygame.K_d

# === Fichiers ===
BEATMAP_FOLDER = "beatmaps"
ASSETS_FOLDER = "assets"

# === Textes d interface ===
MENU_TITLE = "Piano Tile Arcade"
SELECT_PROMPT = "Selectionne une chanson"
