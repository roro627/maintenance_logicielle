import MG2D.geometrie.Point;

/**
 * Verifie les contrats purs de Pong.
 */
public class TestContratPong {

    /**
     * Point d entree du test de contrat.
     *
     * @param args arguments CLI non utilises.
     */
    public static void main(String[] args) {
        testerRebondBordures();
        testerPointEtReinitialisation();
        testerReductionRaquetteApresRebond();
        testerRetourMenuAuNeuviemePoint();
        testerCentrageMenu();
    }

    /**
     * Verifie le rebond de la balle sur les bordures.
     */
    private static void testerRebondBordures() {
        EtatPong etat = new EtatPong();
        MoteurPong moteur = new MoteurPong();

        etat.setPositionYBalle(EtatPong.EPAISSEUR_LIGNE + EtatPong.RAYON_BALLE);
        etat.setDy(-1);
        moteur.appliquerRebondBordures(etat);
        assertCondition(etat.getDy() == 1, "La balle doit rebondir sur la bordure basse");

        etat.setPositionYBalle(EtatPong.HAUTEUR - EtatPong.EPAISSEUR_LIGNE - EtatPong.RAYON_BALLE);
        etat.setDy(1);
        moteur.appliquerRebondBordures(etat);
        assertCondition(etat.getDy() == -1, "La balle doit rebondir sur la bordure haute");
    }

    /**
     * Verifie le score et la reinitialisation de manche.
     */
    private static void testerPointEtReinitialisation() {
        EtatPong etat = new EtatPong();
        MoteurPong moteur = new MoteurPong();
        etat.setDemarrer(true);
        etat.setDx(1);
        etat.setDy(1);
        etat.setNbRebond(3);
        etat.setTailleRaquette(100);
        etat.setPositionXBalle(EtatPong.EPAISSEUR_LIGNE + EtatPong.RAYON_BALLE);

        moteur.gererPointsEtReinitialisation(etat, 400);

        assertCondition(etat.getScoreDroit() == 1, "Le joueur droit doit marquer quand la balle sort a gauche");
        assertCondition(!etat.isDemarrer(), "La manche doit etre reinitialisee apres un point");
        assertCondition(etat.getDx() == 0 && etat.getDy() == 0, "La direction de la balle doit etre reinitialisee");
        assertCondition(etat.getNbRebond() == 0, "Le compteur de rebond doit etre remis a zero");
        assertCondition(etat.getTailleRaquette() == EtatPong.TAILLE_RAQUETTE_INITIALE, "La taille des raquettes doit etre restauree");
    }

    /**
     * Verifie la reduction de taille apres un rebond.
     */
    private static void testerReductionRaquetteApresRebond() {
        EtatPong etat = new EtatPong();
        MoteurPong moteur = new MoteurPong();
        int tailleInitiale = etat.getTailleRaquette();

        etat.setNbRebond(1);
        moteur.consommerReductionRaquette(etat);

        assertCondition(etat.getTailleRaquette() == tailleInitiale - (tailleInitiale / 10), "La raquette doit etre reduite de 10 pour cent");
        assertCondition(etat.getNbRebond() == 0, "Le rebond doit etre consomme");
    }

    /**
     * Verifie le signal de retour menu au neuvieme point.
     */
    private static void testerRetourMenuAuNeuviemePoint() {
        EtatPong etat = new EtatPong();
        MoteurPong moteur = new MoteurPong();
        etat.setScoreGauche(8);
        etat.setPositionXBalle(EtatPong.LARGEUR - EtatPong.EPAISSEUR_LIGNE - EtatPong.RAYON_BALLE);

        moteur.gererPointsEtReinitialisation(etat, 512);

        assertCondition(etat.getScoreGauche() == 9, "Le joueur gauche doit atteindre 9 points");
        assertCondition(etat.isRetourMenu(), "Le moteur doit signaler le retour menu a 9 points");
    }

    /**
     * Verifie le recentrage des textes du menu principal.
     */
    private static void testerCentrageMenu() {
        Point centreJouer = Pong.calculerCentreTexteBoutonJouer();
        Point centreQuitter = Pong.calculerCentreTexteBoutonQuitter();
        Point centreTitre = Pong.calculerCentreTitreMenu();

        assertCondition(centreJouer.getX() == EtatPong.LARGEUR / 2, "Le libelle Play doit etre centre horizontalement");
        assertCondition(
            centreJouer.getY() == 225,
            "Le libelle Play doit etre centre verticalement dans son bouton"
        );
        assertCondition(
            centreQuitter.getX() == EtatPong.LARGEUR / 2,
            "Le libelle Exit doit etre centre horizontalement"
        );
        assertCondition(
            centreQuitter.getY() == 125,
            "Le libelle Exit doit etre centre verticalement dans son bouton"
        );
        assertCondition(centreTitre.getX() == EtatPong.LARGEUR / 2, "Le titre doit etre centre horizontalement");
        assertCondition(centreTitre.getY() == (EtatPong.HAUTEUR / 2) + 100, "Le titre doit garder son decalage vertical");
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
