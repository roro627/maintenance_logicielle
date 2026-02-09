import java.awt.Canvas;
import java.awt.event.KeyEvent;

/**
 * Verifie la correspondance entre touches clavier et boutons borne.
 */
public class TestUnitaireClavierBorneArcade {

    /**
     * Point d entree du test unitaire.
     *
     * @param args arguments CLI non utilises.
     */
    public static void main(String[] args) {
        ClavierBorneArcade clavier = new ClavierBorneArcade();
        Canvas source = new Canvas();

        simulerAppuiEtRelachement(clavier, source, KeyEvent.VK_F);
        assertCondition(clavier.getBoutonJ1AEnfoncee(), "VK_F doit activer bouton J1A enfonce");
        simulerRelachement(clavier, source, KeyEvent.VK_F);
        assertCondition(clavier.getBoutonJ1ATape(), "VK_F doit activer bouton J1A tape");

        simulerAppuiEtRelachement(clavier, source, KeyEvent.VK_UP);
        assertCondition(clavier.getJoyJ1HautEnfoncee(), "VK_UP doit activer joy J1 haut enfonce");
        simulerRelachement(clavier, source, KeyEvent.VK_UP);
        assertCondition(clavier.getJoyJ1HautTape(), "VK_UP doit activer joy J1 haut tape");

        simulerAppuiEtRelachement(clavier, source, KeyEvent.VK_Q);
        assertCondition(clavier.getBoutonJ2AEnfoncee(), "VK_Q doit activer bouton J2A enfonce");
        simulerRelachement(clavier, source, KeyEvent.VK_Q);
        assertCondition(clavier.getBoutonJ2ATape(), "VK_Q doit activer bouton J2A tape");
    }

    /**
     * Simule un appui de touche.
     *
     * @param clavier clavier borne.
     * @param source composant source AWT.
     * @param codeTouche code de touche.
     */
    private static void simulerAppuiEtRelachement(ClavierBorneArcade clavier, Canvas source, int codeTouche) {
        KeyEvent appui = new KeyEvent(source, KeyEvent.KEY_PRESSED, System.currentTimeMillis(), 0,
                codeTouche, KeyEvent.CHAR_UNDEFINED);
        clavier.keyPressed(appui);
    }

    /**
     * Simule un relachement de touche.
     *
     * @param clavier clavier borne.
     * @param source composant source AWT.
     * @param codeTouche code de touche.
     */
    private static void simulerRelachement(ClavierBorneArcade clavier, Canvas source, int codeTouche) {
        KeyEvent relachement = new KeyEvent(source, KeyEvent.KEY_RELEASED, System.currentTimeMillis(), 0,
                codeTouche, KeyEvent.CHAR_UNDEFINED);
        clavier.keyReleased(relachement);
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
