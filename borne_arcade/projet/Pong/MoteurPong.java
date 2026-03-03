/**
 * Centralise les regles pures d une manche de Pong.
 */
public final class MoteurPong {

    /**
     * Reinitialise une manche avec une position verticale deterministe.
     *
     * @param etat etat a reinitialiser.
     * @param positionYBalleInitiale position verticale de la balle.
     */
    public void reinitialiserManche(EtatPong etat, int positionYBalleInitiale) {
        etat.setDemarrer(false);
        etat.setPositionXBalle(EtatPong.LARGEUR / 2);
        etat.setPositionYBalle(positionYBalleInitiale);
        etat.setPositionYRaquetteGauche(EtatPong.HAUTEUR / 2);
        etat.setPositionYRaquetteDroite(EtatPong.HAUTEUR / 2);
        etat.setDx(0);
        etat.setDy(0);
        etat.setNbRebond(0);
        etat.setVitesseBalle(EtatPong.VITESSE_BALLE_INITIALE);
        if (etat.getScoreGauche() >= 9 || etat.getScoreDroit() >= 9) {
            etat.setRetourMenu(true);
        }
    }

    /**
     * Demarre la balle si le bouton de depart est actif.
     *
     * @param etat etat a mettre a jour.
     * @param boutonDepart true si le bouton de depart est presse.
     */
    public void demarrerSiDemande(EtatPong etat, boolean boutonDepart) {
        if (!etat.isDemarrer() && boutonDepart && etat.getScoreGauche() < 9 && etat.getScoreDroit() < 9) {
            etat.setDemarrer(true);
            etat.setDx(1);
            etat.setDy(1);
        }
    }

    /**
     * Deplace les raquettes sans sortir des bordures.
     *
     * @param etat etat courant.
     * @param j1Haut entree joueur 1 haut.
     * @param j1Bas entree joueur 1 bas.
     * @param j2Haut entree joueur 2 haut.
     * @param j2Bas entree joueur 2 bas.
     */
    public void deplacerRaquettes(EtatPong etat, boolean j1Haut, boolean j1Bas, boolean j2Haut, boolean j2Bas) {
        if (j1Bas) {
            etat.setPositionYRaquetteGauche(
                Math.max(
                    EtatPong.EPAISSEUR_LIGNE + etat.getTailleRaquette() / 2,
                    etat.getPositionYRaquetteGauche() - EtatPong.VITESSE_RAQUETTE
                )
            );
        }
        if (j1Haut) {
            etat.setPositionYRaquetteGauche(
                Math.min(
                    EtatPong.HAUTEUR - EtatPong.EPAISSEUR_LIGNE - etat.getTailleRaquette() / 2,
                    etat.getPositionYRaquetteGauche() + EtatPong.VITESSE_RAQUETTE
                )
            );
        }
        if (j2Bas) {
            etat.setPositionYRaquetteDroite(
                Math.max(
                    EtatPong.EPAISSEUR_LIGNE + etat.getTailleRaquette() / 2,
                    etat.getPositionYRaquetteDroite() - EtatPong.VITESSE_RAQUETTE
                )
            );
        }
        if (j2Haut) {
            etat.setPositionYRaquetteDroite(
                Math.min(
                    EtatPong.HAUTEUR - EtatPong.EPAISSEUR_LIGNE - etat.getTailleRaquette() / 2,
                    etat.getPositionYRaquetteDroite() + EtatPong.VITESSE_RAQUETTE
                )
            );
        }
    }

    /**
     * Applique le rebond sur bordure haute/basse.
     *
     * @param etat etat courant.
     */
    public void appliquerRebondBordures(EtatPong etat) {
        if (etat.getPositionYBalle() - EtatPong.RAYON_BALLE <= EtatPong.EPAISSEUR_LIGNE) {
            etat.setDy(1);
        }
        if (etat.getPositionYBalle() + EtatPong.RAYON_BALLE >= EtatPong.HAUTEUR - EtatPong.EPAISSEUR_LIGNE) {
            etat.setDy(-1);
        }
    }

    /**
     * Applique la reduction de raquette au prochain rebond consomme.
     *
     * @param etat etat courant.
     */
    public void consommerReductionRaquette(EtatPong etat) {
        if (etat.getNbRebond() == 1) {
            etat.setTailleRaquette(etat.getTailleRaquette() - (etat.getTailleRaquette() / 10));
            etat.setNbRebond(0);
        }
    }

    /**
     * Signale un rebond sur raquette.
     *
     * @param etat etat courant.
     */
    public void enregistrerRebondRaquette(EtatPong etat) {
        etat.setDx(-etat.getDx());
        etat.setNbRebond(etat.getNbRebond() + 1);
    }

    /**
     * Gere les points et la reinitialisation de manche.
     *
     * @param etat etat courant.
     * @param positionYBalleInitiale position verticale de reinitialisation.
     */
    public void gererPointsEtReinitialisation(EtatPong etat, int positionYBalleInitiale) {
        if (etat.getPositionXBalle() - EtatPong.RAYON_BALLE <= EtatPong.EPAISSEUR_LIGNE) {
            etat.setScoreDroit(etat.getScoreDroit() + 1);
            etat.setTailleRaquette(EtatPong.TAILLE_RAQUETTE_INITIALE);
            reinitialiserManche(etat, positionYBalleInitiale);
        } else if (etat.getPositionXBalle() + EtatPong.RAYON_BALLE >= EtatPong.LARGEUR - EtatPong.EPAISSEUR_LIGNE) {
            etat.setScoreGauche(etat.getScoreGauche() + 1);
            etat.setTailleRaquette(EtatPong.TAILLE_RAQUETTE_INITIALE);
            reinitialiserManche(etat, positionYBalleInitiale);
        }
    }
}
