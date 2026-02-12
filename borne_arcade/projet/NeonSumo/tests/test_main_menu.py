"""Tests unitaires de configuration du menu titre NeonSumo."""

from __future__ import annotations

import importlib.util
import sys
import types
import unittest
from pathlib import Path

MODULE_NEON_SUMO = Path(__file__).resolve().parents[1]
if str(MODULE_NEON_SUMO) not in sys.path:
    sys.path.insert(0, str(MODULE_NEON_SUMO))

if "pygame" not in sys.modules:
    try:
        import pygame as _pygame  # noqa: F401
    except ModuleNotFoundError:
        sys.modules["pygame"] = types.SimpleNamespace()

CHEMIN_MAIN_NEON_SUMO = MODULE_NEON_SUMO / "main.py"
SPEC_MAIN_NEON_SUMO = importlib.util.spec_from_file_location("main_neon_sumo", CHEMIN_MAIN_NEON_SUMO)
if SPEC_MAIN_NEON_SUMO is None or SPEC_MAIN_NEON_SUMO.loader is None:
    raise ImportError("Impossible de charger le module main.py de NeonSumo.")
MODULE_MAIN_NEON_SUMO = importlib.util.module_from_spec(SPEC_MAIN_NEON_SUMO)
sys.modules[SPEC_MAIN_NEON_SUMO.name] = MODULE_MAIN_NEON_SUMO
SPEC_MAIN_NEON_SUMO.loader.exec_module(MODULE_MAIN_NEON_SUMO)
construire_parametres_menu_titre = MODULE_MAIN_NEON_SUMO.construire_parametres_menu_titre


class TestConfigurationMenuTitre(unittest.TestCase):
    """Valide la lecture des parametres de style du menu titre."""

    def test_construire_parametres_menu_titre_defauts(self) -> None:
        """Controle les valeurs par defaut quand la section est absente.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        parametres = construire_parametres_menu_titre({})
        self.assertEqual(parametres.nombre_lignes_grille, 16)
        self.assertEqual(parametres.opacite_voile, 126)
        self.assertEqual(parametres.taille_police_titre, 102)

    def test_construire_parametres_menu_titre_personnalise(self) -> None:
        """Controle la surcharge de configuration du menu titre.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        configuration = {
            "menu_titre": {
                "vitesse_animation": 2.4,
                "amplitude_oscillation": 14.0,
                "nombre_lignes_grille": 20,
                "epaisseur_lignes_grille": 3,
                "opacite_voile": 90,
                "taille_police_titre": 96,
                "taille_police_sous_titre": 30,
                "taille_police_info": 21,
            }
        }

        parametres = construire_parametres_menu_titre(configuration)
        self.assertEqual(parametres.vitesse_animation, 2.4)
        self.assertEqual(parametres.amplitude_oscillation, 14.0)
        self.assertEqual(parametres.nombre_lignes_grille, 20)
        self.assertEqual(parametres.epaisseur_lignes_grille, 3)
        self.assertEqual(parametres.opacite_voile, 90)
        self.assertEqual(parametres.taille_police_titre, 96)
        self.assertEqual(parametres.taille_police_sous_titre, 30)
        self.assertEqual(parametres.taille_police_info, 21)


if __name__ == "__main__":
    unittest.main()
