"""Tests unitaires du module operations du mode maintenance."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE_MAINTENANCE = Path(__file__).resolve().parents[1]
if str(MODULE_MAINTENANCE) not in sys.path:
    sys.path.insert(0, str(MODULE_MAINTENANCE))

import operations  # pylint: disable=import-error


class TestOperationsMaintenance(unittest.TestCase):
    """Valide les comportements critiques des operations maintenance."""

    def test_executer_commande_diffuse_sortie_en_temps_reel(self) -> None:
        """Controle que les lignes de sortie sont diffusees a mesure de l execution.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        lignes_capturees: list[str] = []
        commande = [
            sys.executable,
            "-c",
            "import time; print('ligne_a'); time.sleep(0.2); print('ligne_b')",
        ]

        succes, sortie = operations.executer_commande(
            commande,
            Path.cwd(),
            timeout_secondes=5,
            consommateur_sortie=lignes_capturees.append,
            intervalle_lecture_secondes=0.05,
        )

        self.assertTrue(succes)
        self.assertIn("ligne_a", sortie)
        self.assertIn("ligne_b", sortie)
        self.assertGreaterEqual(len(lignes_capturees), 2)
        self.assertIn("ligne_a", lignes_capturees)
        self.assertIn("ligne_b", lignes_capturees)

    def test_executer_commande_timeout_retourne_message_actionnable(self) -> None:
        """Controle le message de timeout pour l exploitation.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        commande = [sys.executable, "-c", "import time; time.sleep(2)"]
        succes, sortie = operations.executer_commande(
            commande,
            Path.cwd(),
            timeout_secondes=1,
            intervalle_lecture_secondes=0.05,
        )

        self.assertFalse(succes)
        self.assertIn("Commande expiree", sortie)
        self.assertIn("Action recommandee", sortie)

    def test_executer_operation_inconnue_journalise_erreur(self) -> None:
        """Controle qu une operation inconnue genere un journal utile.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        lignes_capturees: list[str] = []
        configuration = operations.charger_configuration(Path("config_introuvable.json"))

        with tempfile.TemporaryDirectory() as dossier_temporaire:
            racine_temporaire = Path(dossier_temporaire)
            with patch.object(operations, "obtenir_racine_projet", return_value=racine_temporaire):
                succes, message, chemin_journal = operations.executer_operation(
                    "operation_inconnue",
                    configuration,
                    lignes_capturees.append,
                )
                self.assertFalse(succes)
                self.assertIn("Operation inconnue", message)
                self.assertTrue(chemin_journal.exists())
                contenu_journal = chemin_journal.read_text(encoding="utf-8")
                self.assertIn("Operation inconnue", contenu_journal)
                self.assertTrue(any("Operation inconnue" in ligne for ligne in lignes_capturees))

    def test_selectionner_dossier_logs_fallback_si_racine_non_ecrivable(self) -> None:
        """Controle la selection de dossier logs avec repli sur un second candidat.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        dossier_principal = Path("/racine/inaccessible")
        dossier_secours = Path("/tmp/maintenance_mode_logs_test")

        with (
            patch.object(
                operations,
                "lister_dossiers_logs_candidats",
                return_value=[dossier_principal, dossier_secours],
            ),
            patch.object(
                operations,
                "tester_ecriture_dossier_logs",
                side_effect=[False, True],
            ),
        ):
            dossier_selectionne = operations.selectionner_dossier_logs(Path("/projet"))
            self.assertEqual(dossier_selectionne, dossier_secours)

    def test_executer_operation_capture_exception_inattendue(self) -> None:
        """Controle qu une exception interne retourne un echec actionnable.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        lignes_capturees: list[str] = []
        configuration = operations.charger_configuration(Path("config_introuvable.json"))

        with tempfile.TemporaryDirectory() as dossier_temporaire:
            racine_temporaire = Path(dossier_temporaire)
            with (
                patch.object(operations, "obtenir_racine_projet", return_value=racine_temporaire),
                patch.object(operations, "operation_diagnostic", side_effect=RuntimeError("boom")),
            ):
                succes, message, chemin_journal = operations.executer_operation(
                    "diagnostic",
                    configuration,
                    lignes_capturees.append,
                )

                self.assertFalse(succes)
                self.assertIn("Operation interrompue", message)
                self.assertIn("Action recommandee", message)
                self.assertTrue(chemin_journal.exists())
                self.assertTrue(any("ERREUR: Operation interrompue" in ligne for ligne in lignes_capturees))

    def test_lister_operations_contient_reset_pre_requis(self) -> None:
        """Controle la presence de l operation reset dans le catalogue.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        operations_disponibles = operations.lister_operations()
        identifiants = [operation["id"] for operation in operations_disponibles]
        self.assertIn("reset_pre_requis", identifiants)
        self.assertIn("git_retour_precedent", identifiants)

    def test_extraire_premiere_ligne_sortie_gere_sortie_vide(self) -> None:
        """Controle l extraction robuste de premiere ligne de sortie.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        self.assertEqual(operations.extraire_premiere_ligne_sortie(""), "(sortie indisponible)")
        self.assertEqual(
            operations.extraire_premiere_ligne_sortie("ligne1\nligne2"),
            "ligne1",
        )

    def test_operation_diagnostic_tolere_sortie_vide_si_pre_requis_absents(self) -> None:
        """Controle la robustesse du diagnostic quand des outils manquent.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        configuration = operations.charger_configuration(Path("config_introuvable.json"))
        lignes_capturees: list[str] = []
        with tempfile.TemporaryDirectory() as dossier_temporaire:
            racine_temporaire = Path(dossier_temporaire)
            with (
                patch.object(operations, "diagnostiquer_pre_requis_borne", return_value=False),
                patch.object(operations, "executer_commande", return_value=(False, "")),
            ):
                succes, message, _ = operations.operation_diagnostic(
                    configuration,
                    racine_temporaire,
                    racine_temporaire / "journal.log",
                    lignes_capturees.append,
                )

                self.assertFalse(succes)
                self.assertIn("Diagnostic termine avec erreurs", message)
                self.assertTrue(any("(sortie indisponible)" in ligne for ligne in lignes_capturees))

    def test_operation_reset_pre_requis_refuse_sans_sudo(self) -> None:
        """Controle le message actionnable sans privileges sudo non interactifs.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        configuration = operations.charger_configuration(Path("config_introuvable.json"))
        lignes_capturees: list[str] = []
        with tempfile.TemporaryDirectory() as dossier_temporaire:
            racine_temporaire = Path(dossier_temporaire)
            with patch.object(operations, "obtenir_prefixe_privileges_systeme", return_value=None):
                succes, message, _ = operations.operation_reset_pre_requis(
                    configuration,
                    racine_temporaire,
                    racine_temporaire / "journal.log",
                    lignes_capturees.append,
                )
                self.assertFalse(succes)
                self.assertIn("sudo non disponible", message)
                self.assertTrue(any("Action recommandee" in ligne for ligne in lignes_capturees))

    def test_operation_git_pull_refuse_si_git_absent(self) -> None:
        """Controle le message actionnable si git est absent.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        configuration = operations.charger_configuration(Path("config_introuvable.json"))
        lignes_capturees: list[str] = []
        with tempfile.TemporaryDirectory() as dossier_temporaire:
            racine_temporaire = Path(dossier_temporaire)
            with patch.object(operations.shutil, "which", return_value=None):
                succes, message, _ = operations.operation_git_pull(
                    configuration,
                    racine_temporaire,
                    racine_temporaire / "journal.log",
                    lignes_capturees.append,
                )
                self.assertFalse(succes)
                self.assertIn("git introuvable", message)
                self.assertTrue(any("Action recommandee" in ligne for ligne in lignes_capturees))

    def test_operation_git_retour_precedent_refuse_si_depot_modifie(self) -> None:
        """Controle le refus de rollback quand le depot n est pas propre.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        configuration = operations.charger_configuration(Path("config_introuvable.json"))
        lignes_capturees: list[str] = []
        with tempfile.TemporaryDirectory() as dossier_temporaire:
            racine_temporaire = Path(dossier_temporaire)
            resultat_statut = type("Resultat", (), {"returncode": 0, "stdout": " M fichier.py\n"})()
            with (
                patch.object(operations, "verifier_git_disponible", return_value=True),
                patch.object(operations, "executer_commande", return_value=(True, "ok")),
                patch.object(operations.subprocess, "run", return_value=resultat_statut),
            ):
                succes, message, _ = operations.operation_git_retour_precedent(
                    configuration,
                    racine_temporaire,
                    racine_temporaire / "journal.log",
                    lignes_capturees.append,
                )
                self.assertFalse(succes)
                self.assertIn("modifications locales detectees", message)

    def test_operation_git_retour_precedent_succes(self) -> None:
        """Controle l orchestration nominale du rollback git.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        configuration = operations.charger_configuration(Path("config_introuvable.json"))
        lignes_capturees: list[str] = []
        with tempfile.TemporaryDirectory() as dossier_temporaire:
            racine_temporaire = Path(dossier_temporaire)
            resultat_statut = type("Resultat", (), {"returncode": 0, "stdout": ""})()
            with (
                patch.object(operations, "verifier_git_disponible", return_value=True),
                patch.object(operations, "executer_commande", return_value=(True, "ok")) as mock_exec,
                patch.object(operations.subprocess, "run", return_value=resultat_statut),
            ):
                succes, message, _ = operations.operation_git_retour_precedent(
                    configuration,
                    racine_temporaire,
                    racine_temporaire / "journal.log",
                    lignes_capturees.append,
                )

                self.assertTrue(succes)
                self.assertIn("Retour commit precedent termine", message)
                self.assertEqual(mock_exec.call_count, 3)

    def test_operation_reset_pre_requis_enchaine_commandes_et_nettoyage(self) -> None:
        """Controle l orchestration complete du reset prerequis.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        configuration = operations.charger_configuration(Path("config_introuvable.json"))
        lignes_capturees: list[str] = []
        with tempfile.TemporaryDirectory() as dossier_temporaire:
            racine_temporaire = Path(dossier_temporaire)

            with (
                patch.object(operations, "obtenir_prefixe_privileges_systeme", return_value=["sudo", "-n"]),
                patch.object(operations, "executer_commande", return_value=(True, "ok")) as mock_exec,
                patch.object(
                    operations,
                    "nettoyer_artefacts_reset",
                    return_value=(True, "Nettoyage local termine."),
                ) as mock_nettoyage,
            ):
                succes, message, _ = operations.operation_reset_pre_requis(
                    configuration,
                    racine_temporaire,
                    racine_temporaire / "journal.log",
                    lignes_capturees.append,
                )

                self.assertTrue(succes)
                self.assertIn("Reset prerequis termine", message)
                self.assertEqual(mock_exec.call_count, 3)
                mock_nettoyage.assert_called_once_with(racine_temporaire, lignes_capturees.append)


if __name__ == "__main__":
    unittest.main()
