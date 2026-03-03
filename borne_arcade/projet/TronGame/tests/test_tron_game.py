"""Tests cibles du jeu TronGame."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame

DOSSIER_JEU = Path(__file__).resolve().parents[1]
if str(DOSSIER_JEU) not in sys.path:
    sys.path.insert(0, str(DOSSIER_JEU))

from ai import AI  # pylint: disable=import-error
from config import BLUE, BLUE_GLOW, ORANGE, ORANGE_GLOW  # pylint: disable=import-error
from direction import Direction  # pylint: disable=import-error
from game_main import Game  # pylint: disable=import-error


class TestTronGame(unittest.TestCase):
    """Verifie les contrats critiques du gameplay Tron."""

    @classmethod
    def setUpClass(cls) -> None:
        """Initialise pygame une fois pour la suite."""

        pygame.init()
        pygame.font.init()

    @classmethod
    def tearDownClass(cls) -> None:
        """Libere pygame en fin de suite."""

        pygame.quit()

    def creer_jeu(self) -> Game:
        """Construit un jeu minimal deterministe pour les tests.

        Returns:
            Instance de jeu prete a etre manipulee.
        """

        surface = pygame.Surface((100, 100))
        return Game(surface, mode="multi", move_delay=0)

    def test_collision_bordure_tue_le_joueur(self) -> None:
        """Verifie qu une collision sur bordure termine la partie."""

        jeu = self.creer_jeu()
        jeu.player1.positions = [(jeu.cells_x - 1, 0)]
        jeu.player1.direction = Direction.RIGHT
        jeu.player1.last_move_time = -10_000
        jeu.player2.positions = [(0, jeu.cells_y - 1)]
        jeu.player2.direction = Direction.RIGHT
        jeu.player2.last_move_time = -10_000
        jeu.update_grid()

        fin_de_partie = jeu.update()

        self.assertTrue(fin_de_partie)
        self.assertTrue(jeu.game_over)
        self.assertEqual(jeu.winner, "Joueur 2")

    def test_mise_a_jour_grille_reflete_positions(self) -> None:
        """Verifie que la grille reprend bien les positions des joueurs."""

        jeu = self.creer_jeu()
        jeu.player1.positions = [(1, 1), (2, 1)]
        jeu.player2.positions = [(5, 4)]

        jeu.update_grid()

        self.assertEqual(jeu.grid[1][1], 1)
        self.assertEqual(jeu.grid[1][2], 1)
        self.assertEqual(jeu.grid[4][5], 2)

    def test_ia_choisit_un_mouvement_non_suicidaire(self) -> None:
        """Verifie que l IA choisit la seule direction sans collision immediate."""

        grille = [[0 for _ in range(5)] for _ in range(5)]
        ia = AI(2, 2, ORANGE, ORANGE_GLOW, difficulty="moyen")
        ia.positions = [(2, 2)]
        ia.direction = Direction.RIGHT

        grille[2][3] = 1
        grille[1][2] = 1
        grille[2][1] = 1

        ia.update(10_000, grille, None)

        self.assertEqual(ia.direction, Direction.DOWN)

    def test_gagnant_est_renseigne_quand_joueur_deux_perd(self) -> None:
        """Verifie que le gagnant est correctement renseigne."""

        jeu = self.creer_jeu()
        jeu.player1.positions = [(1, 1)]
        jeu.player1.direction = Direction.RIGHT
        jeu.player2.positions = [(0, 0)]
        jeu.player1.last_move_time = pygame.time.get_ticks()
        jeu.player2.last_move_time = -10_000
        jeu.player2.direction = Direction.LEFT
        jeu.update_grid()

        fin_de_partie = jeu.update()

        self.assertTrue(fin_de_partie)
        self.assertEqual(jeu.winner, "Joueur 1")


if __name__ == "__main__":
    unittest.main()
