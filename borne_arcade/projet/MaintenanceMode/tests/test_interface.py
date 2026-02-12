"""Tests unitaires des comportements d interface MaintenanceMode."""

from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path

MODULE_MAINTENANCE = Path(__file__).resolve().parents[1]
if str(MODULE_MAINTENANCE) not in sys.path:
    sys.path.insert(0, str(MODULE_MAINTENANCE))

if "pygame" not in sys.modules:
    try:
        import pygame as _pygame  # noqa: F401
    except ModuleNotFoundError:
        sys.modules["pygame"] = types.SimpleNamespace()

from main import (  # pylint: disable=import-error
    EtatInterface,
    activer_auto_scroll_journal,
    ajouter_ligne_journal,
    ajuster_decalage_journal,
    calculer_decalage_max_journal,
)


class TestInterfaceMaintenanceMode(unittest.TestCase):
    """Verifie la logique de defilement du journal temps reel."""

    def test_calculer_decalage_max_journal(self) -> None:
        """Controle le calcul du decalage maximal selon la fenetre visible.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        self.assertEqual(calculer_decalage_max_journal(10, 4), 6)
        self.assertEqual(calculer_decalage_max_journal(3, 6), 0)

    def test_ajuster_decalage_journal_active_mode_manuel(self) -> None:
        """Controle l entree en mode manuel et le bornage du decalage.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        etat = EtatInterface()
        etat.journal_visible = [f"ligne {index}" for index in range(20)]

        ajuster_decalage_journal(etat, 7, len(etat.journal_visible), 5)

        self.assertFalse(etat.auto_scroll_journal)
        self.assertEqual(etat.decalage_lignes_journal, 7)

        ajuster_decalage_journal(etat, 99, len(etat.journal_visible), 5)
        self.assertEqual(etat.decalage_lignes_journal, 15)

    def test_ajuster_decalage_journal_reactive_auto_scroll_en_bas(self) -> None:
        """Controle le retour automatique quand le decalage revient a zero.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        etat = EtatInterface(auto_scroll_journal=False, decalage_lignes_journal=4)
        etat.journal_visible = [f"ligne {index}" for index in range(12)]

        ajuster_decalage_journal(etat, -4, len(etat.journal_visible), 6)

        self.assertTrue(etat.auto_scroll_journal)
        self.assertEqual(etat.decalage_lignes_journal, 0)

    def test_ajouter_ligne_journal_borne_historique(self) -> None:
        """Controle que le journal conserve un historique borne et coherent.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        etat = EtatInterface(auto_scroll_journal=False, decalage_lignes_journal=8)
        etat.journal_visible = [f"ligne {index}" for index in range(12)]

        ajouter_ligne_journal(etat, "nouvelle", limite_lignes=10, nombre_lignes_visibles=5)

        self.assertEqual(len(etat.journal_visible), 10)
        self.assertEqual(etat.journal_visible[-1], "nouvelle")
        self.assertEqual(etat.decalage_lignes_journal, 5)

        activer_auto_scroll_journal(etat)
        self.assertTrue(etat.auto_scroll_journal)
        self.assertEqual(etat.decalage_lignes_journal, 0)


if __name__ == "__main__":
    unittest.main()
