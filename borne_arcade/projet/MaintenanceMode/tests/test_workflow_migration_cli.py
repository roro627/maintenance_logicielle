"""Tests unitaires du CLI de workflow de migration."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


def charger_module_workflow_migration():
    """Charge dynamiquement le module CLI du workflow migration.

    Args:
        Aucun.

    Returns:
        Module Python charge depuis `scripts/migration/workflow_migration.py`.
    """

    chemin_module = Path(__file__).resolve().parents[4] / "scripts" / "migration" / "workflow_migration.py"
    spec = importlib.util.spec_from_file_location("workflow_migration_test", chemin_module)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestWorkflowMigrationCli(unittest.TestCase):
    """Valide le contrat public du CLI de workflow migration."""

    @classmethod
    def setUpClass(cls) -> None:
        """Charge le module cible une fois pour toutes les assertions.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        cls.module = charger_module_workflow_migration()

    def test_versions_installees_format_json(self) -> None:
        """Controle la sortie JSON stable des versions installees.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        cibles = [
            {
                "id": "java17",
                "titre": "Java 17",
                "description": "JDK",
                "type": "paquet_apt",
                "version_installee": "17.0.8",
                "version_candidate": "17.0.9",
                "migration_disponible": True,
                "resume_migration": "Migration disponible",
                "commande_migration_lisible": "apt-get install -y openjdk-17-jdk",
                "supportee_sur_hote": True,
                "raison_indisponibilite": "",
                "version_paquet_installee": "17.0.8",
            }
        ]

        sortie = io.StringIO()
        with (
            patch.object(self.module.operations, "collecter_cibles_migration", return_value=cibles),
            patch.object(sys, "argv", ["workflow_migration.py", "versions-installees", "--format", "json"]),
            contextlib.redirect_stdout(sortie),
        ):
            code = self.module.main()

        self.assertEqual(code, 0)
        contenu = json.loads(sortie.getvalue())
        self.assertEqual(contenu[0]["id"], "java17")
        self.assertEqual(contenu[0]["version_paquet_installee"], "17.0.8")

    def test_preparer_ia_transmet_cible_et_dossier_sortie(self) -> None:
        """Controle la propagation du contexte cible + dossier de sortie.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        appels: list[tuple[str, dict[str, object] | None]] = []

        def faux_executer(operation_id: str, contexte_operation: dict[str, object] | None = None) -> int:
            """Capture l appel du CLI sans executer l operation reelle.

            Args:
                operation_id: Identifiant de l operation.
                contexte_operation: Contexte transmis par le parseur.

            Returns:
                Code de retour force.
            """

            appels.append((operation_id, contexte_operation))
            return 0

        with (
            patch.object(self.module, "executer_operation_cli", side_effect=faux_executer),
            patch.object(
                sys,
                "argv",
                [
                    "workflow_migration.py",
                    "preparer-ia",
                    "--cible",
                    "java17",
                    "--dossier-sortie",
                    "logs/tests",
                ],
            ),
        ):
            code = self.module.main()

        self.assertEqual(code, 0)
        self.assertEqual(appels[0][0], "preparer_placeholder_ia_migration")
        self.assertEqual(appels[0][1]["cible_migration_id"], "java17")
        self.assertEqual(appels[0][1]["dossier_sortie"], "logs/tests")

    def test_qualite_transmet_cible_selectionnee(self) -> None:
        """Controle la propagation de la cible a l operation qualite.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        appels: list[tuple[str, dict[str, object] | None]] = []

        def faux_executer(operation_id: str, contexte_operation: dict[str, object] | None = None) -> int:
            """Capture l appel qualite sans lancer la suite reelle.

            Args:
                operation_id: Identifiant de l operation.
                contexte_operation: Contexte associe.

            Returns:
                Code de retour force.
            """

            appels.append((operation_id, contexte_operation))
            return 0

        with (
            patch.object(self.module, "executer_operation_cli", side_effect=faux_executer),
            patch.object(sys, "argv", ["workflow_migration.py", "qualite", "--cible", "java17"]),
        ):
            code = self.module.main()

        self.assertEqual(code, 0)
        self.assertEqual(appels[0][0], "relancer_qualite_complete")
        self.assertEqual(appels[0][1]["cible_migration_id"], "java17")


if __name__ == "__main__":
    unittest.main()
