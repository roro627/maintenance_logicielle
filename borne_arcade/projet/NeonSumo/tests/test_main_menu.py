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

def creer_fausse_impl_pygame():
    """Construit un module pygame minimal pour les tests sans dependance native.

    Args:
        Aucun.

    Returns:
        Espace de noms exposeant les constantes de touches attendues.
    """

    return types.SimpleNamespace(
        K_UP=1,
        K_DOWN=2,
        K_LEFT=3,
        K_RIGHT=4,
        K_f=5,
        K_g=6,
        K_h=7,
        K_r=8,
        K_t=9,
        K_y=10,
        K_o=11,
        K_l=12,
        K_k=13,
        K_m=14,
        K_q=15,
        K_s=16,
        K_d=17,
        K_a=18,
        K_z=19,
        K_e=20,
        K_1=21,
        K_2=22,
        K_3=23,
        K_4=24,
        K_5=25,
        K_6=26,
        K_KP1=31,
        K_KP2=32,
        K_KP3=33,
        K_KP4=34,
        K_KP5=35,
        K_KP6=36,
    )

CHEMIN_MAIN_NEON_SUMO = MODULE_NEON_SUMO / "main.py"
SPEC_MAIN_NEON_SUMO = importlib.util.spec_from_file_location("main_neon_sumo", CHEMIN_MAIN_NEON_SUMO)
if SPEC_MAIN_NEON_SUMO is None or SPEC_MAIN_NEON_SUMO.loader is None:
    raise ImportError("Impossible de charger le module main.py de NeonSumo.")
MODULE_MAIN_NEON_SUMO = importlib.util.module_from_spec(SPEC_MAIN_NEON_SUMO)
sys.modules[SPEC_MAIN_NEON_SUMO.name] = MODULE_MAIN_NEON_SUMO
SPEC_MAIN_NEON_SUMO.loader.exec_module(MODULE_MAIN_NEON_SUMO)
if MODULE_MAIN_NEON_SUMO.pygame is None:
    try:
        MODULE_MAIN_NEON_SUMO.pygame = MODULE_MAIN_NEON_SUMO.importer_pygame()
    except RuntimeError:
        MODULE_MAIN_NEON_SUMO.pygame = creer_fausse_impl_pygame()
if not hasattr(MODULE_MAIN_NEON_SUMO.pygame, "K_UP"):
    MODULE_MAIN_NEON_SUMO.pygame = creer_fausse_impl_pygame()
