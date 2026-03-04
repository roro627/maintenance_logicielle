"""Tests cibles du jeu ball-blast."""

from __future__ import annotations

import importlib
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

def installer_fausse_impl_pygame():
    """Installe un module pygame minimal pour executer les tests sans dependance native.

    Args:
        Aucun.

    Returns:
        Module pygame factice expose dans `sys.modules`.
    """

    module_pygame = types.ModuleType("pygame")
    module_pygame.__path__ = []
    module_pygame.SRCALPHA = 1
    module_pygame.NOFRAME = 2
    module_pygame.FULLSCREEN = 4
    module_pygame.K_LEFT = 276
    module_pygame.K_RIGHT = 275
    module_pygame.K_f = 102

    class RectFactice:
        """Represente un rectangle minimal compatible avec les usages des tests."""

        def __init__(self, largeur: int, hauteur: int) -> None:
            self.x = 0
            self.y = 0
            self.width = largeur
            self.height = hauteur
            self.left = 0
            self.top = 0
            self.right = largeur
            self.bottom = hauteur
            self.centerx = largeur // 2
            self.centery = hauteur // 2
            self.center = (self.centerx, self.centery)

        def _recalculer_depuis_position(self) -> None:
            """Met a jour les bornes derivees apres un changement de position.

            Args:
                Aucun.

            Returns:
                Aucun.
            """

            self.left = self.x
            self.top = self.y
            self.right = self.x + self.width
            self.bottom = self.y + self.height
            self.centerx = self.x + self.width // 2
            self.centery = self.y + self.height // 2
            self.center = (self.centerx, self.centery)

        def appliquer_options(self, **options):
            """Applique les options de placement supportees par `get_rect`.

            Args:
                **options: Options de placement pygame simplifiees.

            Returns:
                Le rectangle mis a jour.
            """

            centre = options.get("center")
            if centre is not None:
                self.center = centre
                self.centerx, self.centery = centre
                self.x = self.centerx - self.width // 2
                self.y = self.centery - self.height // 2
                self._recalculer_depuis_position()
            return self

    class SurfaceFactice:
        """Represente une surface minimale pour les tests unitaires."""

        def __init__(self, taille, _flags=0) -> None:
            self._taille = tuple(taille)

        def get_rect(self, **options):
            """Retourne un rectangle associe a la surface.

            Args:
                **options: Options de placement pygame simplifiees.

            Returns:
                Rectangle factice dimensionne sur la surface.
            """

            return RectFactice(self._taille[0], self._taille[1]).appliquer_options(**options)

        def blit(self, _source, _position):
            """Simule un blit sans effet secondaire.

            Args:
                _source: Surface source non utilisee.
                _position: Position cible non utilisee.

            Returns:
                Aucun.
            """

            return None

        def fill(self, _couleur):
            """Simule un remplissage sans effet secondaire.

            Args:
                _couleur: Couleur ignoree.

            Returns:
                Aucun.
            """

            return None

        def get_size(self):
            """Retourne la taille de la surface.

            Args:
                Aucun.

            Returns:
                Tuple largeur/hauteur.
            """

            return self._taille

        def convert(self):
            """Retourne la surface courante pour l API pygame.

            Args:
                Aucun.

            Returns:
                La surface courante.
            """

            return self

        def convert_alpha(self):
            """Retourne la surface courante pour l API pygame.

            Args:
                Aucun.

            Returns:
                La surface courante.
            """

            return self

    class PoliceFactice:
        """Represente une police minimale pour les rendus de test."""

        def __init__(self, taille: int) -> None:
            self.taille = taille

        def render(self, texte: str, _antialias, _couleur):
            """Cree une surface dimensionnee selon le texte demande.

            Args:
                texte: Texte a rasteriser.
                _antialias: Parametre ignore.
                _couleur: Couleur ignoree.

            Returns:
                Surface factice correspondant au texte.
            """

            largeur = max(1, len(texte) * max(1, self.taille // 2))
            hauteur = max(1, self.taille)
            return SurfaceFactice((largeur, hauteur), module_pygame.SRCALPHA)

    module_font = types.ModuleType("pygame.font")
    module_font.init = lambda: None
    module_font.SysFont = lambda _nom, taille: PoliceFactice(taille)

    module_sprite = types.ModuleType("pygame.sprite")

    class SpriteFactice:
        """Base minimale compatible avec `pygame.sprite.Sprite`."""

        def __init__(self) -> None:
            self.image = None
            self.rect = None

        def kill(self) -> None:
            """Simule la suppression du sprite.

            Args:
                Aucun.

            Returns:
                Aucun.
            """

            return None

    class GroupFactice(list):
        """Collection minimale compatible avec `pygame.sprite.Group`."""

        def add(self, *elements) -> None:
            """Ajoute des elements au groupe.

            Args:
                *elements: Sprites a memoriser.

            Returns:
                Aucun.
            """

            self.extend(elements)

        def draw(self, _surface) -> None:
            """Simule le rendu du groupe.

            Args:
                _surface: Surface ignoree.

            Returns:
                Aucun.
            """

            return None

        def update(self) -> None:
            """Simule la mise a jour du groupe.

            Args:
                Aucun.

            Returns:
                Aucun.
            """

            return None

        def sprites(self):
            """Retourne une liste stable des sprites.

            Args:
                Aucun.

            Returns:
                Liste des elements contenus.
            """

            return list(self)

    module_sprite.Sprite = SpriteFactice
    module_sprite.Group = GroupFactice
    module_sprite.groupcollide = lambda *_args, **_kwargs: {}

    module_transform = types.ModuleType("pygame.transform")
    module_transform.scale = lambda surface, _taille: surface
    module_transform.rotate = lambda surface, _angle: surface

    module_image = types.ModuleType("pygame.image")
    module_image.load = lambda _chemin: SurfaceFactice((64, 64), module_pygame.SRCALPHA)

    module_draw = types.ModuleType("pygame.draw")
    module_draw.rect = lambda *_args, **_kwargs: None
    module_draw.polygon = lambda *_args, **_kwargs: None
    module_draw.circle = lambda *_args, **_kwargs: None

    module_mask = types.ModuleType("pygame.mask")
    module_mask.from_surface = lambda _surface: object()

    module_key = types.ModuleType("pygame.key")
    module_key.get_pressed = lambda: {}

    module_time = types.ModuleType("pygame.time")

    class HorlogeFactice:
        """Horloge minimale pour conserver la signature pygame."""

        def tick(self, _fps):
            """Simule le bridage de la boucle.

            Args:
                _fps: Frequence cible ignoree.

            Returns:
                Aucun.
            """

            return None

    module_time.Clock = HorlogeFactice

    module_display = types.ModuleType("pygame.display")
    module_display.set_mode = lambda taille, _flags=0: SurfaceFactice(taille, module_pygame.SRCALPHA)
    module_display.set_caption = lambda _titre: None
    module_display.update = lambda: None
    module_display.flip = lambda: None

    module_mixer = types.ModuleType("pygame.mixer")
    module_mixer.music = types.SimpleNamespace(load=lambda _chemin: None, play=lambda: None)

    module_pygame.Surface = SurfaceFactice
    module_pygame.Rect = RectFactice
    module_pygame.init = lambda: None
    module_pygame.quit = lambda: None
    module_pygame.font = module_font
    module_pygame.sprite = module_sprite
    module_pygame.transform = module_transform
    module_pygame.image = module_image
    module_pygame.draw = module_draw
    module_pygame.mask = module_mask
    module_pygame.key = module_key
    module_pygame.time = module_time
    module_pygame.display = module_display
    module_pygame.mixer = module_mixer

    sys.modules["pygame"] = module_pygame
    sys.modules["pygame.font"] = module_font
    sys.modules["pygame.sprite"] = module_sprite
    sys.modules["pygame.transform"] = module_transform
    sys.modules["pygame.image"] = module_image
    sys.modules["pygame.draw"] = module_draw
    sys.modules["pygame.mask"] = module_mask
    sys.modules["pygame.key"] = module_key
    sys.modules["pygame.time"] = module_time
    sys.modules["pygame.display"] = module_display
    sys.modules["pygame.mixer"] = module_mixer
    return module_pygame


try:
    import pygame
except ModuleNotFoundError:
    pygame = installer_fausse_impl_pygame()

DOSSIER_SOURCE = Path(__file__).resolve().parents[1] / "src"
if str(DOSSIER_SOURCE) not in sys.path:
    sys.path.insert(0, str(DOSSIER_SOURCE))

from game import Game, calculer_scissions_balle  # pylint: disable=import-error
import constantes as module_constantes  # pylint: disable=import-error


class TestBallBlast(unittest.TestCase):
    """Verifie les contrats critiques de ball-blast."""

    @classmethod
    def setUpClass(cls) -> None:
        """Initialise pygame une fois pour la suite."""

        pygame.init()
        pygame.font.init()

    @classmethod
    def tearDownClass(cls) -> None:
        """Libere pygame en fin de suite."""

        pygame.quit()

    def test_save_score_trie_par_ordre_decroissant(self) -> None:
        """Verifie le tri des scores sauvegardes."""

        jeu = Game.__new__(Game)
        jeu.player = type("JoueurFactice", (), {"score": 42})()

        with tempfile.TemporaryDirectory() as dossier_temporaire:
            ancien_cwd = Path.cwd()
            os.chdir(dossier_temporaire)
            try:
                Path("highscore").write_text("AAA-10\nBBB-99\n", encoding="utf-8")
                jeu._saveScore("ZZZ")
                lignes = Path("highscore").read_text(encoding="utf-8").splitlines()
            finally:
                os.chdir(ancien_cwd)

        self.assertEqual(lignes, ["BBB-99", "ZZZ-42", "AAA-10"])

    def test_next_level_reinitialise_les_compteurs(self) -> None:
        """Verifie la reinitialisation des compteurs de niveau."""

        jeu = Game.__new__(Game)
        jeu.level = 3
        jeu.ballsToSpawn = 1
        jeu.frameNumberWinAnim = 7
        jeu.frameNumberSpawnBalls = 8
        jeu.frameNumberBeginLevel = 9

        jeu.nextLevel()

        self.assertEqual(jeu.level, 4)
        self.assertEqual(jeu.ballsToSpawn, 14 + 4 * 5)
        self.assertEqual(jeu.frameNumberWinAnim, 0)
        self.assertEqual(jeu.frameNumberSpawnBalls, 0)
        self.assertEqual(jeu.frameNumberBeginLevel, 0)

    def test_calculer_scissions_balle_retourne_deux_boules_filles(self) -> None:
        """Verifie la resolution pure des scissions de boules."""

        niveaux = [[(0, 0, 0), 50], [(255, 0, 0), 40], [(0, 255, 0), 33]]
        scissions = calculer_scissions_balle(True, 0, 120, 75, niveaux)

        self.assertEqual(len(scissions), 2)
        self.assertEqual(scissions[0]["niveau"], 1)
        self.assertEqual(scissions[0]["decalage"], 10)
        self.assertEqual(scissions[1]["decalage"], -10)
        self.assertEqual(scissions[0]["rayon"], 40)

    def test_cache_score_est_reutilise_si_le_score_ne_change_pas(self) -> None:
        """Verifie que le cache score n est pas regenere inutilement."""

        jeu = Game.__new__(Game)
        jeu.player = type("JoueurFactice", (), {"score": 12})()
        jeu.score_affiche = -1
        jeu.surface_score = None

        police = mock.Mock()
        police.render.return_value = pygame.Surface((40, 12), pygame.SRCALPHA)

        with mock.patch("game.FONT_SCORE", police):
            Game._mettre_a_jour_surface_score(jeu)
            premiere_surface = jeu.surface_score
            Game._mettre_a_jour_surface_score(jeu)

        self.assertIs(jeu.surface_score, premiere_surface)
        police.render.assert_called_once()

    def test_constantes_affichage_suivent_la_configuration_borne(self) -> None:
        """Verifie l application de la resolution et du mode borne."""

        with mock.patch.dict(
            os.environ,
            {
                "BORNE_RESOLUTION_X": "1280",
                "BORNE_RESOLUTION_Y": "1024",
                "BORNE_MODE_AFFICHAGE": "fenetre_sans_bordure",
            },
            clear=False,
        ):
            constantes_rechargees = importlib.reload(module_constantes)

        self.assertEqual(constantes_rechargees.SCREEN_WIDTH, 1280)
        self.assertEqual(constantes_rechargees.SCREEN_HEIGHT, 1024)
        self.assertEqual(constantes_rechargees.DISPLAY_FLAGS, pygame.NOFRAME)
        importlib.reload(module_constantes)


if __name__ == "__main__":
    unittest.main()
