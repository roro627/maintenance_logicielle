"""Gestion des notes et de la musique pour PianoTile."""

import random
import pygame

from ui.utils.note import Note

try:
    import librosa  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - fallback runtime
    librosa = None


SEUIL_SAMPLE_RATE = 22050
INTERVALLE_MINIMAL = 0.30
INTERVALLE_BASE = 1.10
DUREE_PAR_DEFAUT = 45.0
DEPART_NOTES = 0.50


class Piano:
    """Represente la piste musicale et les notes jouables."""

    def __init__(self, gameview):
        """Initialise la piste courante et pre-genere les notes.

        Args:
            gameview: Vue de jeu associee.

        Returns:
            Aucun.
        """

        self.__gameView = gameview
        self.__filepath = (
            "./assets/music/"
            + self.__gameView.getWindowManager()
            .getMusicSelect()
            .lower()
            .replace("play musique ", "")
            .replace(" ", "")
            .replace("'", "")
            .replace(",", "")
            + ".mp3"
        )
        self.__difficulty = 1
        self.__notes = self.generate_notes()

    def getNotes(self):
        """Retourne la liste des notes pre-generees.

        Args:
            Aucun.

        Returns:
            Liste des objets Note.
        """

        return self.__notes

    def increaseDifficulty(self):
        """Augmente la difficulte de generation des notes.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        self.__difficulty += 1

    def play(self):
        """Demarre la lecture de la musique.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        pygame.mixer.init()
        pygame.mixer.music.load(self.__filepath)
        pygame.mixer.music.play()

    def pause(self):
        """Met en pause la musique en cours.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        pygame.mixer.music.pause()

    def generate_notes(self):
        """Genere les notes en fonction du morceau charge.

        Args:
            Aucun.

        Returns:
            Liste de notes ordonnee dans le temps.
        """

        if librosa is not None:
            notes = self.__generate_notes_librosa()
            if notes:
                return notes
        return self.__generate_notes_fallback()

    def __generate_notes_librosa(self):
        """Genere des notes basees sur les battements librosa.

        Args:
            Aucun.

        Returns:
            Liste de notes, possiblement vide en cas d echec.
        """

        try:
            y_signal, sample_rate = librosa.load(self.__filepath, sr=SEUIL_SAMPLE_RATE, mono=True)
            _, beat_frames = librosa.beat.beat_track(y=y_signal, sr=sample_rate)
            beat_times = librosa.frames_to_time(beat_frames, sr=sample_rate)
        except Exception:
            return []

        notes = []
        for temps in beat_times:
            nb_notes = min(self.__difficulty, random.randint(1, 4))
            for _ in range(nb_notes):
                position = random.choice(["left", "middle", "right", "top"])
                note = Note(gameview=self.__gameView, position=position, timestamp=float(temps))
                notes.append(note)
        return notes

    def __generate_notes_fallback(self):
        """Genere des notes sans librosa avec une cadence reguliere.

        Args:
            Aucun.

        Returns:
            Liste de notes avec generation legere en RAM.
        """

        duree = self.__estimer_duree_morceau()
        intervalle = max(INTERVALLE_MINIMAL, INTERVALLE_BASE - (self.__difficulty * 0.08))

        notes = []
        temps = DEPART_NOTES
        while temps < duree:
            nb_notes = min(self.__difficulty, random.randint(1, 3))
            for _ in range(nb_notes):
                position = random.choice(["left", "middle", "right", "top"])
                note = Note(gameview=self.__gameView, position=position, timestamp=float(temps))
                notes.append(note)
            temps += intervalle
        return notes

    def __estimer_duree_morceau(self):
        """Estime la duree du morceau pour le fallback.

        Args:
            Aucun.

        Returns:
            Duree estimee en secondes.
        """

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            son = pygame.mixer.Sound(self.__filepath)
            duree = float(son.get_length())
            if duree > 1.0:
                return duree
        except Exception:
            pass
        return DUREE_PAR_DEFAUT

    def getCurrentTime(self):
        """Retourne le temps courant de lecture du morceau.

        Args:
            Aucun.

        Returns:
            Temps courant en secondes.
        """

        return pygame.mixer.music.get_pos() / 1000.0