construire_parametres_menu_titre = MODULE_MAIN_NEON_SUMO.construire_parametres_menu_titre
mode_competitif_actif = MODULE_MAIN_NEON_SUMO.mode_competitif_actif
doit_reinitialiser_attract = MODULE_MAIN_NEON_SUMO.doit_reinitialiser_attract
gerer_entree_borne = MODULE_MAIN_NEON_SUMO.gerer_entree_borne
construire_aliases_boutons_j1 = MODULE_MAIN_NEON_SUMO.construire_aliases_boutons_j1
touche_juste_appuyee = MODULE_MAIN_NEON_SUMO.touche_juste_appuyee
construire_textes_aide_menu_titre = MODULE_MAIN_NEON_SUMO.construire_textes_aide_menu_titre
verifier_coherence_entrees_borne = MODULE_MAIN_NEON_SUMO.verifier_coherence_entrees_borne
EntreeJoueur = MODULE_MAIN_NEON_SUMO.EntreeJoueur


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

    def test_mode_competitif_actif_reconnait_uniquement_manche(self) -> None:
        """Controle la detection de l etat competitif.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        self.assertTrue(mode_competitif_actif("manche"))
        self.assertFalse(mode_competitif_actif("attract"))
        self.assertFalse(mode_competitif_actif("titre"))

    def test_doit_reinitialiser_attract_uniquement_sur_elimination_attract(self) -> None:
        """Controle le comportement de relance du mode attract.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        self.assertTrue(doit_reinitialiser_attract("attract", True, False))
        self.assertTrue(doit_reinitialiser_attract("attract", False, True))
        self.assertTrue(doit_reinitialiser_attract("attract", True, True))
        self.assertFalse(doit_reinitialiser_attract("manche", True, False))
        self.assertFalse(doit_reinitialiser_attract("attract", False, False))

    def test_gerer_entree_borne_associe_les_touches_arcade_attendues(self) -> None:
        """Controle le mapping explicite des boutons borne pour NeonSumo.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        j1, j2 = gerer_entree_borne()

        self.assertEqual(j1.haut, MODULE_MAIN_NEON_SUMO.pygame.K_UP)
        self.assertEqual(j1.bas, MODULE_MAIN_NEON_SUMO.pygame.K_DOWN)
        self.assertEqual(j1.gauche, MODULE_MAIN_NEON_SUMO.pygame.K_LEFT)
        self.assertEqual(j1.droite, MODULE_MAIN_NEON_SUMO.pygame.K_RIGHT)
        self.assertEqual(j1.dash, MODULE_MAIN_NEON_SUMO.pygame.K_f)
        self.assertEqual(j1.frein, MODULE_MAIN_NEON_SUMO.pygame.K_g)
        self.assertEqual(j1.bump, MODULE_MAIN_NEON_SUMO.pygame.K_h)
        self.assertEqual(j1.bouclier, MODULE_MAIN_NEON_SUMO.pygame.K_r)
        self.assertEqual(j1.taunt, MODULE_MAIN_NEON_SUMO.pygame.K_t)
        self.assertEqual(j1.ultime, MODULE_MAIN_NEON_SUMO.pygame.K_y)

        self.assertEqual(j2.haut, MODULE_MAIN_NEON_SUMO.pygame.K_o)
        self.assertEqual(j2.bas, MODULE_MAIN_NEON_SUMO.pygame.K_l)
        self.assertEqual(j2.gauche, MODULE_MAIN_NEON_SUMO.pygame.K_k)
        self.assertEqual(j2.droite, MODULE_MAIN_NEON_SUMO.pygame.K_m)
        self.assertEqual(j2.dash, MODULE_MAIN_NEON_SUMO.pygame.K_q)
        self.assertEqual(j2.frein, MODULE_MAIN_NEON_SUMO.pygame.K_s)
        self.assertEqual(j2.bump, MODULE_MAIN_NEON_SUMO.pygame.K_d)
        self.assertEqual(j2.bouclier, MODULE_MAIN_NEON_SUMO.pygame.K_a)
        self.assertEqual(j2.taunt, MODULE_MAIN_NEON_SUMO.pygame.K_z)
        self.assertEqual(j2.ultime, MODULE_MAIN_NEON_SUMO.pygame.K_e)

    def test_construire_aliases_boutons_j1_inclut_les_touches_numeriques(self) -> None:
        """Controle la presence des alias numeriques pour B1..B6.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        alias = construire_aliases_boutons_j1()

        self.assertIn(MODULE_MAIN_NEON_SUMO.pygame.K_1, alias["dash"])
        self.assertIn(MODULE_MAIN_NEON_SUMO.pygame.K_KP1, alias["dash"])
        self.assertIn(MODULE_MAIN_NEON_SUMO.pygame.K_3, alias["bump"])
        self.assertIn(MODULE_MAIN_NEON_SUMO.pygame.K_KP3, alias["bump"])
        self.assertIn(MODULE_MAIN_NEON_SUMO.pygame.K_6, alias["ultime"])
        self.assertIn(MODULE_MAIN_NEON_SUMO.pygame.K_KP6, alias["ultime"])

    def test_touche_juste_appuyee_accepte_les_aliases(self) -> None:
        """Controle la detection front montant avec touche alias.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        resultat = touche_juste_appuyee(
            {MODULE_MAIN_NEON_SUMO.pygame.K_3},
            MODULE_MAIN_NEON_SUMO.pygame.K_h,
            (MODULE_MAIN_NEON_SUMO.pygame.K_3, MODULE_MAIN_NEON_SUMO.pygame.K_KP3),
        )
        self.assertTrue(resultat)

    def test_verifier_coherence_entrees_borne_refuse_un_doublon_joueur(self) -> None:
        """Controle le refus d un doublon de touche sur un meme joueur.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        j1 = EntreeJoueur(1, 2, 3, 4, 5, 6, 7, 8, 9, 5)
        j2 = EntreeJoueur(11, 12, 13, 14, 15, 16, 17, 18, 19, 20)

        with self.assertRaisesRegex(ValueError, "Configuration commandes J1 incoherente"):
            verifier_coherence_entrees_borne(j1, j2)

    def test_verifier_coherence_entrees_borne_refuse_un_doublon_inter_joueurs(self) -> None:
        """Controle le refus d une collision de touche entre J1 et J2.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        j1 = EntreeJoueur(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
        j2 = EntreeJoueur(11, 12, 13, 14, 15, 16, 17, 18, 19, 5)

        with self.assertRaisesRegex(ValueError, "Configuration commandes borne incoherente"):
            verifier_coherence_entrees_borne(j1, j2)

    def test_construire_textes_aide_menu_titre_couvre_toutes_les_actions(self) -> None:
        """Controle que l aide du menu titre rappelle bien tous les boutons utiles.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        lignes = construire_textes_aide_menu_titre()
        self.assertEqual(len(lignes), 3)
        self.assertIn("B1: Start match", lignes[0])
        self.assertIn("B6: Retour menu", lignes[0])
        self.assertIn("B5 Taunt", lignes[1])
        self.assertIn("B6 Ultime", lignes[1])


if __name__ == "__main__":
    unittest.main()
