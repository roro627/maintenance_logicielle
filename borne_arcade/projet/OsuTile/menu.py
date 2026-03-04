import os
import sys

import pygame

from config import (
    BEATMAP_FOLDER,
    DISPLAY_FLAGS,
    FPS,
    MENU_DOWN_KEY,
    MENU_QUIT_KEY,
    MENU_SELECT_KEY,
    MENU_TITLE,
    MENU_UP_KEY,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SELECT_PROMPT,
)
from game import play_map


def draw_gradient_background(screen, color1, color2):
    """Dessine un fond degrade vertical.

    Args:
        screen: Surface pygame cible.
        color1: Couleur du haut.
        color2: Couleur du bas.

    Returns:
        Aucun.
    """

    for y in range(SCREEN_HEIGHT):
        ratio = y / SCREEN_HEIGHT
        rouge = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        vert = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        bleu = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        pygame.draw.line(screen, (rouge, vert, bleu), (0, y), (SCREEN_WIDTH, y))


def neon_text(surface, text, font, pos, main_color, glow_color, glow_size=4):
    """Affiche un texte avec un halo neon.

    Args:
        surface: Surface de rendu.
        text: Texte a afficher.
        font: Police pygame.
        pos: Position du texte.
        main_color: Couleur principale.
        glow_color: Couleur du halo.
        glow_size: Taille du halo.

    Returns:
        Aucun.
    """

    base = font.render(text, True, main_color)
    for dx in range(-glow_size, glow_size + 1):
        for dy in range(-glow_size, glow_size + 1):
            if dx * dx + dy * dy <= glow_size * glow_size:
                glow = font.render(text, True, glow_color)
                surface.blit(glow, (pos[0] + dx, pos[1] + dy))
    surface.blit(base, pos)


def run_menu():
    """Execute le menu de selection des beatmaps.

    Args:
        Aucun.

    Returns:
        Aucun.
    """

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DISPLAY_FLAGS)
    pygame.display.set_caption("Selection de musique")
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial Black", 48, bold=True)
    small_font = pygame.font.SysFont("Arial", 28, bold=True)

    beatmaps = [f for f in os.listdir(BEATMAP_FOLDER) if f.endswith(".osu")]
    selected_index = 0

    bg_top = (20, 20, 60)
    bg_bottom = (60, 0, 60)
    neon = (0, 255, 255)
    neon_glow = (0, 180, 255)
    white = (255, 255, 255)
    yellow = (255, 255, 0)
    select_bg = (40, 0, 80)

    running = True
    while running:
        draw_gradient_background(screen, bg_top, bg_bottom)

        title_pos = (SCREEN_WIDTH // 2 - font.size(MENU_TITLE)[0] // 2, 60)
        neon_text(screen, MENU_TITLE, font, title_pos, neon, neon_glow, 8)

        margin_x, margin_y = 120, 170
        rect_width = SCREEN_WIDTH - 2 * margin_x
        rect_height = 60 * len(beatmaps) + 40
        border_rect = pygame.Rect(margin_x, margin_y, rect_width, rect_height)
        pygame.draw.rect(screen, neon, border_rect, 6)
        pygame.draw.rect(screen, white, border_rect, 2)

        for index, beatmap in enumerate(beatmaps):
            display_name = os.path.splitext(beatmap)[0].replace("_", " ")
            y = margin_y + 20 + index * 60
            x = SCREEN_WIDTH // 2
            position = (x - small_font.size(display_name)[0] // 2, y)
            if index == selected_index:
                select_rect = pygame.Rect(margin_x + 10, y - 8, rect_width - 20, 54)
                pygame.draw.rect(screen, select_bg, select_rect)
                pygame.draw.rect(screen, yellow, select_rect, 3)
                neon_text(screen, display_name, small_font, position, yellow, neon_glow, 4)
            else:
                neon_text(screen, display_name, small_font, position, white, neon_glow, 2)

        prompt = SELECT_PROMPT + "  (H pour quitter)"
        prompt_pos = (
            SCREEN_WIDTH // 2 - small_font.size(prompt)[0] // 2,
            SCREEN_HEIGHT - 60,
        )
        neon_text(screen, prompt, small_font, prompt_pos, neon, neon_glow, 3)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == MENU_UP_KEY:
                    selected_index = (selected_index - 1) % len(beatmaps)
                elif event.key == MENU_DOWN_KEY:
                    selected_index = (selected_index + 1) % len(beatmaps)
                elif event.key == MENU_SELECT_KEY:
                    result = play_map(beatmaps[selected_index])
                    if result == "quit":
                        running = False
                elif event.key == MENU_QUIT_KEY:
                    running = False

        clock.tick(FPS)

    pygame.quit()
    sys.exit()
