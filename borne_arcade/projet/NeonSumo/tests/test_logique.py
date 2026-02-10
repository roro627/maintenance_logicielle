"""Tests unitaires pour la logique Neon Sumo."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

DOSSIER_JEU = Path(__file__).resolve().parents[1]
if str(DOSSIER_JEU) not in sys.path:
    sys.path.insert(0, str(DOSSIER_JEU))

from logique import (  # noqa: E402
    Joueur,
    ParametresCombat,
    activer_dash,
    activer_ultime,
    charger_ultime,
    decrementer_cooldowns,
    executer_bump,
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

    def test_collision_bump_applique_knockback(self) -> None:
        """Valide qu un bump frontal applique bien une impulsion."""

        parametres = self.creer_parametres()
        attaquant = self.creer_joueur("J1", 100.0, 100.0)
        defenseur = self.creer_joueur("J2", 140.0, 100.0)

        succes = executer_bump(attaquant, defenseur, parametres)

        self.assertTrue(succes)
        self.assertGreater(defenseur.vitesse_x, 0.0)
        self.assertGreaterEqual(attaquant.cooldowns["bump"], 0.79)

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


def main() -> None:
    """Point d entree de la suite de tests unitaire."""

    unittest.main()


if __name__ == "__main__":
    main()
