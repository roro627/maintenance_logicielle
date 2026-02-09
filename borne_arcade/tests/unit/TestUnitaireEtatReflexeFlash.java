import java.io.File;

/**
 * Verifie les transitions d etat du jeu ReflexeFlash.
 */
public class TestUnitaireEtatReflexeFlash {

    /**
     * Point d entree du test unitaire.
     *
     * @param args arguments CLI non utilises.
     */
    public static void main(String[] args) {
        String fichier = "test_reflexeflash_highscore.txt";
        Jeu jeu = new Jeu(fichier);

        assertCondition(jeu.getEtat() == EtatJeu.ATTENTE, "Etat initial attendu: ATTENTE");

        jeu.demarrer();
        assertCondition(jeu.getEtat() == EtatJeu.EN_COURS, "Etat apres demarrage attendu: EN_COURS");

        jeu.incrementerScore();
        jeu.incrementerScore();
        assertCondition(jeu.getScoreCourant() == 2, "Le score courant doit valoir 2");

        jeu.arreter();
        assertCondition(jeu.getEtat() == EtatJeu.TERMINE, "Etat final attendu: TERMINE");
        assertCondition(jeu.getMeilleurScore() >= 2, "Le meilleur score doit etre mis a jour");

        new File(fichier).delete();
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
