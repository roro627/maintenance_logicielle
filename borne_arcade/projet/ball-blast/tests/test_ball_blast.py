"""Tests cibles du jeu ball-blast."""

from __future__ import annotations

import importlib
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame

DOSSIER_SOURCE = Path(__file__).resolve().parents[1] / "src"
if str(DOSSIER_SOURCE) not in sys.path:
    sys.path.insert(0, str(DOSSIER_SOURCE))

from game import Game, calculer_scissions_balle  # pylint: disable=import-error
import constantes as module_constantes  # pylint: disable=import-error


class TestBallBlast(unittest.TestCase):
    """Verifie les contrats critiques de ball-blast."""

    @classmethod
    def setUpClass(cls) -> None:
        """Initialise pygame une fois pour la suite."""

        pygame.init()
        pygame.font.init()

    @classmethod
    def tearDownClass(cls) -> None:
        """Libere pygame en fin de suite."""

        pygame.quit()

    def test_save_score_trie_par_ordre_decroissant(self) -> None:
        """Verifie le tri des scores sauvegardes."""

        jeu = Game.__new__(Game)
        jeu.player = type("JoueurFactice", (), {"score": 42})()

        with tempfile.TemporaryDirectory() as dossier_temporaire:
            ancien_cwd = Path.cwd()
            os.chdir(dossier_temporaire)
            try:
                Path("highscore").write_text("AAA-10\nBBB-99\n", encoding="utf-8")
                jeu._saveScore("ZZZ")
                lignes = Path("highscore").read_text(encoding="utf-8").splitlines()
            finally:
                os.chdir(ancien_cwd)

        self.assertEqual(lignes, ["BBB-99", "ZZZ-42", "AAA-10"])

    def test_next_level_reinitialise_les_compteurs(self) -> None:
        """Verifie la reinitialisation des compteurs de niveau."""

        jeu = Game.__new__(Game)
        jeu.level = 3
        jeu.ballsToSpawn = 1
        jeu.frameNumberWinAnim = 7
        jeu.frameNumberSpawnBalls = 8
        jeu.frameNumberBeginLevel = 9

        jeu.nextLevel()

        self.assertEqual(jeu.level, 4)
        self.assertEqual(jeu.ballsToSpawn, 14 + 4 * 5)
        self.assertEqual(jeu.frameNumberWinAnim, 0)
        self.assertEqual(jeu.frameNumberSpawnBalls, 0)
        self.assertEqual(jeu.frameNumberBeginLevel, 0)

    def test_calculer_scissions_balle_retourne_deux_boules_filles(self) -> None:
        """Verifie la resolution pure des scissions de boules."""

        niveaux = [[(0, 0, 0), 50], [(255, 0, 0), 40], [(0, 255, 0), 33]]
        scissions = calculer_scissions_balle(True, 0, 120, 75, niveaux)

        self.assertEqual(len(scissions), 2)
        self.assertEqual(scissions[0]["niveau"], 1)
        self.assertEqual(scissions[0]["decalage"], 10)
        self.assertEqual(scissions[1]["decalage"], -10)
        self.assertEqual(scissions[0]["rayon"], 40)

    def test_constantes_affichage_suivent_la_configuration_borne(self) -> None:
        """Verifie l application de la resolution et du mode borne."""

        with mock.patch.dict(
            os.environ,
            {
                "BORNE_RESOLUTION_X": "1280",
                "BORNE_RESOLUTION_Y": "1024",
                "BORNE_MODE_AFFICHAGE": "fenetre_sans_bordure",
            },
            clear=False,
        ):
            constantes_rechargees = importlib.reload(module_constantes)

        self.assertEqual(constantes_rechargees.SCREEN_WIDTH, 1280)
        self.assertEqual(constantes_rechargees.SCREEN_HEIGHT, 1024)
        self.assertEqual(constantes_rechargees.DISPLAY_FLAGS, pygame.NOFRAME)
        importlib.reload(module_constantes)


if __name__ == "__main__":
    unittest.main()
