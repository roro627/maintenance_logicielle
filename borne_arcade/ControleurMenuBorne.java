import java.util.List;

/**
 * Porte la logique pure du menu de la borne.
 */
public final class ControleurMenuBorne {
    /** Catalogue logique du menu. */
    private final List<JeuCatalogue> jeux;

    /** Etat courant du menu. */
    private final EtatMenuBorne etat;

    /** Gestionnaire du mode maintenance. */
    private final EtatModeMaintenance etatModeMaintenance;

    /** Lanceur de jeu injectable. */
    private final LanceurJeuMenu lanceurJeu;

    /**
     * Construit un controleur de menu testable.
     *
     * @param jeuxCatalogue catalogue des jeux.
     * @param etatMaintenance etat du mode maintenance.
     * @param lanceur lanceur de jeu injectable.
     */
    public ControleurMenuBorne(
        List<JeuCatalogue> jeuxCatalogue,
        EtatModeMaintenance etatMaintenance,
        LanceurJeuMenu lanceur
    ) {
        if (jeuxCatalogue == null || jeuxCatalogue.isEmpty()) {
            throw new IllegalArgumentException("Le catalogue de jeux ne doit pas etre vide.");
        }
        if (etatMaintenance == null) {
            throw new IllegalArgumentException("L etat du mode maintenance est obligatoire.");
        }
        if (lanceur == null) {
            throw new IllegalArgumentException("Le lanceur de jeu est obligatoire.");
        }

        this.jeux = jeuxCatalogue;
        this.etatModeMaintenance = etatMaintenance;
        this.lanceurJeu = lanceur;
        this.etat = new EtatMenuBorne(0, jeuxCatalogue.get(0));
    }

    /**
     * Retourne l etat courant du menu.
     *
     * @return etat courant.
     */
    public EtatMenuBorne getEtat() {
        return etat;
    }

    /**
     * Remonte la selection comme dans le menu historique.
     */
    public void deplacerHaut() {
        if (etat.getIndexSelection() == 0) {
            appliquerSelection(jeux.size() - 1);
            return;
        }
        appliquerSelection(etat.getIndexSelection() - 1);
    }

    /**
     * Descend la selection comme dans le menu historique.
     */
    public void deplacerBas() {
        if (etat.getIndexSelection() == jeux.size() - 1) {
            appliquerSelection(0);
            return;
        }
        appliquerSelection(etat.getIndexSelection() + 1);
    }

    /**
     * Ouvre la confirmation de fermeture.
     */
    public void demanderFermeture() {
        etat.setConfirmationFermetureOuverte(true);
    }

    /**
     * Ferme la confirmation de fermeture sans quitter.
     */
    public void annulerFermeture() {
        etat.setConfirmationFermetureOuverte(false);
        etat.setQuitterDemande(false);
    }

    /**
     * Valide la fermeture du menu.
     */
    public void confirmerFermeture() {
        etat.setConfirmationFermetureOuverte(false);
        etat.setQuitterDemande(true);
    }

    /**
     * Tente de selectionner explicitement un jeu par son nom.
     *
     * @param nomJeu nom logique recherche.
     * @return true si le jeu a ete trouve.
     */
    public boolean selectionnerJeuParNom(String nomJeu) {
        for (int index = 0; index < jeux.size(); index++) {
            if (jeux.get(index).getNom().equals(nomJeu)) {
                appliquerSelection(index);
                return true;
            }
        }
        return false;
    }

    /**
     * Tente de lancer le jeu selectionne.
     *
     * @return true si le jeu a ete lance, false si le lancement est refuse.
     * @throws Exception si le lancement reel echoue.
     */
    public boolean lancerJeuSelectionne() throws Exception {
        JeuCatalogue jeu = etat.getJeuSelectionne();
        if (jeu == null) {
            return false;
        }
        if (estJeuMaintenanceVerrouille(jeu)) {
            return false;
        }
        lanceurJeu.lancerJeu(jeu);
        return true;
    }

    /**
     * Indique si le jeu courant correspond au mode maintenance verrouille.
     *
     * @return true si le lancement doit etre refuse.
     */
    public boolean estSelectionMaintenanceVerrouillee() {
        return estJeuMaintenanceVerrouille(etat.getJeuSelectionne());
    }

    /**
     * Met a jour la selection logique et le jeu courant.
     *
     * @param nouvelIndex nouvel index.
     */
    private void appliquerSelection(int nouvelIndex) {
        etat.setIndexSelection(nouvelIndex);
        etat.setJeuSelectionne(jeux.get(nouvelIndex));
    }

    /**
     * Indique si un jeu correspond au mode maintenance verrouille.
     *
     * @param jeu jeu a verifier.
     * @return true si le jeu est le mode maintenance encore verrouille.
     */
    private boolean estJeuMaintenanceVerrouille(JeuCatalogue jeu) {
        if (jeu == null || !etatModeMaintenance.estActif()) {
            return false;
        }
        return jeu.getNom().equals(etatModeMaintenance.getNomJeuMaintenance()) && !etatModeMaintenance.estDebloque();
    }
}
