"""Tests unitaires pour la logique Neon Sumo."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

DOSSIER_JEU = Path(__file__).resolve().parents[1]
if str(DOSSIER_JEU) not in sys.path:
    sys.path.insert(0, str(DOSSIER_JEU))

from logique import (  # noqa: E402
    EtatStyleJoueur,
    Joueur,
    ParametresCombat,
    ParametresStyle,
    activer_dash,
    activer_ultime,
    charger_ultime,
    decrementer_cooldowns,
    enregistrer_impact_style,
    executer_bump,
    mettre_a_jour_etat_style,
    mettre_a_jour_sauvetage_bord,
    resoudre_collision_capsules,
    tenter_esquive_proche,
    verifier_sortie_arene,
)


class TestLogiqueNeonSumo(unittest.TestCase):
    """Verifie les regles de base du coeur de simulation."""

    def creer_parametres(self) -> ParametresCombat:
        """Cree une configuration de test stable.

        Returns:
            ParametresCombat utilisables dans les tests.
        """

        return ParametresCombat(
            acceleration=900.0,
            friction_base=1.6,
            friction_frein=5.5,
            vitesse_max=500.0,
            coefficient_rebond_collision=0.65,
            impulsion_dash=350.0,
            impulsion_bump=280.0,
            rayon_bump=60.0,
            multiplicateur_bouclier=0.3,
            duree_bouclier=0.5,
            cooldown_dash=1.2,
            cooldown_bump=0.8,
            cooldown_bouclier=2.2,
            cooldown_taunt=1.0,
            gain_ultime_par_seconde=0.1,
            gain_ultime_par_impact=0.2,
            rayon_ultime=160.0,
            impulsion_ultime=500.0,
            delai_sortie_arene=0.2,
        )

    def creer_joueur(self, identifiant: str, x: float, y: float) -> Joueur:
        """Cree un joueur de test.

        Args:
            identifiant: Nom du joueur.
            x: Position X.
            y: Position Y.

        Returns:
            Joueur initialise.
        """

        return Joueur(
            identifiant=identifiant,
            position_x=x,
            position_y=y,
            vitesse_x=0.0,
            vitesse_y=0.0,
            rayon=28.0,
            direction_x=1.0,
            direction_y=0.0,
            cooldowns={"dash": 0.0, "bump": 0.0, "bouclier": 0.0, "taunt": 0.0},
        )

    def creer_parametres_style(self) -> ParametresStyle:
        """Construit des parametres style de test.

        Returns:
            ParametresStyle utilisables dans les tests.
        """

        return ParametresStyle(
            fenetre_combo=2.0,
            bonus_combo_par_niveau=4,
            points_impact=16,
            points_esquive=20,
            points_sauvetage=24,
            distance_esquive=70.0,
            cooldown_esquive=1.0,
            marge_sauvetage=18.0,
            duree_affichage_action=1.2,
        )

    def test_collision_bump_applique_knockback(self) -> None:
        """Valide qu un bump frontal applique bien une impulsion."""

        parametres = self.creer_parametres()
        attaquant = self.creer_joueur("J1", 100.0, 100.0)
        defenseur = self.creer_joueur("J2", 140.0, 100.0)

        succes = executer_bump(attaquant, defenseur, parametres)

        self.assertTrue(succes)
        self.assertGreater(defenseur.vitesse_x, 0.0)
        self.assertGreaterEqual(attaquant.cooldowns["bump"], 0.79)

    def test_collision_passive_repousse_et_echange_vitesse(self) -> None:
        """Valide le push passif quand deux capsules se chevauchent."""

        parametres = self.creer_parametres()
        joueur_1 = self.creer_joueur("J1", 100.0, 100.0)
        joueur_2 = self.creer_joueur("J2", 150.0, 100.0)
        joueur_1.vitesse_x = 120.0
        joueur_2.vitesse_x = -40.0

        collision_resolue = resoudre_collision_capsules(joueur_1, joueur_2, parametres)

        distance_apres = abs(joueur_2.position_x - joueur_1.position_x)
        self.assertTrue(collision_resolue)
        self.assertGreaterEqual(distance_apres, joueur_1.rayon + joueur_2.rayon - 1e-6)
        self.assertLess(joueur_1.vitesse_x, 120.0)
        self.assertGreater(joueur_2.vitesse_x, -40.0)

    def test_collision_passive_absente_hors_portee(self) -> None:
        """Verifie qu aucune correction n est appliquee sans chevauchement."""

        parametres = self.creer_parametres()
        joueur_1 = self.creer_joueur("J1", 100.0, 100.0)
        joueur_2 = self.creer_joueur("J2", 300.0, 100.0)

        collision_resolue = resoudre_collision_capsules(joueur_1, joueur_2, parametres)

        self.assertFalse(collision_resolue)
        self.assertEqual(joueur_1.position_x, 100.0)
        self.assertEqual(joueur_2.position_x, 300.0)

    def test_detection_sortie_arene(self) -> None:
        """Verifie l elimination apres delai hors arene."""

        parametres = self.creer_parametres()
        joueur = self.creer_joueur("J1", 200.0, 100.0)

        elimine_rapide = verifier_sortie_arene(
            joueur,
            centre_x=100.0,
            centre_y=100.0,
            rayon_arene=40.0,
            delta_temps=0.1,
            parametres=parametres,
        )
        elimine_apres_delai = verifier_sortie_arene(
            joueur,
            centre_x=100.0,
            centre_y=100.0,
            rayon_arene=40.0,
            delta_temps=0.11,
            parametres=parametres,
        )

        self.assertFalse(elimine_rapide)
        self.assertTrue(elimine_apres_delai)

    def test_cooldown_dash_et_jauge_ultime(self) -> None:
        """Controle cooldown dash et consommation de la jauge ultime."""

        parametres = self.creer_parametres()
        joueur = self.creer_joueur("J1", 100.0, 100.0)
        adversaire = self.creer_joueur("J2", 120.0, 100.0)

        premier_dash = activer_dash(joueur, parametres)
        second_dash_immediat = activer_dash(joueur, parametres)

        self.assertTrue(premier_dash)
        self.assertFalse(second_dash_immediat)

        decrementer_cooldowns(joueur, 1.3)
        troisieme_dash = activer_dash(joueur, parametres)
        self.assertTrue(troisieme_dash)

        charger_ultime(joueur, 10.0, parametres)
        self.assertGreaterEqual(joueur.jauge_ultime, 1.0)

        succes_ultime = activer_ultime(joueur, adversaire, parametres)
        self.assertTrue(succes_ultime)
        self.assertEqual(joueur.jauge_ultime, 0.0)

    def test_style_combo_sur_impacts(self) -> None:
        """Verifie la progression du combo style sur impacts successifs."""

        style = EtatStyleJoueur()
        parametres_style = self.creer_parametres_style()

        premier_gain = enregistrer_impact_style(style, parametres_style)
        mettre_a_jour_etat_style(style, 0.2)
        second_gain = enregistrer_impact_style(style, parametres_style)

        self.assertGreaterEqual(premier_gain, parametres_style.points_impact)
        self.assertGreater(second_gain, premier_gain)
        self.assertEqual(style.combo_courant, 2)
        self.assertGreater(style.score_total, premier_gain)

    def test_style_esquive_proche_respecte_cooldown(self) -> None:
        """Controle la detection d esquive proche et son cooldown."""

        parametres_style = self.creer_parametres_style()
        style = EtatStyleJoueur()
        joueur = self.creer_joueur("J1", 100.0, 100.0)
        adversaire = self.creer_joueur("J2", 160.0, 100.0)
        joueur.vitesse_x = -180.0
        adversaire.vitesse_x = 120.0

        esquive_1 = tenter_esquive_proche(joueur, adversaire, style, parametres_style)
        esquive_2 = tenter_esquive_proche(joueur, adversaire, style, parametres_style)

        self.assertTrue(esquive_1)
        self.assertFalse(esquive_2)

        mettre_a_jour_etat_style(style, parametres_style.cooldown_esquive + 0.1)
        esquive_3 = tenter_esquive_proche(joueur, adversaire, style, parametres_style)
        self.assertTrue(esquive_3)

    def test_style_sauvetage_bord(self) -> None:
        """Verifie le bonus style lors d un retour depuis la zone danger."""

        parametres_style = self.creer_parametres_style()
        style = EtatStyleJoueur()
        joueur = self.creer_joueur("J1", 460.0, 100.0)
        centre_x = 100.0
        centre_y = 100.0
        rayon_arene = 380.0
        largeur_danger = 30.0

        bonus_absent = mettre_a_jour_sauvetage_bord(
            joueur,
            style,
            parametres_style,
            centre_x,
            centre_y,
            rayon_arene,
            largeur_danger,
        )

        joueur.position_x = 300.0
        bonus_present = mettre_a_jour_sauvetage_bord(
            joueur,
            style,
            parametres_style,
            centre_x,
            centre_y,
            rayon_arene,
            largeur_danger,
        )

        self.assertFalse(bonus_absent)
        self.assertTrue(bonus_present)
        self.assertGreaterEqual(style.score_total, parametres_style.points_sauvetage)


def main() -> None:
    """Point d entree de la suite de tests unitaire."""

    unittest.main()


if __name__ == "__main__":
    main()
