/**
 * Verifie les contrats logiques critiques du jeu Columns.
 */
public class TestContratColumns {

    /**
     * Point d entree du test de contrat.
     *
     * @param args arguments CLI non utilises.
     */
    public static void main(String[] args) {
        testerDetectionComboHorizontal();
        testerSuppressionAnimeeJusquAuVide();
        testerChuteGravitaire();
        testerDeplacementColonneEtRotation();
    }

    /**
     * Verifie la detection d un alignement horizontal.
     */
    private static void testerDetectionComboHorizontal() {
        Puits puits = new Puits(0, 0, 1);
        viderGrille(puits);
        puits.getGrille()[0][0] = new Gemme(Gemme.BLEU);
        puits.getGrille()[1][0] = new Gemme(Gemme.BLEU);
        puits.getGrille()[2][0] = new Gemme(Gemme.BLEU);

        int supprimees = puits.verification();

        assertCondition(supprimees == 3, "Un combo horizontal de 3 gemmes doit etre detecte");
        assertCondition(
            puits.getGrille()[0][0].getCouleur() == -Gemme.NBFRAMESUPPR,
            "Les gemmes detectees doivent passer en etat de suppression"
        );
    }

    /**
     * Verifie que l animation de suppression finit sur des cases vides.
     */
    private static void testerSuppressionAnimeeJusquAuVide() {
        Puits puits = new Puits(0, 0, 1);
        viderGrille(puits);
        puits.getGrille()[0][0] = new Gemme(Gemme.ROUGE);
        puits.getGrille()[1][1] = new Gemme(Gemme.ROUGE);
        puits.getGrille()[2][2] = new Gemme(Gemme.ROUGE);
        puits.verification();

        for (int iteration = 0; iteration < Gemme.NBFRAMESUPPR; iteration++) {
            puits.animSuppr();
        }

        assertCondition(puits.getGrille()[0][0].getCouleur() == Gemme.VIDE, "La gemme doit disparaitre apres l animation");
        assertCondition(puits.getGrille()[1][1].getCouleur() == Gemme.VIDE, "La gemme doit finir vide");
        assertCondition(puits.getGrille()[2][2].getCouleur() == Gemme.VIDE, "La gemme doit finir vide");
    }

    /**
     * Verifie la gravite des gemmes apres une suppression.
     */
    private static void testerChuteGravitaire() {
        Puits puits = new Puits(0, 0, 1);
        viderGrille(puits);
        puits.getGrille()[0][2] = new Gemme(Gemme.JAUNE);

        boolean chuteDetectee = puits.verifChute();

        assertCondition(chuteDetectee, "Une gemme suspendue doit chuter");
        assertCondition(puits.getGrille()[0][1].getCouleur() == Gemme.JAUNE, "La gemme doit etre descendue d un cran");
        assertCondition(puits.getGrille()[0][2].getCouleur() == Gemme.VIDE, "L ancienne case doit devenir vide");
    }

    /**
     * Verifie la rotation et les blocages lateraux de la colonne courante.
     */
    private static void testerDeplacementColonneEtRotation() {
        Puits puits = new Puits(0, 0, 1);
        viderGrille(puits);
        Colone colonne = puits.getColoneCourante();
        colonne.setX(1);
        colonne.setY(5);
        colonne.getGemme(0).setCouleur(Gemme.JAUNE);
        colonne.getGemme(1).setCouleur(Gemme.ORANGE);
        colonne.getGemme(2).setCouleur(Gemme.VERT);

        colonne.intervertir();
        assertCondition(colonne.getCouleurGemme(0) == Gemme.ORANGE, "La rotation doit remonter la gemme centrale");
        assertCondition(colonne.getCouleurGemme(1) == Gemme.VERT, "La rotation doit decaler la gemme haute");
        assertCondition(colonne.getCouleurGemme(2) == Gemme.JAUNE, "La rotation doit descendre la gemme basse");

        colonne.deplacer(1, puits.getGrille());
        assertCondition(colonne.getX() == 2, "La colonne doit pouvoir se deplacer vers la droite");

        puits.getGrille()[3][5] = new Gemme(Gemme.ROUGE);
        colonne.deplacer(1, puits.getGrille());
        assertCondition(colonne.getX() == 2, "La colonne ne doit pas traverser une case occupee");

        colonne.setX(0);
        colonne.deplacer(-1, puits.getGrille());
        assertCondition(colonne.getX() == 0, "La colonne ne doit pas sortir par la gauche");
    }

    /**
     * Vide integralement la grille d un puits.
     *
     * @param puits puits a nettoyer.
     */
    private static void viderGrille(Puits puits) {
        for (int x = 0; x < Puits.LARGEUR; x++) {
            for (int y = 0; y < Puits.HAUTEUR; y++) {
                puits.getGrille()[x][y] = new Gemme(Gemme.VIDE);
            }
        }
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
