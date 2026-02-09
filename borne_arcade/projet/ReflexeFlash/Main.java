/**
 * Point d entree du jeu ReflexeFlash.
 */
public class Main {

    /**
     * Lance une partie courte de ReflexeFlash.
     *
     * @param args arguments CLI non utilises.
     */
    public static void main(String[] args) {
        Jeu jeu = new Jeu("highscore");
        jeu.demarrer();

        for (int tentative = 0; tentative < 5; tentative++) {
            jeu.incrementerScore();
        }

        jeu.arreter();
        System.out.println("ReflexeFlash termine. Score: " + jeu.getScoreCourant()
                + " / Meilleur: " + jeu.getMeilleurScore());
    }
}
