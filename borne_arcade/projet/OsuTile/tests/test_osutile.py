"""Tests cibles du jeu OsuTile."""

from __future__ import annotations

import importlib
import math
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from unittest.mock import Mock

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

DOSSIER_JEU = Path(__file__).resolve().parents[1]
if str(DOSSIER_JEU) not in sys.path:
    sys.path.insert(0, str(DOSSIER_JEU))

from config import FALL_TIME, HIT_BOX_PIXEL, HIT_LINE_Y, SCREEN_HEIGHT, TILE_HEIGHT  # pylint: disable=import-error
from game import evaluer_frappe_tuile, load_beatmap  # pylint: disable=import-error
from main import ensure_maps_exported, lister_exports_manquants  # pylint: disable=import-error
from tile import Tile  # pylint: disable=import-error
import config as module_config  # pylint: disable=import-error


class TestOsuTile(unittest.TestCase):
    """Verifie les contrats critiques d OsuTile."""

    def test_load_beatmap_charge_une_carte_valide(self) -> None:
        """Verifie qu une carte Python exportee est chargee correctement."""

        with tempfile.TemporaryDirectory() as dossier_temporaire:
            racine = Path(dossier_temporaire)
            dossier_maps = racine / "maps"
            dossier_maps.mkdir()
            (dossier_maps / "Demo.py").write_text("beatmap = [(0, 1000), (2, 1500)]\n", encoding="utf-8")
            ancien_cwd = Path.cwd()
            os.chdir(racine)
            try:
                self.assertEqual(load_beatmap("Demo.osu"), [(0, 1000), (2, 1500)])
            finally:
                os.chdir(ancien_cwd)

    def test_ensure_maps_exported_ne_regenere_pas_les_cartes_existantes(self) -> None:
        """Verifie que seules les cartes manquantes sont regenerees."""

        with tempfile.TemporaryDirectory() as dossier_temporaire:
            racine = Path(dossier_temporaire)
            dossier_osu = racine / "beatmaps"
            dossier_maps = racine / "maps"
            dossier_osu.mkdir()
            dossier_maps.mkdir()
            (dossier_osu / "Existante.osu").write_text("contenu", encoding="utf-8")
            (dossier_osu / "Nouvelle.osu").write_text("contenu", encoding="utf-8")
            (dossier_maps / "Existante.py").write_text("beatmap = []\n", encoding="utf-8")
            executeur = Mock()

            manquants = lister_exports_manquants(str(dossier_osu), str(dossier_maps))
            ensure_maps_exported(str(dossier_osu), str(dossier_maps), executeur)

            self.assertEqual(manquants, [(str(dossier_osu / "Nouvelle.osu"), str(dossier_maps / "Nouvelle.py"))])
            executeur.assert_called_once_with(
                ["python3", "tools/export_map.py", str(dossier_osu / "Nouvelle.osu"), str(dossier_maps / "Nouvelle.py")],
                check=False,
            )

    def test_evaluer_frappe_tuile_distingue_perfect_et_miss(self) -> None:
        """Verifie le calcul pur de la fenetre de frappe."""

        tuile = Tile(0, 1000)
        temps_perfect = tuile.time + (HIT_LINE_Y * FALL_TIME * 1000 / SCREEN_HEIGHT)
        temps_miss = tuile.time + ((HIT_LINE_Y + HIT_BOX_PIXEL + TILE_HEIGHT + 20) * FALL_TIME * 1000 / SCREEN_HEIGHT)

        self.assertEqual(evaluer_frappe_tuile(tuile, temps_perfect), "Perfect")
        self.assertEqual(evaluer_frappe_tuile(tuile, temps_miss), "Miss")
        self.assertTrue(math.isfinite(temps_perfect))

    def test_configuration_affichage_utilise_la_resolution_borne(self) -> None:
        """Verifie que la configuration d affichage suit les variables borne."""

        with mock.patch.dict(
            os.environ,
            {
                "BORNE_RESOLUTION_X": "1280",
                "BORNE_RESOLUTION_Y": "1024",
                "BORNE_MODE_AFFICHAGE": "fenetre_sans_bordure",
            },
            clear=False,
        ):
            config_rechargee = importlib.reload(module_config)

        self.assertEqual(config_rechargee.SCREEN_WIDTH, 1280)
        self.assertEqual(config_rechargee.SCREEN_HEIGHT, 1024)
        self.assertEqual(config_rechargee.DISPLAY_FLAGS, config_rechargee.pygame.NOFRAME)
        importlib.reload(module_config)


if __name__ == "__main__":
    unittest.main()
