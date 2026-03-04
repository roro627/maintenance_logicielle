import importlib.util
import os
import time

import pygame

from config import (
    ASSETS_FOLDER,
    BACKGROUND_COLOR,
    DISPLAY_FLAGS,
    FPS,
    HIT_BOX_PIXEL,
    HIT_LINE_Y,
    KEY_MAPPING,
    LANE_COUNT,
    MENU_BACK_TO_MENU_KEY,
    MENU_QUIT_KEY,
    MENU_RESUME_KEY,
    MENU_RETRY_KEY,
    PAUSE_KEY,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TILE_COLOR,
    TILE_HEIGHT,
)
from tile import Tile


def load_beatmap(filename):
    """Charge une beatmap exportee en Python.

    Args:
        filename: Nom du fichier `.osu` source.

    Returns:
        Liste des tuiles exportees.
    """

    map_name = os.path.splitext(filename)[0]
    map_path = os.path.join("maps", f"{map_name}.py")
    spec = importlib.util.spec_from_file_location("beatmap_module", map_path)
    beatmap_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(beatmap_module)
    return beatmap_module.beatmap


def draw_pause_menu(screen, font):
    """Dessine l ecran de pause.

    Args:
        screen: Surface de rendu.
        font: Police pygame.

    Returns:
        Aucun.
    """

    screen.fill(BACKGROUND_COLOR)
    text = font.render("Pause", True, (255, 255, 255))
    resume = font.render("Entree : reprendre", True, (200, 200, 200))
    quit_text = font.render("Q : quitter", True, (200, 200, 200))
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 300))
    screen.blit(resume, (SCREEN_WIDTH // 2 - resume.get_width() // 2, 400))
    screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, 450))
    pygame.display.flip()


def evaluer_frappe_tuile(
    tuile,
    temps_courant,
    position_ligne=HIT_LINE_Y,
    marge_pixels=HIT_BOX_PIXEL,
    hauteur_tuile=TILE_HEIGHT,
):
    """Retourne le resultat de frappe pour une tuile a un instant donne.

    Args:
        tuile: Tuile a evaluer.
        temps_courant: Temps de reference en millisecondes.
        position_ligne: Ordonnee de la ligne de frappe.
        marge_pixels: Tolerance verticale de frappe.
        hauteur_tuile: Hauteur de la tuile.

    Returns:
        `Perfect` si la tuile est dans la fenetre de frappe, sinon `Miss`.
    """

    position_y = tuile.get_y(temps_courant)
    sommet = position_y
    bas = position_y + hauteur_tuile
    if sommet <= position_ligne + marge_pixels and bas >= position_ligne - marge_pixels:
        return "Perfect"
    return "Miss"


