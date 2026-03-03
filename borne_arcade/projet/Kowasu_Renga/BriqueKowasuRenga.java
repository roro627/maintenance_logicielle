/**
 * Represente une brique logique de Kowasu Renga.
 */
public final class BriqueKowasuRenga {
    /** Indique si la brique est encore active. */
    private boolean active;

    /** Nombre de coups restants. */
    private int resistance;

    /** Index couleur logique. */
    private int indexCouleur;

    /**
     * Construit une brique.
     *
     * @param coupsRestants resistance initiale.
     * @param couleurInitiale index de couleur initial.
     */
    public BriqueKowasuRenga(int coupsRestants, int couleurInitiale) {
        this.active = true;
        this.resistance = coupsRestants;
        this.indexCouleur = couleurInitiale;
    }

    /**
     * Indique si la brique est encore active.
     *
     * @return true si la brique existe encore.
     */
    public boolean isActive() {
        return active;
    }

    /**
     * Met a jour l etat actif.
     *
     * @param activeCourante nouvel etat actif.
     */
    public void setActive(boolean activeCourante) {
        this.active = activeCourante;
    }

    /**
     * Retourne la resistance restante.
     *
     * @return coups restants.
     */
    public int getResistance() {
        return resistance;
    }

    /**
     * Met a jour la resistance restante.
     *
     * @param coupsRestants nouvelle resistance.
     */
    public void setResistance(int coupsRestants) {
        this.resistance = coupsRestants;
    }

    /**
     * Retourne l index de couleur logique.
     *
     * @return index de couleur.
     */
    public int getIndexCouleur() {
        return indexCouleur;
    }

    /**
     * Met a jour l index de couleur logique.
     *
     * @param index nouvel index.
     */
    public void setIndexCouleur(int index) {
        this.indexCouleur = index;
    }
}
