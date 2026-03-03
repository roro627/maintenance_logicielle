import java.io.IOException;

/**
 * Lance un jeu via son script shell reel.
 */
public final class LanceurJeuProcessus implements LanceurJeuMenu {

    /**
     * Lance le script du jeu cible puis attend sa fin.
     *
     * @param jeu jeu a lancer.
     * @throws IOException si le script ne peut pas etre execute.
     * @throws InterruptedException si le thread est interrompu pendant l attente.
     */
    @Override
    public void lancerJeu(JeuCatalogue jeu) throws IOException, InterruptedException {
        ProcessBuilder constructeur = new ProcessBuilder("./" + jeu.getCheminLanceur());
        Process process = constructeur.start();
        process.waitFor();
    }
}
