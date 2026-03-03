/**
 * Verifie les contrats purs du noyau Kowasu Renga.
 */
public class TestContratKowasuRenga {

    /**
     * Point d entree du test de contrat.
     *
     * @param args arguments CLI non utilises.
     */
    public static void main(String[] args) {
        testerInitialisationDesBriques();
        testerPerteDeBalle();
        testerFragilisationEtDestructionBrique();
        testerAccelerationProgressive();
    }

    /**
     * Verifie la creation des 75 briques avec resistances decroissantes.
     */
    private static void testerInitialisationDesBriques() {
        EtatKowasuRenga etat = new EtatKowasuRenga();
        MoteurKowasuRenga moteur = new MoteurKowasuRenga();
        moteur.initialiserBriques(etat);

        assertCondition(etat.getBriques().length == 75, "Le plateau doit contenir 75 emplacements de briques");
        assertCondition(etat.getBriques()[0].getResistance() == 5, "La premiere ligne doit commencer a 5 coups");
        assertCondition(etat.getBriques()[14].getIndexCouleur() == 0, "La premiere ligne doit garder la premiere couleur");
        assertCondition(etat.getBriques()[15].getResistance() == 4, "La deuxieme ligne doit passer a 4 coups");
        assertCondition(etat.getBriques()[74].getResistance() == 1, "La derniere ligne doit etre destructible en un coup");
    }

    /**
     * Verifie le reset complet apres une balle perdue.
     */
    private static void testerPerteDeBalle() {
        EtatKowasuRenga etat = new EtatKowasuRenga();
        MoteurKowasuRenga moteur = new MoteurKowasuRenga();
        etat.setDx(2.0);
        etat.setDy(1);
        etat.setPositionXBalle(900);
        etat.setPositionYBalle(200);

        moteur.perdreBalle(etat);

        assertCondition(etat.getDx() == 0.0, "La balle perdue doit remettre dx a zero");
        assertCondition(etat.getDy() == 0, "La balle perdue doit remettre dy a zero");
        assertCondition(etat.getPositionXBalle() == EtatKowasuRenga.LARGEUR / 2, "La balle doit etre recentree");
        assertCondition(etat.getPositionYBalle() == 80, "La balle doit revenir sur sa hauteur de depart");
        assertCondition(etat.getNbVies() == 2, "Une vie doit etre retiree apres une balle perdue");
    }

    /**
     * Verifie la fragilisation puis la destruction d une brique.
     */
    private static void testerFragilisationEtDestructionBrique() {
        EtatKowasuRenga etat = new EtatKowasuRenga();
        MoteurKowasuRenga moteur = new MoteurKowasuRenga();
        moteur.initialiserBriques(etat);

        moteur.impacterBrique(etat, 0);
        assertCondition(etat.getBriques()[0].getResistance() == 4, "Une brique solide doit perdre un point de resistance");
        assertCondition(etat.getBriques()[0].getIndexCouleur() == 1, "La couleur logique doit avancer d un cran");
        assertCondition(etat.getScore() == 10, "Une fragilisation doit rapporter 10 points");

        BriqueKowasuRenga briqueFragile = etat.getBriques()[74];
        moteur.impacterBrique(etat, 74);
        assertCondition(!briqueFragile.isActive(), "Une brique a un coup doit etre detruite");
        assertCondition(etat.getScore() == 110, "Une destruction doit rapporter 100 points supplementaires");
    }

    /**
     * Verifie l acceleration progressive tous les dix impacts.
     */
    private static void testerAccelerationProgressive() {
        EtatKowasuRenga etat = new EtatKowasuRenga();
        MoteurKowasuRenga moteur = new MoteurKowasuRenga();
        moteur.initialiserBriques(etat);

        for (int index = 0; index < 10; index++) {
            moteur.impacterBrique(etat, index);
        }

        assertCondition(etat.getVitesseCourante() == EtatKowasuRenga.VITESSE_INITIALE - 1, "Le delai doit diminuer apres 10 impacts");
        assertCondition(etat.getImpactsDepuisAcceleration() == 0, "Le compteur d impacts doit etre remis a zero apres acceleration");
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
