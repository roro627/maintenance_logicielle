/**
 * Decrit un ennemi a instancier pour Initial Drift.
 */
public final class ConfigurationEnnemiInitialDrift {
    /** Identifiant logique du type d ennemi. */
    private final int type;

    /** Nom lisible du type d ennemi. */
    private final String nomType;

    /** Texture a utiliser. */
    private final String cheminTexture;

    /** Abscisse de generation. */
    private final int abscisse;

    /** Ordonnee de generation. */
    private final int ordonnee;

    /** Vitesse a appliquer. */
    private final int vitesse;

    /** Indique si la creation est autorisee. */
    private final boolean creationAutorisee;

    /**
     * Construit une configuration immutable.
     *
     * @param typeEnnemi identifiant du type.
     * @param nomTypeEnnemi nom lisible.
     * @param cheminTextureEnnemi texture a utiliser.
     * @param positionX abscisse de depart.
     * @param positionY ordonnee de depart.
     * @param vitesseEnnemi vitesse de l ennemi.
     * @param autorisee true si l ennemi doit etre cree.
     */
    public ConfigurationEnnemiInitialDrift(
        int typeEnnemi,
        String nomTypeEnnemi,
        String cheminTextureEnnemi,
        int positionX,
        int positionY,
        int vitesseEnnemi,
        boolean autorisee
    ) {
        this.type = typeEnnemi;
        this.nomType = nomTypeEnnemi;
        this.cheminTexture = cheminTextureEnnemi;
        this.abscisse = positionX;
        this.ordonnee = positionY;
        this.vitesse = vitesseEnnemi;
        this.creationAutorisee = autorisee;
    }

    /**
     * Retourne l identifiant du type.
     *
     * @return identifiant de type.
     */
    public int getType() {
        return type;
    }

    /**
     * Retourne le nom lisible du type.
     *
     * @return nom du type.
     */
    public String getNomType() {
        return nomType;
    }

    /**
     * Retourne la texture a instancier.
     *
     * @return chemin texture.
     */
    public String getCheminTexture() {
        return cheminTexture;
    }

    /**
     * Retourne l abscisse de depart.
     *
     * @return position X.
     */
    public int getAbscisse() {
        return abscisse;
    }

    /**
     * Retourne l ordonnee de depart.
     *
     * @return position Y.
     */
    public int getOrdonnee() {
        return ordonnee;
    }

    /**
     * Retourne la vitesse a appliquer.
     *
     * @return vitesse de l ennemi.
     */
    public int getVitesse() {
        return vitesse;
    }

    /**
     * Indique si l ennemi doit etre cree.
     *
     * @return true si la creation est autorisee.
     */
    public boolean isCreationAutorisee() {
        return creationAutorisee;
    }
}
