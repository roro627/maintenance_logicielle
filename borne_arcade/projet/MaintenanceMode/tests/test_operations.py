"""Tests unitaires du module operations du mode maintenance."""

from __future__ import annotations

import json
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

    def test_construire_environnement_codex_utilise_base_url_ollama_distante(self) -> None:
        """Controle la normalisation de l URL OSS distante pour Codex.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        configuration_assistant = {
            "codex": {"fournisseur_local": "ollama"},
            "ollama": {"base_url": "http://10.22.28.190:11434"},
        }

        environnement = operations.construire_environnement_codex_migration(configuration_assistant)

        self.assertEqual(environnement["CODEX_OSS_BASE_URL"], "http://10.22.28.190:11434/v1")

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

    def test_lister_paquets_reset_ignore_python3_meme_si_mal_configure(self) -> None:
        """Controle que python3 ne peut jamais etre cible par le reset prerequis.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        with (
            patch.object(operations, "PAQUETS_RESET_NON_SYSTEME_BORNE", ["python3", "checkstyle"]),
            patch.object(operations, "paquet_systeme_installe", return_value=True),
        ):
            paquets = operations.lister_paquets_reset_non_systeme_installes()
            self.assertEqual(paquets, ["checkstyle"])
            self.assertNotIn("python3", paquets)

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
                patch.object(
                    operations,
                    "lister_paquets_reset_non_systeme_installes",
                    return_value=["checkstyle", "pylint"],
                ),
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
                self.assertIn("mode sur", message)
                self.assertEqual(mock_exec.call_count, 2)
                commandes = [appel.args[0] for appel in mock_exec.call_args_list]
                self.assertTrue(any("remove" in commande for commande in commandes))
                self.assertFalse(any("autoremove" in commande for commande in commandes))
                mock_nettoyage.assert_called_once_with(racine_temporaire, lignes_capturees.append)

    def test_operation_reset_pre_requis_sans_paquet_purgeable_execute_clean_uniquement(self) -> None:
        """Controle le reset sur quand aucun paquet non-systeme n est installe.

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
                patch.object(operations, "lister_paquets_reset_non_systeme_installes", return_value=[]),
                patch.object(operations, "executer_commande", return_value=(True, "ok")) as mock_exec,
                patch.object(
                    operations,
                    "nettoyer_artefacts_reset",
                    return_value=(True, "Nettoyage local termine."),
                ),
            ):
                succes, message, _ = operations.operation_reset_pre_requis(
                    configuration,
                    racine_temporaire,
                    racine_temporaire / "journal.log",
                    lignes_capturees.append,
                )

                self.assertTrue(succes)
                self.assertIn("mode sur", message)
                self.assertEqual(mock_exec.call_count, 1)
                premiere_commande = mock_exec.call_args_list[0].args[0]
                self.assertIn("clean", premiere_commande)

    def test_collecter_cibles_migration_indique_hote_non_supporte(self) -> None:
        """Controle l enrichissement d une cible quand l hote n est pas compatible apt.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        definition = {
            "id": "java17",
            "titre": "Java 17",
            "description": "JDK cible",
            "type": "paquet_apt",
            "paquet_apt": "openjdk-17-jdk",
            "commande_version_installee": ["java", "-version"],
            "commandes_migration": [["apt-get", "install", "-y", "openjdk-17-jdk"]],
        }

        with (
            patch.object(operations, "charger_configuration_cibles_migration", return_value=[definition]),
            patch.object(
                operations,
                "decrire_support_hote_migration_apt",
                return_value=(False, "Migration reservee a Debian."),
            ),
            patch.object(operations, "obtenir_version_humaine_installee", return_value="java version 20"),
        ):
            cibles = operations.collecter_cibles_migration(Path.cwd())

        self.assertEqual(len(cibles), 1)
        self.assertFalse(cibles[0]["supportee_sur_hote"])
        self.assertEqual(cibles[0]["raison_indisponibilite"], "Migration reservee a Debian.")
        self.assertEqual(cibles[0]["version_installee"], "java version 20")
        self.assertFalse(cibles[0]["migration_disponible"])

    def test_decrire_support_hote_migration_apt_refuse_ubuntu(self) -> None:
        """Controle que la migration apt refuse un hote Ubuntu meme si apt est present.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        with (
            patch.object(operations, "os", create=True) as faux_os,
            patch.object(operations.shutil, "which", return_value="/usr/bin/factice"),
            patch.object(
                operations,
                "lire_variables_os_release",
                return_value={"ID": "ubuntu", "PRETTY_NAME": "Ubuntu 24.04.2 LTS"},
            ),
        ):
            faux_os.name = "posix"
            supportee, raison = operations.decrire_support_hote_migration_apt()

        self.assertFalse(supportee)
        self.assertIn("Ubuntu 24.04.2 LTS", raison)

    def test_verifier_etat_migration_autorise_commit_courant_different_pour_qualite(self) -> None:
        """Controle que l etape qualite peut reutiliser une session apres un nouveau commit.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        with tempfile.TemporaryDirectory() as dossier_temporaire:
            racine_temporaire = Path(dossier_temporaire)
            operations.enregistrer_etat_migration(
                racine_temporaire,
                {
                    "cible_id": "java17",
                    "titre": "Java 17",
                    "commit_git": "ancien_commit",
                    "migration_appliquee": True,
                    "placeholder_ia_genere": True,
                    "qualite_verifiee": False,
                },
            )

            with patch.object(
                operations,
                "capturer_contexte_git",
                return_value={"branche_git": "migration/java17", "commit_git": "nouveau_commit", "depot_propre": True},
            ):
                succes, message, etat = operations.verifier_etat_migration_pour_cible(
                    racine_temporaire,
                    {"id": "java17"},
                    exiger_migration=True,
                    exiger_assistant_ia=True,
                    autoriser_commit_courant_different=True,
                )

        self.assertTrue(succes)
        self.assertEqual(message, "")
        self.assertEqual(etat["commit_git"], "ancien_commit")

    def test_etat_migration_persistant_roundtrip(self) -> None:
        """Controle la persistence de l etat de migration sur disque.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        with tempfile.TemporaryDirectory() as dossier_temporaire:
            racine_temporaire = Path(dossier_temporaire)
            etat = {
                "cible_id": "java17",
                "titre": "Java 17",
                "migration_appliquee": True,
            }

            chemin_etat = operations.enregistrer_etat_migration(racine_temporaire, etat)
            self.assertTrue(chemin_etat.exists())
            self.assertEqual(operations.charger_etat_migration(racine_temporaire)["cible_id"], "java17")
            self.assertTrue(operations.effacer_etat_migration_obsolete(racine_temporaire))
            self.assertEqual(operations.charger_etat_migration(racine_temporaire), {})

    def test_operation_appliquer_migration_enregistre_session(self) -> None:
        """Controle la creation d une session persistante apres migration appliquee.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        configuration = operations.charger_configuration(Path("config_introuvable.json"))
        cible = {
            "id": "java17",
            "titre": "Java 17",
            "version_installee": "17.0.0",
            "version_candidate": "17.0.8",
            "migration_disponible": True,
            "supportee_sur_hote": True,
            "commandes_migration": [["apt-get", "install", "-y", "openjdk-17-jdk"]],
        }

        with tempfile.TemporaryDirectory() as dossier_temporaire:
            racine_temporaire = Path(dossier_temporaire)
            with (
                patch.object(operations, "obtenir_cible_migration_contextualisee", return_value=(cible, [cible])),
                patch.object(operations, "obtenir_prefixe_privileges_systeme", return_value=[]),
                patch.object(operations, "executer_commande", return_value=(True, "ok")),
                patch.object(
                    operations,
                    "capturer_contexte_git",
                    return_value={"branche_git": "migration/java17", "commit_git": "abc123", "depot_propre": True},
                ),
            ):
                succes, message, _ = operations.operation_appliquer_migration_cible(
                    configuration,
                    racine_temporaire,
                    racine_temporaire / "journal.log",
                    lambda _: None,
                    {"cible_migration_id": "java17"},
                )

            self.assertTrue(succes)
            self.assertIn("Session", message)
            etat = operations.charger_etat_migration(racine_temporaire)
            self.assertTrue(etat["migration_appliquee"])
            self.assertEqual(etat["cible_id"], "java17")
            self.assertEqual(etat["commit_git"], "abc123")

    def test_operation_preparer_assistant_ia_genere_brief_reponse_et_trace(self) -> None:
        """Controle la generation du brief, de la reponse et de la trace IA.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        configuration = operations.charger_configuration(Path("config_introuvable.json"))
        cible = {
            "id": "java17",
            "titre": "Java 17",
            "description": "JDK cible",
            "type": "paquet_apt",
            "version_installee": "17.0.0",
            "version_candidate": "17.0.8",
            "commande_migration_lisible": "apt-get install -y openjdk-17-jdk",
        }
        configuration_assistant = {
            "codex": {
                "commande": "codex",
                "modele": "qwen3:8b",
                "fournisseur_local": "ollama",
                "utiliser_provider_oss": True,
                "activer_recherche_web": True,
                "sortie_json": True,
                "couleur": "never",
                "politique_approbation": "never",
                "sandbox": "danger-full-access",
                "ignorer_verification_git": False,
                "arguments_supplementaires": [],
            },
            "ollama": {"base_url": "http://10.22.28.190:11434"},
            "mcp": {
                "context7": {
                    "actif": True,
                    "commande": "npx",
                    "arguments": ["-y", "@upstash/context7-mcp"],
                    "delai_demarrage_secondes": 120,
                    "timeout_outil_secondes": 300,
                }
            },
            "prompt": {"chemin_modele": "config/prompt_migration_ia.md"},
        }

        def faux_executer_commande(
            commande: list[str],
            repertoire_travail: Path,
            timeout_secondes: int,
            consommateur_sortie=None,
            intervalle_lecture_secondes: float = 0.1,
            entree_texte: str | None = None,
            variables_environnement: dict[str, str] | None = None,
        ) -> tuple[bool, str]:
            """Simule une execution Codex CLI avec flux JSONL.

            Args:
                commande: Commande recue.
                repertoire_travail: Dossier de travail cible.
                timeout_secondes: Timeout demande.
                consommateur_sortie: Callback temps reel.
                intervalle_lecture_secondes: Intervalle de lecture.
                entree_texte: Prompt envoye sur stdin.

            Returns:
                Statut de succes et sortie brute.
            """

            _ = repertoire_travail, timeout_secondes, intervalle_lecture_secondes
            self.assertNotIn("--search", commande)
            self.assertIn("--local-provider", commande)
            self.assertIn("ollama", commande)
            self.assertIn("-m", commande)
            self.assertIn("qwen3:8b", commande)
            self.assertIn("--dangerously-bypass-approvals-and-sandbox", commande)
            self.assertNotIn("-a", commande)
            self.assertIsNotNone(entree_texte)
            assert entree_texte is not None
            self.assertIn("brief_ia_migration_java17", entree_texte)
            self.assertIsNotNone(variables_environnement)
            assert variables_environnement is not None
            self.assertEqual(
                variables_environnement.get("CODEX_OSS_BASE_URL"),
                "http://10.22.28.190:11434/v1",
            )

            chemin_reponse = Path(commande[commande.index("-o") + 1])
            chemin_reponse.write_text("Resume final IA\nTests relances\n", encoding="utf-8")
            for evenement in [
                {"type": "thread.started", "thread_id": "thread_test"},
                {"type": "turn.started"},
                {"type": "item.completed", "item": {"type": "reasoning", "text": "Analyse du depot"}},
                {"type": "item.completed", "item": {"type": "agent_message", "text": "Resume final IA"}},
                {"type": "turn.completed", "usage": {"input_tokens": 10, "output_tokens": 5}},
            ]:
                if consommateur_sortie is not None:
                    consommateur_sortie(json.dumps(evenement))
            return True, "ok"

        with tempfile.TemporaryDirectory() as dossier_temporaire:
            racine_temporaire = Path(dossier_temporaire)
            operations.enregistrer_etat_migration(
                racine_temporaire,
                {
                    "cible_id": "java17",
                    "titre": "Java 17",
                    "version_installee": "17.0.0",
                    "version_candidate": "17.0.8",
                    "branche_git": "migration/java17",
                    "commit_git": "abc123",
                    "migration_appliquee": True,
                    "placeholder_ia_genere": False,
                    "chemin_placeholder_md": "",
                    "chemin_placeholder_json": "",
                    "chemin_reponse_ia": "",
                    "chemin_transcription_ia_jsonl": "",
                    "qualite_verifiee": False,
                    "chemin_rapport_qualite": "",
                    "horodatage_derniere_etape": "2026-03-02T10:00:00",
                },
            )

            with (
                patch.object(operations, "obtenir_cible_migration_contextualisee", return_value=(cible, [cible])),
                patch.object(
                    operations,
                    "capturer_contexte_git",
                    return_value={"branche_git": "migration/java17", "commit_git": "abc123", "depot_propre": True},
                ),
                patch.object(operations, "charger_configuration_assistant_ia", return_value=configuration_assistant),
                patch.object(
                    operations,
                    "charger_modele_prompt_assistant_ia",
                    return_value="Contexte {{CHEMIN_BRIEF_JSON}}\nValidation\n{{COMMANDES_QUALITE}}",
                ),
                patch.object(operations, "verifier_outils_assistant_ia", return_value=(True, "")),
                patch.object(operations, "executer_commande", side_effect=faux_executer_commande),
            ):
                succes, message, _ = operations.operation_preparer_placeholder_ia_migration(
                    configuration,
                    racine_temporaire,
                    racine_temporaire / "journal.log",
                    lambda _: None,
                    {
                        "cible_migration_id": "java17",
                        "dossier_sortie": str(racine_temporaire),
                    },
                )

            self.assertTrue(succes)
            self.assertIn("Reponse:", message)
            self.assertEqual(len(list(racine_temporaire.glob("brief_ia_migration_java17_*.md"))), 1)
            self.assertEqual(len(list(racine_temporaire.glob("brief_ia_migration_java17_*.json"))), 1)
            self.assertEqual(len(list(racine_temporaire.glob("reponse_ia_migration_java17_*.md"))), 1)
            self.assertEqual(len(list(racine_temporaire.glob("transcription_ia_migration_java17_*.jsonl"))), 1)
            etat = operations.charger_etat_migration(racine_temporaire)
            self.assertTrue(etat["placeholder_ia_genere"])
            self.assertTrue(Path(str(etat["chemin_placeholder_md"])).exists())
            self.assertTrue(Path(str(etat["chemin_placeholder_json"])).exists())
            self.assertTrue(Path(str(etat["chemin_reponse_ia"])).exists())
            self.assertTrue(Path(str(etat["chemin_transcription_ia_jsonl"])).exists())
            brief = json.loads(Path(str(etat["chemin_placeholder_json"])).read_text(encoding="utf-8"))
            self.assertEqual(brief["assistant_ia"]["modele"], "qwen3:8b")
            self.assertEqual(brief["backend_ia"]["backend"], "codex")

    def test_operation_preparer_assistant_ia_refuse_si_outils_absents(self) -> None:
        """Controle le refus propre si Codex/Ollama sont indisponibles.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        configuration = operations.charger_configuration(Path("config_introuvable.json"))
        cible = {
            "id": "java17",
            "titre": "Java 17",
            "description": "JDK cible",
            "type": "paquet_apt",
            "version_installee": "17.0.0",
            "version_candidate": "17.0.8",
            "commande_migration_lisible": "apt-get install -y openjdk-17-jdk",
        }

        with tempfile.TemporaryDirectory() as dossier_temporaire:
            racine_temporaire = Path(dossier_temporaire)
            operations.enregistrer_etat_migration(
                racine_temporaire,
                {
                    "cible_id": "java17",
                    "titre": "Java 17",
                    "version_installee": "17.0.0",
                    "version_candidate": "17.0.8",
                    "branche_git": "migration/java17",
                    "commit_git": "abc123",
                    "migration_appliquee": True,
                    "placeholder_ia_genere": False,
                    "chemin_placeholder_md": "",
                    "chemin_placeholder_json": "",
                    "chemin_reponse_ia": "",
                    "chemin_transcription_ia_jsonl": "",
                    "qualite_verifiee": False,
                    "chemin_rapport_qualite": "",
                    "horodatage_derniere_etape": "2026-03-02T10:00:00",
                },
            )

            with (
                patch.object(operations, "obtenir_cible_migration_contextualisee", return_value=(cible, [cible])),
                patch.object(
                    operations,
                    "capturer_contexte_git",
                    return_value={"branche_git": "migration/java17", "commit_git": "abc123", "depot_propre": True},
                ),
                patch.object(
                    operations,
                    "verifier_outils_assistant_ia",
                    return_value=(False, "Assistant IA impossible: URL du serveur Ollama absente."),
                ),
            ):
                succes, message, _ = operations.operation_preparer_placeholder_ia_migration(
                    configuration,
                    racine_temporaire,
                    racine_temporaire / "journal.log",
                    lambda _: None,
                    {
                        "cible_migration_id": "java17",
                        "dossier_sortie": str(racine_temporaire),
                    },
                )

            self.assertFalse(succes)
            self.assertIn("Ollama", message)
            self.assertEqual(len(list(racine_temporaire.glob("brief_ia_migration_java17_*.md"))), 1)
            etat = operations.charger_etat_migration(racine_temporaire)
            self.assertFalse(etat["placeholder_ia_genere"])
            self.assertEqual(etat["chemin_reponse_ia"], "")

    def test_operation_relancer_qualite_refuse_sans_assistant_ia(self) -> None:
        """Controle le respect de l ordre migration puis IA avant la qualite.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        configuration = operations.charger_configuration(Path("config_introuvable.json"))
        cible = {
            "id": "java17",
            "titre": "Java 17",
            "version_installee": "17.0.0",
            "version_candidate": "17.0.8",
        }

        with tempfile.TemporaryDirectory() as dossier_temporaire:
            racine_temporaire = Path(dossier_temporaire)
            operations.enregistrer_etat_migration(
                racine_temporaire,
                {
                    "cible_id": "java17",
                    "titre": "Java 17",
                    "version_installee": "17.0.0",
                    "version_candidate": "17.0.8",
                    "branche_git": "migration/java17",
                    "commit_git": "abc123",
                    "migration_appliquee": True,
                    "placeholder_ia_genere": False,
                    "chemin_placeholder_md": "",
                    "chemin_placeholder_json": "",
                    "chemin_reponse_ia": "",
                    "chemin_transcription_ia_jsonl": "",
                    "qualite_verifiee": False,
                    "chemin_rapport_qualite": "",
                    "horodatage_derniere_etape": "2026-03-02T10:00:00",
                },
            )

            with (
                patch.object(operations, "obtenir_cible_migration_contextualisee", return_value=(cible, [cible])),
                patch.object(
                    operations,
                    "capturer_contexte_git",
                    return_value={"branche_git": "migration/java17", "commit_git": "abc123", "depot_propre": True},
                ),
            ):
                succes, message, _ = operations.operation_relancer_qualite_complete(
                    configuration,
                    racine_temporaire,
                    racine_temporaire / "journal.log",
                    lambda _: None,
                    {"cible_migration_id": "java17"},
                )

            self.assertFalse(succes)
            self.assertIn("assistant IA", message)

    def test_operation_relancer_qualite_genere_rapport_si_act_absent(self) -> None:
        """Controle la creation d un rapport qualite meme si `act` est absent.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        configuration = operations.charger_configuration(Path("config_introuvable.json"))
        cible = {
            "id": "java17",
            "titre": "Java 17",
            "version_installee": "17.0.0",
            "version_candidate": "17.0.8",
        }

        with tempfile.TemporaryDirectory() as dossier_temporaire:
            racine_temporaire = Path(dossier_temporaire)
            operations.enregistrer_etat_migration(
                racine_temporaire,
                {
                    "cible_id": "java17",
                    "titre": "Java 17",
                    "version_installee": "17.0.0",
                    "version_candidate": "17.0.8",
                    "branche_git": "migration/java17",
                    "commit_git": "abc123",
                    "migration_appliquee": True,
                    "placeholder_ia_genere": True,
                    "chemin_placeholder_md": str(racine_temporaire / "placeholder.md"),
                    "chemin_placeholder_json": str(racine_temporaire / "placeholder.json"),
                    "qualite_verifiee": False,
                    "chemin_rapport_qualite": "",
                    "horodatage_derniere_etape": "2026-03-02T10:00:00",
                },
            )

            with (
                patch.object(operations, "obtenir_cible_migration_contextualisee", return_value=(cible, [cible])),
                patch.object(
                    operations,
                    "capturer_contexte_git",
                    return_value={"branche_git": "migration/java17", "commit_git": "abc123", "depot_propre": True},
                ),
                patch.object(operations, "trouver_commande_act", return_value=None),
                patch.object(operations, "selectionner_dossier_logs", return_value=racine_temporaire),
            ):
                succes, message, _ = operations.operation_relancer_qualite_complete(
                    configuration,
                    racine_temporaire,
                    racine_temporaire / "journal.log",
                    lambda _: None,
                    {"cible_migration_id": "java17"},
                )

            self.assertFalse(succes)
            self.assertIn("act introuvable", message)
            rapports = list(racine_temporaire.glob("rapport_qualite_migration_java17_*.json"))
            self.assertEqual(len(rapports), 1)
            etat = operations.charger_etat_migration(racine_temporaire)
            self.assertFalse(etat["qualite_verifiee"])
            self.assertEqual(Path(str(etat["chemin_rapport_qualite"])), rapports[0])

    def test_operation_proposer_pr_refuse_sans_qualite_validee(self) -> None:
        """Controle le refus d ouverture PR quand la qualite n est pas validee.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        configuration = operations.charger_configuration(Path("config_introuvable.json"))
        cible = {
            "id": "java17",
            "titre": "Java 17",
            "version_installee": "17.0.0",
            "version_candidate": "17.0.8",
        }

        with tempfile.TemporaryDirectory() as dossier_temporaire:
            racine_temporaire = Path(dossier_temporaire)
            operations.enregistrer_etat_migration(
                racine_temporaire,
                {
                    "cible_id": "java17",
                    "titre": "Java 17",
                    "version_installee": "17.0.0",
                    "version_candidate": "17.0.8",
                    "branche_git": "migration/java17",
                    "commit_git": "abc123",
                    "migration_appliquee": True,
                    "placeholder_ia_genere": True,
                    "chemin_placeholder_md": "placeholder.md",
                    "chemin_placeholder_json": "placeholder.json",
                    "qualite_verifiee": False,
                    "chemin_rapport_qualite": "",
                    "horodatage_derniere_etape": "2026-03-02T10:00:00",
                },
            )

            with (
                patch.object(operations, "obtenir_cible_migration_contextualisee", return_value=(cible, [cible])),
                patch.object(
                    operations,
                    "capturer_contexte_git",
                    return_value={"branche_git": "migration/java17", "commit_git": "abc123", "depot_propre": True},
                ),
            ):
                succes, message, _ = operations.operation_proposer_pr_migration(
                    configuration,
                    racine_temporaire,
                    racine_temporaire / "journal.log",
                    lambda _: None,
                    {"cible_migration_id": "java17"},
                )

            self.assertFalse(succes)
            self.assertIn("qualite complete n a pas ete validee", message)


if __name__ == "__main__":
    unittest.main()
