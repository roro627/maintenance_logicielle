#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Configuration du jeu Tron."""

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


# Dimensions de l ecran
MODE_AFFICHAGE = determiner_mode_affichage()
SCREEN_WIDTH = lire_entier_environnement("BORNE_RESOLUTION_X", 1280)
SCREEN_HEIGHT = lire_entier_environnement("BORNE_RESOLUTION_Y", 1024)
FPS = 60
TITLE = "TRON - Arcade Game"
FULLSCREEN = MODE_AFFICHAGE == MODE_AFFICHAGE_PLEIN_ECRAN
DISPLAY_FLAGS = determiner_drapeaux_affichage(MODE_AFFICHAGE)

# Parametres du jeu
GRID_SIZE = 10
MOVE_DELAY = 50
TRAIL_LENGTH = 500

# Niveaux de difficulte de l IA
AI_DIFFICULTY_SETTINGS = {
    "facile": {
        "look_ahead": 5,
        "update_interval": 300,
    },
    "moyen": {
        "look_ahead": 10,
        "update_interval": 200,
    },
    "difficile": {
        "look_ahead": 15,
        "update_interval": 100,
    },
}

# Couleurs
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 80, 255)
BLUE_GLOW = (30, 144, 255)
ORANGE = (255, 140, 0)
ORANGE_GLOW = (255, 165, 0)
CYAN = (0, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
NEON_BLUE = (30, 100, 255)
NEON_PINK = (255, 0, 128)

# Controles des joueurs
PLAYER1_CONTROLS = {
    "UP": "UP",
    "DOWN": "DOWN",
    "LEFT": "LEFT",
    "RIGHT": "RIGHT",
}

PLAYER2_CONTROLS = {
    "UP": "O",
    "DOWN": "l",
    "LEFT": "k",
    "RIGHT": "m",
}

# Chemins des ressources
SOUNDS_DIR = "assets/sounds"
IMAGES_DIR = "assets/images"

# Sons
SOUND_NAVIGATE = "navigate.wav"
SOUND_SELECT = "select.wav"
SOUND_CRASH = "crash.wav"
SOUND_MOVE = "move.wav"
MUSIC_MENU = "music_menu_wav"

# Images
LOGO_IMAGE = "tron_logo.png"
