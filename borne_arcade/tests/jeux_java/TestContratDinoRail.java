import MG2D.geometrie.Point;
import MG2D.geometrie.Rectangle;

/**
 * Verifie les contrats non graphiques critiques de DinoRail.
 */
public class TestContratDinoRail {
    /** Image de test valide pour instancier un obstacle. */
    private static final String CHEMIN_IMAGE_TEST = "assets/img/cactus.png";

    /**
     * Point d entree du test de contrat DinoRail.
     *
     * @param args arguments CLI non utilises.
     */
    public static void main(String[] args) {
        testerIntersectionObstacle();
        testerAbsenceIntersectionObstacle();
        testerObstacleHorsEcran();
    }

    /**
     * Verifie qu un obstacle detecte bien une collision.
     */
    private static void testerIntersectionObstacle() {
        Obstacle obstacle = new Obstacle(new Point(100, 150), new Point(140, 200), CHEMIN_IMAGE_TEST);
        Rectangle joueur = new Rectangle(MG2D.Couleur.VERT, new Point(110, 150), new Point(180, 240));
        assertCondition(obstacle.intersectionRapide(joueur), "Une collision obstacle/joueur devait etre detectee");
    }

    /**
     * Verifie qu un obstacle n intercepte pas un joueur lointain.
     */
    private static void testerAbsenceIntersectionObstacle() {
        Obstacle obstacle = new Obstacle(new Point(100, 150), new Point(140, 200), CHEMIN_IMAGE_TEST);
        Rectangle joueur = new Rectangle(MG2D.Couleur.VERT, new Point(300, 300), new Point(380, 420));
        assertCondition(!obstacle.intersectionRapide(joueur), "Une collision ne devait pas etre detectee");
    }

    /**
     * Verifie la detection de sortie d ecran.
     */
    private static void testerObstacleHorsEcran() {
        Obstacle obstacleVisible = new Obstacle(new Point(10, 150), new Point(50, 200), CHEMIN_IMAGE_TEST);
        Obstacle obstacleHorsEcran = new Obstacle(new Point(-60, 150), new Point(-10, 200), CHEMIN_IMAGE_TEST);
        assertCondition(!obstacleVisible.isOffScreen(), "L obstacle visible ne doit pas etre marque hors ecran");
        assertCondition(obstacleHorsEcran.isOffScreen(), "L obstacle sorti a gauche doit etre marque hors ecran");
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
