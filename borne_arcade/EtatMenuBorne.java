/**
 * Transporte l etat logique courant du menu de la borne.
 */
public final class EtatMenuBorne {
    /** Index du jeu actuellement selectionne. */
    private int indexSelection;

    /** Indique si la confirmation de fermeture est ouverte. */
    private boolean confirmationFermetureOuverte;

    /** Indique si le menu a demande sa fermeture. */
    private boolean quitterDemande;

    /** Jeu actuellement selectionne. */
    private JeuCatalogue jeuSelectionne;

    /**
     * Construit un etat de menu complet.
     *
     * @param indexInitial index de selection initial.
     * @param jeuInitial jeu initialement selectionne.
     */
    public EtatMenuBorne(int indexInitial, JeuCatalogue jeuInitial) {
        this.indexSelection = indexInitial;
        this.confirmationFermetureOuverte = false;
        this.quitterDemande = false;
        this.jeuSelectionne = jeuInitial;
    }

    /**
     * Retourne l index du jeu selectionne.
     *
     * @return index courant.
     */
    public int getIndexSelection() {
        return indexSelection;
    }

    /**
     * Met a jour l index du jeu selectionne.
     *
     * @param nouvelIndex nouvel index.
     */
    public void setIndexSelection(int nouvelIndex) {
        this.indexSelection = nouvelIndex;
    }

    /**
     * Indique si la confirmation de fermeture est visible.
     *
     * @return true si la confirmation est ouverte.
     */
    public boolean isConfirmationFermetureOuverte() {
        return confirmationFermetureOuverte;
    }

    /**
     * Met a jour l etat de la confirmation de fermeture.
     *
     * @param ouverte true si la confirmation doit etre visible.
     */
    public void setConfirmationFermetureOuverte(boolean ouverte) {
        this.confirmationFermetureOuverte = ouverte;
    }

    /**
     * Indique si le menu a demande sa fermeture.
     *
     * @return true si une sortie a ete validee.
     */
    public boolean isQuitterDemande() {
        return quitterDemande;
    }

    /**
     * Met a jour l etat de demande de fermeture.
     *
     * @param quitter true si la fermeture est demandee.
     */
    public void setQuitterDemande(boolean quitter) {
        this.quitterDemande = quitter;
    }

    /**
     * Retourne le jeu actuellement selectionne.
     *
     * @return jeu courant.
     */
    public JeuCatalogue getJeuSelectionne() {
        return jeuSelectionne;
    }

    /**
     * Met a jour le jeu selectionne.
     *
     * @param jeuCourant jeu courant.
     */
    public void setJeuSelectionne(JeuCatalogue jeuCourant) {
        this.jeuSelectionne = jeuCourant;
    }
}