def draw_scene(screen, font, tiles, current_time, score, combo, feedbacks):
    """Dessine la scene de jeu complete.

    Args:
        screen: Surface de rendu.
        font: Police principale.
        tiles: Liste des tuiles.
        current_time: Temps courant.
        score: Score courant.
        combo: Combo courant.
        feedbacks: Feedbacks temporaires.

    Returns:
        Aucun.
    """

    screen.fill(BACKGROUND_COLOR)
    pygame.draw.line(screen, (255, 0, 0), (0, HIT_LINE_Y), (SCREEN_WIDTH, HIT_LINE_Y), 3)
    for tile in tiles:
        if tile.hit:
            continue
        y = tile.get_y(current_time)
        if y > SCREEN_HEIGHT - 60:
            continue
        x = tile.lane * (SCREEN_WIDTH // LANE_COUNT)
        tile.draw(screen, x, SCREEN_WIDTH // LANE_COUNT, current_time, TILE_COLOR)

    screen.blit(font.render(f"Score : {score}", True, (255, 255, 255)), (10, SCREEN_HEIGHT - 80))
    screen.blit(font.render(f"Combo : {combo}", True, (200, 200, 200)), (10, SCREEN_HEIGHT - 40))

    for feedback in feedbacks[:]:
        text, temps_initial, lane = feedback
        if current_time - temps_initial < 300:
            color = (255, 255, 255) if text == "Perfect" else (255, 50, 50)
            surface = font.render(text, True, color)
            x = lane * (SCREEN_WIDTH // LANE_COUNT) + 20
            screen.blit(surface, (x, HIT_LINE_Y - 40))
        else:
            feedbacks.remove(feedback)

    pygame.display.flip()


def countdown(screen, font, tiles, current_time, score, combo, feedbacks):
    """Affiche un compte a rebours avant reprise.

    Args:
        screen: Surface de rendu.
        font: Police principale.
        tiles: Tuiles courantes.
        current_time: Temps courant.
        score: Score courant.
        combo: Combo courant.
        feedbacks: Feedbacks temporaires.

    Returns:
        Aucun.
    """

    for compteur in range(3, 0, -1):
        draw_scene(screen, font, tiles, current_time, score, combo, feedbacks)
        txt = font.render(str(compteur), True, (255, 255, 255))
        screen.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()
        time.sleep(1)


def end_screen(screen, font, score, total_notes, max_combo):
    """Affiche l ecran de fin.

    Args:
        screen: Surface de rendu.
        font: Police principale.
        score: Score final.
        total_notes: Nombre total de notes.
        max_combo: Combo maximal.

    Returns:
        `retry`, `menu` ou `quit`.
    """

    screen.fill(BACKGROUND_COLOR)
    title = font.render("Fin de la partie", True, (255, 255, 255))
    score_txt = font.render(f"Score final : {score}", True, (255, 255, 255))
    percent = (score / total_notes) * 100 if total_notes > 0 else 0
    percent_txt = font.render(f"Precision : {percent:.1f}%", True, (0, 255, 255))
    combo_txt = font.render(f"Combo max : {max_combo}", True, (255, 255, 0))
    retry = font.render("Entree : Rejouer", True, (200, 200, 200))
    menu = font.render("M : Menu", True, (200, 200, 200))
    quit_text = font.render("Q : Quitter", True, (200, 200, 200))
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 180))
    screen.blit(score_txt, (SCREEN_WIDTH // 2 - score_txt.get_width() // 2, 250))
    screen.blit(percent_txt, (SCREEN_WIDTH // 2 - percent_txt.get_width() // 2, 300))
    screen.blit(combo_txt, (SCREEN_WIDTH // 2 - combo_txt.get_width() // 2, 350))
    screen.blit(retry, (SCREEN_WIDTH // 2 - retry.get_width() // 2, 420))
    screen.blit(menu, (SCREEN_WIDTH // 2 - menu.get_width() // 2, 470))
    screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, 520))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == MENU_RETRY_KEY:
                    return "retry"
                if event.key == MENU_BACK_TO_MENU_KEY:
                    return "menu"
                if event.key == MENU_QUIT_KEY:
                    return "quit"


def play_map(filename):
    """Execute une partie sur une beatmap.

    Args:
        filename: Fichier `.osu` a jouer.

    Returns:
        `retry`, `menu` ou `quit`.
    """

    beatmap = load_beatmap(filename)
    tiles = [Tile(lane, time_value) for lane, time_value in beatmap]
    audio_file = os.path.join(ASSETS_FOLDER, os.path.splitext(filename)[0] + ".mp3")

    flags = pygame.HWSURFACE | pygame.DOUBLEBUF | DISPLAY_FLAGS
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 48)

    pygame.mixer.init()
    if os.path.exists(audio_file):
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
    else:
        print(f"Audio manquant : {audio_file}")

    start_time = time.time()
    paused = False
    score = 0
    combo = 0
    max_combo = 0
    feedbacks = []
    total_notes = len(tiles)

    while True:
        current_time = (time.time() - start_time) * 1000 if not paused else current_time
        screen.fill(BACKGROUND_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == PAUSE_KEY:
                    paused = True
                    pygame.mixer.music.pause()
                    draw_pause_menu(screen, font)
                    while paused:
                        for pause_event in pygame.event.get():
                            if pause_event.type == pygame.QUIT:
                                return "quit"
                            if pause_event.type == pygame.KEYDOWN:
                                if pause_event.key == MENU_RESUME_KEY:
                                    countdown(screen, font, tiles, current_time, score, combo, feedbacks)
                                    start_time = time.time() - (current_time / 1000)
                                    pygame.mixer.music.unpause()
                                    paused = False
                                elif pause_event.key == MENU_QUIT_KEY:
                                    return "menu"
                else:
                    for lane, key in KEY_MAPPING.items():
                        if key is None or event.key != key:
                            continue
                        for tile in tiles:
                            if tile.hit:
                                continue
                            if tile.lane == lane and evaluer_frappe_tuile(tile, current_time) == "Perfect":
                                tile.hit = True
                                score += 1
                                combo += 1
                                if combo > max_combo:
                                    max_combo = combo
                                feedbacks.append(("Perfect", current_time, lane))
                                break
                        else:
                            combo = 0
                            feedbacks.append(("Miss", current_time, lane))

        for tile in tiles:
            if not tile.hit and tile.get_y(current_time) > SCREEN_HEIGHT:
                tile.hit = True
                combo = 0
                feedbacks.append(("Miss", current_time, tile.lane))

        draw_scene(screen, font, tiles, current_time, score, combo, feedbacks)

        if all(tile.hit for tile in tiles):
            pygame.mixer.music.stop()
            return end_screen(screen, font, score, total_notes, max_combo)

        clock.tick(FPS)
