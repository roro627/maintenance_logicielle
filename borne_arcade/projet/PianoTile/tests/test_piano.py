"""Tests unitaires de robustesse audio pour PianoTile."""

from __future__ import annotations

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
    from ui.utils.piano import Piano  # pylint: disable=import-error
else:
    Piano = None


class FauxWindowManager:
    """Fournit la selection de musique minimale pour les tests Piano."""

    def getMusicSelect(self) -> str:
        """Retourne une musique de test.

        Args:
            Aucun.

        Returns:
            Nom de musique.
        """

        return "Believer"


class FauxGameView:
    """Expose uniquement le contrat necessaire a Piano."""

    def __init__(self) -> None:
        """Initialise un faux gameview de test.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        self.__window_manager = FauxWindowManager()

    def getWindowManager(self) -> FauxWindowManager:
        """Retourne un faux window manager.

        Args:
            Aucun.

        Returns:
            FauxWindowManager.
        """

        return self.__window_manager


@unittest.skipIf(pygame is None, "pygame indisponible dans cet environnement de test")
class TestPianoRobustesseAudio(unittest.TestCase):
    """Valide les garde-fous audio non bloquants du module Piano."""

    def test_play_echec_audio_renvoie_message_actionnable(self) -> None:
        """Controle qu un echec audio ne plante pas le jeu.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        with patch.object(Piano, "generate_notes", return_value=[]):
            piano = Piano(FauxGameView())

        with (
            patch.object(Piano, "obtenir_temps_systeme_secondes", return_value=12.0),
            patch("ui.utils.piano.pygame.mixer.get_init", return_value=False),
            patch("ui.utils.piano.pygame.mixer.init", side_effect=pygame.error("audio indisponible")),
        ):
            piano.play()

        self.assertFalse(piano.estLectureAudioActive())
        self.assertIn("Action recommandee", piano.getDerniereErreurAudio())

    def test_get_current_time_fallback_sans_audio(self) -> None:
        """Controle le chronometrage de secours sans lecture audio.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        with patch.object(Piano, "generate_notes", return_value=[]):
            piano = Piano(FauxGameView())

        with (
            patch.object(Piano, "obtenir_temps_systeme_secondes", side_effect=[10.0, 10.75]),
            patch("ui.utils.piano.pygame.mixer.get_init", return_value=False),
            patch("ui.utils.piano.pygame.mixer.init", side_effect=pygame.error("audio indisponible")),
        ):
            piano.play()
            temps = piano.getCurrentTime()

        self.assertAlmostEqual(temps, 0.75, places=2)


if __name__ == "__main__":
    unittest.main()
