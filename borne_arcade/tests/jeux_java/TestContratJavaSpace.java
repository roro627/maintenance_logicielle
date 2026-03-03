import java.awt.Canvas;
import java.awt.event.KeyEvent;

import MG2D.geometrie.Point;
import MG2D.geometrie.Texture;

/**
 * Verifie les contrats logiques critiques de JavaSpace.
 */
public class TestContratJavaSpace {

    /**
     * Point d entree du test de contrat.
     *
     * @param args arguments CLI non utilises.
     */
    public static void main(String[] args) {
        testerApparitionEtRebondVerticalDuBoss();
        testerBornageDuJoueur();
    }

    /**
     * Verifie l entree du boss et son rebond vertical.
     */
    private static void testerApparitionEtRebondVerticalDuBoss() {
        Boss boss = new Boss(new Texture("img/ennemie/boss/0.png", new Point(1180, 900), 100, 40), 0, 0, 4);
        boolean encoreVisible = boss.apparition();
        assertCondition(encoreVisible, "Le boss doit rester en apparition tant qu il n a pas depasse l ecran");

        boss.setTex(new Texture("img/ennemie/boss/0.png", new Point(1200, 1010), 100, 40));
        boss.setTraj(4);
        boss.deplacement();
        assertCondition(boss.getTraj() == -4, "Le boss doit rebondir sur la bordure haute");

        boss.setTex(new Texture("img/ennemie/boss/0.png", new Point(1200, 0), 100, 40));
        boss.setTraj(-4);
        boss.deplacement();
        assertCondition(boss.getTraj() == 4, "Le boss doit rebondir sur la bordure basse");
    }

    /**
     * Verifie que le joueur reste dans les bornes autorisees.
     */
    private static void testerBornageDuJoueur() {
        Joueur joueur = new Joueur(new Texture("img/player/player1/1.png", new Point(5, 5), 64, 64), 3, 0, 0, 0, 0, 0);
        ClavierBorneArcade clavier = new ClavierBorneArcade();
        Canvas source = new Canvas();

        simulerAppui(clavier, source, KeyEvent.VK_LEFT);
        joueur.bougerJoueur(clavier, 0, Jeu.LARGEUR, 0, Jeu.HAUTEUR, 10, 10, 64, 64);
        simulerRelachement(clavier, source, KeyEvent.VK_LEFT);
        assertCondition(joueur.getTex().getA().getX() == 5, "Le joueur ne doit pas sortir par la gauche");

        joueur.getTex().setA(new Point(Jeu.LARGEUR - 69, 5));
        simulerAppui(clavier, source, KeyEvent.VK_RIGHT);
        joueur.bougerJoueur(clavier, 0, Jeu.LARGEUR, 0, Jeu.HAUTEUR, 10, 10, 64, 64);
        simulerRelachement(clavier, source, KeyEvent.VK_RIGHT);
        assertCondition(joueur.getTex().getA().getX() == Jeu.LARGEUR - 69, "Le joueur ne doit pas sortir par la droite");

        joueur.getTex().setA(new Point(20, 10));
        simulerAppui(clavier, source, KeyEvent.VK_UP);
        joueur.bougerJoueur(clavier, 0, Jeu.LARGEUR, 0, Jeu.HAUTEUR, 10, 10, 64, 64);
        simulerRelachement(clavier, source, KeyEvent.VK_UP);
        assertCondition(joueur.getTex().getA().getY() == 20, "Le joueur doit pouvoir monter dans la zone autorisee");

        joueur.getTex().setA(new Point(20, 5));
        simulerAppui(clavier, source, KeyEvent.VK_DOWN);
        joueur.bougerJoueur(clavier, 0, Jeu.LARGEUR, 0, Jeu.HAUTEUR, 10, 10, 64, 64);
        simulerRelachement(clavier, source, KeyEvent.VK_DOWN);
        assertCondition(joueur.getTex().getA().getY() == 5, "Le joueur ne doit pas sortir par le bas");
    }

    /**
     * Simule un appui de touche.
     *
     * @param clavier clavier a alimenter.
     * @param source composant source.
     * @param codeTouche code AWT a simuler.
     */
    private static void simulerAppui(ClavierBorneArcade clavier, Canvas source, int codeTouche) {
        KeyEvent evenement = new KeyEvent(
            source,
            KeyEvent.KEY_PRESSED,
            System.currentTimeMillis(),
            0,
            codeTouche,
            KeyEvent.CHAR_UNDEFINED
        );
        clavier.keyPressed(evenement);
    }

    /**
     * Simule un relachement de touche.
     *
     * @param clavier clavier a alimenter.
     * @param source composant source.
     * @param codeTouche code AWT a simuler.
     */
    private static void simulerRelachement(ClavierBorneArcade clavier, Canvas source, int codeTouche) {
        KeyEvent evenement = new KeyEvent(
            source,
            KeyEvent.KEY_RELEASED,
            System.currentTimeMillis(),
            0,
            codeTouche,
            KeyEvent.CHAR_UNDEFINED
        );
        clavier.keyReleased(evenement);
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
