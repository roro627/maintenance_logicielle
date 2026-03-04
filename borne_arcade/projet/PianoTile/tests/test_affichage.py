"""Tests unitaires de configuration d affichage pour PianoTile."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    import pygame
except ModuleNotFoundError:
    pygame = None

MODULE_PIANOTILE = Path(__file__).resolve().parents[1]
if str(MODULE_PIANOTILE) not in sys.path:
    sys.path.insert(0, str(MODULE_PIANOTILE))

if pygame is not None:
    from ui.manager.affichage_borne import (  # pylint: disable=import-error
        MODE_AFFICHAGE_FENETRE_SANS_BORDURE,
        determiner_drapeaux_fenetre,
        determiner_mode_affichage,
        determiner_resolution_borne,
    )
else:
    MODE_AFFICHAGE_FENETRE_SANS_BORDURE = None
    determiner_drapeaux_fenetre = None
    determiner_mode_affichage = None
    determiner_resolution_borne = None


@unittest.skipIf(pygame is None, "pygame indisponible dans cet environnement de test")
class TestAffichagePianoTile(unittest.TestCase):
    """Verifie le parametrage borne de l affichage PianoTile."""

    def test_resolution_borne_est_prioritaire(self) -> None:
        """Controle la lecture des dimensions borne depuis l environnement."""

        with patch.dict(
            os.environ,
            {
                "BORNE_RESOLUTION_X": "1280",
                "BORNE_RESOLUTION_Y": "1024",
                "BORNE_MODE_AFFICHAGE": "fenetre_sans_bordure",
            },
            clear=False,
        ):
            largeur, hauteur = determiner_resolution_borne()
            mode_affichage = determiner_mode_affichage()

        self.assertEqual(largeur, 1280)
        self.assertEqual(hauteur, 1024)
        self.assertEqual(mode_affichage, MODE_AFFICHAGE_FENETRE_SANS_BORDURE)
        self.assertEqual(determiner_drapeaux_fenetre(mode_affichage), pygame.DOUBLEBUF | pygame.NOFRAME)


if __name__ == "__main__":
    unittest.main()
