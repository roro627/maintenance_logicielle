import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;

/**
 * Verifie la lecture et l ecriture des highscores.
 */
public class TestUnitaireHighScore {

    /**
     * Point d entree du test unitaire.
     *
     * @param args arguments CLI non utilises.
     * @throws IOException en cas d erreur de fichier.
     */
    public static void main(String[] args) throws IOException {
        File fichier = File.createTempFile("highscore_test", ".txt");
        ecrireLignesInitiales(fichier);

        ArrayList<LigneHighScore> avant = HighScore.lireFichier(fichier.getAbsolutePath());
        assertCondition(avant.size() == 3, "La lecture initiale doit retourner 3 lignes");

        HighScore.enregistrerFichier(fichier.getAbsolutePath(), avant, "ZZZ", 250);

        ArrayList<LigneHighScore> apres = HighScore.lireFichier(fichier.getAbsolutePath());
        assertCondition(apres.size() == 4, "La liste doit contenir 4 scores apres insertion");
        assertCondition("ZZZ".equals(apres.get(0).getNom()), "Le nouveau score doit etre en tete");
        assertCondition(apres.get(0).getScore() == 250, "Le meilleur score doit valoir 250");

        fichier.delete();
    }

    /**
     * Ecrit un fichier highscore minimal.
     *
     * @param fichier cible du test.
     * @throws IOException en cas d erreur d ecriture.
     */
    private static void ecrireLignesInitiales(File fichier) throws IOException {
        try (FileWriter ecrivain = new FileWriter(fichier, false)) {
            ecrivain.write("AAA-100\n");
            ecrivain.write("BBB-80\n");
            ecrivain.write("CCC-10\n");
        }
    }

    /**
     * Verifie une condition et leve une exception en cas d echec.
     *
     * @param condition resultat attendu.
     * @param message message d erreur.
     */
    private static void assertCondition(boolean condition, String message) {
        if (!condition) {
            throw new IllegalStateException(message);
        }
    }
}
