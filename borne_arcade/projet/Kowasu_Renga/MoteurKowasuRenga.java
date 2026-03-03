/**
 * Centralise les regles pures de Kowasu Renga.
 */
public final class MoteurKowasuRenga {

    /**
     * Initialise les 75 briques du plateau.
     *
     * @param etat etat a initialiser.
     */
    public void initialiserBriques(EtatKowasuRenga etat) {
        int index = 0;
        for (int couleur = 0; couleur < 5; couleur++) {
            int resistance = 5 - couleur;
            for (int colonne = 0; colonne < 15; colonne++) {
                etat.getBriques()[index] = new BriqueKowasuRenga(resistance, couleur);
                index++;
            }
        }
    }

    /**
     * Reinitialise la balle et la raquette apres une balle perdue.
     *
     * @param etat etat a reinitialiser.
     */
    public void perdreBalle(EtatKowasuRenga etat) {
        etat.setDx(0.0);
        etat.setDy(0);
        etat.setPositionXBalle(EtatKowasuRenga.LARGEUR / 2);
        etat.setPositionYBalle(80);
        etat.setPositionXRaquette((EtatKowasuRenga.LARGEUR / 2) - 40);
        etat.setPositionXRaquetteFin((EtatKowasuRenga.LARGEUR / 2) + 40);
        etat.setNbVies(etat.getNbVies() - 1);
        etat.setVitesseCourante(EtatKowasuRenga.VITESSE_INITIALE);
    }

    /**
     * Applique l impact d une balle sur une brique.
     *
     * @param etat etat courant.
     * @param indexBrique index de la brique a impacter.
     */
    public void impacterBrique(EtatKowasuRenga etat, int indexBrique) {
        BriqueKowasuRenga brique = etat.getBriques()[indexBrique];
        if (brique == null || !brique.isActive()) {
            return;
        }

        if (brique.getResistance() == 1) {
            brique.setActive(false);
            etat.setScore(etat.getScore() + 100);
        } else {
            brique.setResistance(brique.getResistance() - 1);
            brique.setIndexCouleur(brique.getIndexCouleur() + 1);
            etat.setScore(etat.getScore() + 10);
        }

        etat.setImpactsDepuisAcceleration(etat.getImpactsDepuisAcceleration() + 1);
        if (
            etat.getImpactsDepuisAcceleration() >= 10
            && etat.getVitesseCourante() > EtatKowasuRenga.VITESSE_MIN
        ) {
            etat.setVitesseCourante(etat.getVitesseCourante() - 1);
            etat.setImpactsDepuisAcceleration(0);
        }
    }
}
