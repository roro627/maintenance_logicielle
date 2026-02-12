"""Gestion des notes et de la musique pour PianoTile."""

import os
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
VARIATION_INTERVALLE_DIFFICULTE = 0.08
DEPART_NOTES = 0.50
DUREE_PAR_DEFAUT = 45.0
NOTES_MAX_PAR_BATTEMENT = 4
NOTES_MAX_PAR_CYCLE_FALLBACK = 3
POSITIONS_NOTES = ["left", "middle", "right", "top"]

VARIABLE_ENV_LIBROSA = "PIANOTILE_ACTIVER_LIBROSA"
VALEURS_ACTIVATION = {"1", "true", "oui", "yes"}
ACTIVER_ANALYSE_LIBROSA_PAR_DEFAUT = False

FREQUENCE_MIXEUR_HZ = 44100
TAILLE_ECHANTILLON_BITS = -16
NOMBRE_CANAUX_MIXEUR = 2
TAILLE_BUFFER_MIXEUR = 512
SECONDES_PAR_MILLISECONDE = 1000.0
SEUIL_LECTURE_AUDIO_INVALIDE = 0.0


def activer_analyse_librosa_depuis_environnement() -> bool:
    """Determine si l analyse audio librosa est activee.

    Args:
        Aucun.

    Returns:
        True si l analyse librosa doit etre activee, sinon False.
    """

    valeur = os.environ.get(VARIABLE_ENV_LIBROSA, "")
    if not valeur:
        return ACTIVER_ANALYSE_LIBROSA_PAR_DEFAUT
    return valeur.strip().lower() in VALEURS_ACTIVATION


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
        self.__analyse_librosa_active = librosa is not None and activer_analyse_librosa_depuis_environnement()
        self.__instant_depart_lecture = 0.0
        self.__lecture_audio_active = False
        self.__derniere_erreur_audio = ""
        self.__notes = self.generate_notes()

    def getNotes(self):
        """Retourne la liste des notes pre-generees.

        Args:
            Aucun.

        Returns:
            Liste des objets Note.
        """

        return self.__notes

    def getDerniereErreurAudio(self) -> str:
        """Retourne le dernier message d erreur audio.

        Args:
            Aucun.

        Returns:
            Message d erreur audio, ou chaine vide.
        """

        return self.__derniere_erreur_audio

    def estLectureAudioActive(self) -> bool:
        """Indique si la lecture audio est active.

        Args:
            Aucun.

        Returns:
            True si l audio est en cours de lecture.
        """

        return self.__lecture_audio_active

    def increaseDifficulty(self):
        """Augmente la difficulte de generation des notes.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        self.__difficulty += 1

    def obtenir_temps_systeme_secondes(self) -> float:
        """Retourne le temps systeme pygame en secondes.

        Args:
            Aucun.

        Returns:
            Temps ecoule depuis le lancement pygame.
        """

        return pygame.time.get_ticks() / SECONDES_PAR_MILLISECONDE

    def play(self):
        """Demarre la lecture de la musique sans bloquer la boucle principale.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        self.__instant_depart_lecture = self.obtenir_temps_systeme_secondes()
        self.__lecture_audio_active = False
        self.__derniere_erreur_audio = ""

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(
                    frequency=FREQUENCE_MIXEUR_HZ,
                    size=TAILLE_ECHANTILLON_BITS,
                    channels=NOMBRE_CANAUX_MIXEUR,
                    buffer=TAILLE_BUFFER_MIXEUR,
                )
            pygame.mixer.music.load(self.__filepath)
            pygame.mixer.music.play()
            self.__lecture_audio_active = True
        except pygame.error as erreur:
            self.__derniere_erreur_audio = (
                f"Lecture audio indisponible ({erreur}). "
                "Action recommandee: verifier la presence des fichiers mp3 et la sortie audio ALSA/PulseAudio."
            )
            print(self.__derniere_erreur_audio)

    def pause(self):
        """Met en pause la musique en cours.

        Args:
            Aucun.

        Returns:
            Aucun.
        """

        if not self.__lecture_audio_active:
            return
        try:
            pygame.mixer.music.pause()
        except pygame.error:
            self.__lecture_audio_active = False

    def generate_notes(self):
        """Genere les notes en fonction du morceau charge.

        Args:
            Aucun.

        Returns:
            Liste de notes ordonnee dans le temps.
        """

        if self.__analyse_librosa_active:
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
        except Exception:  # pylint: disable=broad-exception-caught
            return []

        notes = []
        for temps in beat_times:
            nb_notes = min(self.__difficulty, random.randint(1, NOTES_MAX_PAR_BATTEMENT))
            for _ in range(nb_notes):
                position = random.choice(POSITIONS_NOTES)
                note = Note(gameview=self.__gameView, position=position, timestamp=float(temps))
                notes.append(note)
        return notes

    def __generate_notes_fallback(self):
        """Genere des notes sans analyse audio pour garantir la fluidite.

        Args:
            Aucun.

        Returns:
            Liste de notes avec generation legere en RAM.
        """

        duree = self.__estimer_duree_morceau()
        intervalle = max(
            INTERVALLE_MINIMAL,
            INTERVALLE_BASE - (self.__difficulty * VARIATION_INTERVALLE_DIFFICULTE),
        )

        notes = []
        temps = DEPART_NOTES
        while temps < duree:
            nb_notes = min(self.__difficulty, random.randint(1, NOTES_MAX_PAR_CYCLE_FALLBACK))
            for _ in range(nb_notes):
                position = random.choice(POSITIONS_NOTES)
                note = Note(gameview=self.__gameView, position=position, timestamp=float(temps))
                notes.append(note)
            temps += intervalle
        return notes

    def __estimer_duree_morceau(self):
        """Retourne une duree stable sans charger le MP3 en memoire.

        Args:
            Aucun.

        Returns:
            Duree estimee en secondes.
        """

        return DUREE_PAR_DEFAUT

    def getCurrentTime(self):
        """Retourne le temps courant de lecture du morceau.

        Args:
            Aucun.

        Returns:
            Temps courant en secondes.
        """

        if self.__instant_depart_lecture <= 0:
            return 0.0

        if self.__lecture_audio_active and pygame.mixer.get_init():
            position_audio = pygame.mixer.music.get_pos() / SECONDES_PAR_MILLISECONDE
            if position_audio > SEUIL_LECTURE_AUDIO_INVALIDE:
                return position_audio

        temps_ecoule = self.obtenir_temps_systeme_secondes() - self.__instant_depart_lecture
        return max(0.0, temps_ecoule)
