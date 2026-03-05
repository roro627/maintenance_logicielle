import java.awt.Canvas;
import java.awt.event.KeyEvent;

/**
 * Verifie les contrats non graphiques critiques de Puissance_X.
 */
public class TestContratPuissanceX {

    /**
     * Point d entree du test de contrat Puissance_X.
     *
     * @param args arguments CLI non utilises.
     */
    public static void main(String[] args) {
        testerPlacementEtColonnePleine();
        testerAlignementHorizontal();
        testerAlignementVertical();
        testerAlignementDiagonal();
        testerMatchNul();
        testerAliasNumeriquesEntreeBorne();
    }

    /**
     * Verifie le placement des pions et la detection de colonne pleine.
     */
    private static void testerPlacementEtColonnePleine() {
        Plateau plateau = new Plateau(2, 2, 2);
        assertCondition(plateau.ajoutPion(0, 1) == 0, "Le premier pion doit tomber sur la ligne 0");
        assertCondition(plateau.ajoutPion(0, 2) == 1, "Le second pion doit tomber sur la ligne 1");
        assertCondition(plateau.ajoutPion(0, 1) == -1, "Une colonne pleine doit retourner -1");
    }

    /**
     * Verifie la detection d un alignement horizontal.
     */
    private static void testerAlignementHorizontal() {
        Plateau plateau = new Plateau(4, 4, 4);
        for (int colonne = 0; colonne < 4; colonne++) {
            plateau.ajoutPion(colonne, 1);
        }
        assertCondition(plateau.gagne() == 1, "Un alignement horizontal devait donner la victoire au joueur 1");
    }

    /**
     * Verifie la detection d un alignement vertical.
     */
    private static void testerAlignementVertical() {
        Plateau plateau = new Plateau(4, 4, 4);
        for (int index = 0; index < 4; index++) {
            plateau.ajoutPion(1, 2);
        }
        assertCondition(plateau.gagne() == 2, "Un alignement vertical devait donner la victoire au joueur 2");
    }

    /**
     * Verifie la detection d un alignement diagonal.
     */
    private static void testerAlignementDiagonal() {
        Plateau plateau = new Plateau(4, 4, 4);
        plateau.ajoutPion(0, 1);
        plateau.ajoutPion(1, 2);
        plateau.ajoutPion(1, 1);
        plateau.ajoutPion(2, 2);
        plateau.ajoutPion(2, 2);
        plateau.ajoutPion(2, 1);
        plateau.ajoutPion(3, 2);
        plateau.ajoutPion(3, 2);
        plateau.ajoutPion(3, 2);
        plateau.ajoutPion(3, 1);
        assertCondition(plateau.gagne() == 1, "Un alignement diagonal devait donner la victoire au joueur 1");
    }

    /**
     * Verifie la detection de match nul.
     */
    private static void testerMatchNul() {
        Plateau plateau = new Plateau(2, 2, 3);
        plateau.ajoutPion(0, 1);
        plateau.ajoutPion(0, 2);
        plateau.ajoutPion(1, 2);
        plateau.ajoutPion(1, 1);
        assertCondition(plateau.gagne() == 0, "Un plateau plein sans alignement doit produire un match nul");
    }

    /**
     * Verifie les alias numeriques des boutons J1 pour l entree borne.
     */
    private static void testerAliasNumeriquesEntreeBorne() {
        Entree entree = new Entree();
        Canvas source = new Canvas();

        simulerAppui(entree, source, KeyEvent.VK_1);
        assertCondition(entree.entree(0), "VK_1 devait agir comme validation J1");
        simulerRelachement(entree, source, KeyEvent.VK_1);

        simulerAppui(entree, source, KeyEvent.VK_4);
        assertCondition(entree.echap(0), "VK_4 devait agir comme retour J1");
        simulerRelachement(entree, source, KeyEvent.VK_4);
    }

    /**
     * Simule un appui de touche.
     *
     * @param entree entree clavier Puissance_X.
     * @param source composant source AWT.
     * @param codeTouche code de touche simule.
     */
    private static void simulerAppui(Entree entree, Canvas source, int codeTouche) {
        KeyEvent appui = new KeyEvent(
            source,
            KeyEvent.KEY_PRESSED,
            System.currentTimeMillis(),
            0,
            codeTouche,
            KeyEvent.CHAR_UNDEFINED
        );
        entree.keyPressed(appui);
    }

    /**
     * Simule un relachement de touche.
     *
     * @param entree entree clavier Puissance_X.
     * @param source composant source AWT.
     * @param codeTouche code de touche simule.
     */
    private static void simulerRelachement(Entree entree, Canvas source, int codeTouche) {
        KeyEvent relachement = new KeyEvent(
            source,
            KeyEvent.KEY_RELEASED,
            System.currentTimeMillis(),
            0,
            codeTouche,
            KeyEvent.CHAR_UNDEFINED
        );
        entree.keyReleased(relachement);
    }

    /**
     * Leve une erreur claire si la condition est fausse.
     *
     * @param condition condition attendue.
     * @param message message d erreur.
     */
    private static void assertCondition(boolean condition, String message) {
        if (!condition) {
            throw new IllegalStateException(message);
        }
    }
}
