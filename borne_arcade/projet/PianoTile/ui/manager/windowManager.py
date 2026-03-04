import pygame

from core.player import Player
from ui.layout.backgroundView import BackgroundView
from ui.layout.gameView import GameView
from ui.layout.menuView import MenuView
from ui.layout.musicView import MusicView
from ui.layout.selectionView import SelectionView
from ui.layout.sortedView import SortedView
from ui.layout.timerView import TimerView
from ui.manager.affichage_borne import (
    determiner_drapeaux_fenetre,
    determiner_mode_affichage,
    determiner_resolution_borne,
)
from ui.utils.color import Color


class WindowManager:
    """Centralise la fenetre et les vues PianoTile."""

    def __init__(self, interface):
        """Initialise la fenetre principale et les vues associees.

        Args:
            interface: Interface applicative racine.

        Returns:
            Aucun.
        """

        self.__interface = interface
        self.__screenWidth, self.__screenHeight = determiner_resolution_borne()
        mode_affichage = determiner_mode_affichage()
        drapeaux = determiner_drapeaux_fenetre(mode_affichage)
        self.__window = pygame.display.set_mode((self.__screenWidth, self.__screenHeight), drapeaux)
        pygame.mouse.set_visible(False)
        self.__fontTall = pygame.font.Font("./assets/font/Tinos-Regular.ttf", 40)
        self.__fontSmall = pygame.font.Font("./assets/font/Tinos-Regular.ttf", 30)
        self.__color = Color()
        self.__scrollOffset = 0
        self.__sorted = SortedView(self)
        self.__musicSelect = None
        self.__currentUser = Player(0, "Invite", "invite")
        self.__areaMusic = pygame.Rect(50, 200, self.__screenWidth - 100, self.__screenHeight - 375)
        self.__background = BackgroundView(self)
        self.__music = MusicView(self)
        self.__menu = MenuView(self)
        self.__selection = SelectionView(self)
        self.__timer = TimerView(self)
        self.__game = None

    def getInterface(self):
        """Retourne l interface racine.

        Args:
            Aucun.

        Returns:
            Interface applicative.
        """

        return self.__interface

    def getWindow(self):
        """Retourne la fenetre pygame principale.

        Args:
            Aucun.

        Returns:
            Surface principale.
        """

        return self.__window

    def getScreenWidth(self):
        """Retourne la largeur utile.

        Args:
            Aucun.

        Returns:
            Largeur en pixels.
        """

        return self.__screenWidth

    def getScreenHeight(self):
        """Retourne la hauteur utile.

        Args:
            Aucun.

        Returns:
            Hauteur en pixels.
        """

        return self.__screenHeight

    def getFontTall(self):
        """Retourne la grande police.

        Args:
            Aucun.

        Returns:
            Police pygame.
        """

        return self.__fontTall

    def getFontSmall(self):
        """Retourne la petite police.

        Args:
            Aucun.

        Returns:
            Police pygame.
        """

        return self.__fontSmall

    def getColor(self):
        """Retourne le theme de couleurs.

        Args:
            Aucun.

        Returns:
            Instance `Color`.
        """

        return self.__color

    def getMusicSelect(self):
        """Retourne la musique selectionnee.

        Args:
            Aucun.

        Returns:
            Nom de musique ou `None`.
        """

        return self.__musicSelect

    def getCurrentUser(self):
        """Retourne l utilisateur courant.

        Args:
            Aucun.

        Returns:
            Joueur courant.
        """

        return self.__currentUser

    def setCurrentUser(self, user):
        """Met a jour l utilisateur courant.

        Args:
            user: Joueur a memoriser.

        Returns:
            Aucun.
        """

        self.__currentUser = user

    def getSorted(self):
        """Retourne la vue de tri.

        Args:
            Aucun.

        Returns:
            Vue de tri.
        """

        return self.__sorted

    def getAreaMusic(self):
        """Retourne la zone visible des musiques.

        Args:
            Aucun.

        Returns:
            Rectangle visible.
        """

        return self.__areaMusic

    def getScrollOffset(self):
        """Retourne le decalage de defilement courant.

        Args:
            Aucun.

        Returns:
            Entier de decalage.
        """

        return self.__scrollOffset

    def setScrollOffset(self, offset):
        """Met a jour le decalage de defilement dans les bornes visibles.

        Args:
            offset: Variation de decalage.

        Returns:
            Aucun.
        """

        self.__scrollOffset += offset
        if self.__scrollOffset < 0:
            self.__scrollOffset = 0
        elif self.__scrollOffset > self.__areaMusic.height:
            self.__scrollOffset = self.__areaMusic.height

    def setMusicSelect(self, musicSelect):
        """Met a jour la musique selectionnee.

        Args:
            musicSelect: Musique selectionnee.

        Returns:
            Aucun.
        """

        self.__musicSelect = musicSelect
        if "Detail " not in self.getSelection().getSelection()[1][self.getSelection().getPosition()][0]:
            self.__game = GameView(self)

    def setSelection(self, selection):
        """Met a jour la selection courante.

        Args:
            selection: Vue de selection.

        Returns:
            Aucun.
        """

        self.__selection = selection

    def getBackground(self):
        """Retourne la vue de fond.

        Args:
            Aucun.

        Returns:
            Vue de fond.
        """

        return self.__background

    def getMusic(self):
        """Retourne la vue de musiques.

        Args:
            Aucun.

        Returns:
            Vue de musiques.
        """

        return self.__music

    def getMenu(self):
        """Retourne la vue menu.

        Args:
            Aucun.

        Returns:
            Vue menu.
        """

        return self.__menu

    def getSelection(self):
        """Retourne la vue de selection.

        Args:
            Aucun.

        Returns:
            Vue de selection.
        """

        return self.__selection

    def getGame(self):
        """Retourne la vue de jeu courante.

        Args:
            Aucun.

        Returns:
            Vue de jeu ou `None`.
        """

        return self.__game

    def setGame(self, game):
        """Met a jour la vue de jeu courante.

        Args:
            game: Vue de jeu a memoriser.

        Returns:
            Aucun.
        """

        self.__game = game
