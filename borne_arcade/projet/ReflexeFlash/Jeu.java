import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;

/**
 * Contient la logique metier simplifiee du jeu ReflexeFlash.
 */
public class Jeu {

    /** Fichier de persistance du meilleur score. */
    private final String cheminHighScore;

    /** Etat courant du jeu. */
    private EtatJeu etat;

    /** Score de la session en cours. */
    private int scoreCourant;

    /** Meilleur score persiste. */
    private int meilleurScore;

    /**
     * Construit un jeu ReflexeFlash.
     *
     * @param cheminHighScore chemin du fichier highscore.
     */
    public Jeu(String cheminHighScore) {
        this.cheminHighScore = cheminHighScore;
        this.etat = EtatJeu.ATTENTE;
        this.scoreCourant = 0;
        this.meilleurScore = chargerMeilleurScore();
    }

    /**
     * Demarre une nouvelle session.
     *
     * @return l etat apres demarrage.
     */
    public EtatJeu demarrer() {
        this.scoreCourant = 0;
        this.etat = EtatJeu.EN_COURS;
        return this.etat;
    }

    /**
     * Incremente le score courant d une unite.
     *
     * @return le score courant mis a jour.
     */
    public int incrementerScore() {
        if (this.etat != EtatJeu.EN_COURS) {
            return this.scoreCourant;
        }
        this.scoreCourant++;
        return this.scoreCourant;
    }

    /**
     * Termine la session et sauvegarde le highscore si necessaire.
     *
     * @return l etat final.
     */
    public EtatJeu arreter() {
        this.etat = EtatJeu.TERMINE;
        if (this.scoreCourant > this.meilleurScore) {
            this.meilleurScore = this.scoreCourant;
            sauvegarderMeilleurScore(this.meilleurScore);
        }
        return this.etat;
    }

    /**
     * Retourne l etat courant du jeu.
     *
     * @return etat courant.
     */
    public EtatJeu getEtat() {
        return this.etat;
    }

    /**
     * Retourne le score courant.
     *
     * @return score courant.
     */
    public int getScoreCourant() {
        return this.scoreCourant;
    }

    /**
     * Retourne le meilleur score connu.
     *
     * @return meilleur score.
     */
    public int getMeilleurScore() {
        return this.meilleurScore;
    }

    /**
     * Charge le meilleur score depuis le fichier.
     *
     * @return meilleur score charge ou 0.
     */
    private int chargerMeilleurScore() {
        File fichier = new File(this.cheminHighScore);
        if (!fichier.exists()) {
            return 0;
        }

        try (BufferedReader lecteur = new BufferedReader(new FileReader(fichier))) {
            String ligne = lecteur.readLine();
            if (ligne == null || ligne.trim().isEmpty()) {
                return 0;
            }
            return Integer.parseInt(ligne.trim());
        } catch (IOException | NumberFormatException exception) {
            return 0;
        }
    }

    /**
     * Sauvegarde le meilleur score dans le fichier.
     *
     * @param score score a ecrire.
     */
    private void sauvegarderMeilleurScore(int score) {
        File fichier = new File(this.cheminHighScore);
        File parent = fichier.getParentFile();
        if (parent != null && !parent.exists()) {
            parent.mkdirs();
        }

        try (BufferedWriter ecrivain = new BufferedWriter(new FileWriter(fichier, false))) {
            ecrivain.write(String.valueOf(score));
        } catch (IOException exception) {
            System.err.println("Impossible d ecrire le highscore: " + exception.getMessage());
        }
    }
}
