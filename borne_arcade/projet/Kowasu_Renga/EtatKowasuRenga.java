/**
 * Transporte l etat pur de Kowasu Renga.
 */
public final class EtatKowasuRenga {
    /** Largeur logique du jeu. */
    public static final int LARGEUR = 1280;

    /** Hauteur logique du jeu. */
    public static final int HAUTEUR = 1024;

    /** Delai minimal entre deux rafraichissements. */
    public static final int VITESSE_MIN = 2;

    /** Delai initial de reference. */
    public static final int VITESSE_INITIALE = 5;

    /** Largeur de la raquette. */
    public static final int LARGEUR_RAQUETTE = 80;

    /** Position X de la balle. */
    private int positionXBalle;

    /** Position Y de la balle. */
    private int positionYBalle;

    /** Direction horizontale de la balle. */
    private double dx;

    /** Direction verticale de la balle. */
    private int dy;

    /** Debut de la raquette. */
    private int positionXRaquette;

    /** Fin de la raquette. */
    private int positionXRaquetteFin;

    /** Nombre de vies restantes. */
    private int nbVies;

    /** Score courant. */
    private int score;

    /** Delai de jeu courant. */
    private int vitesseCourante;

    /** Nombre d impacts depuis la derniere acceleration. */
    private int impactsDepuisAcceleration;

    /** Jeu de briques courant. */
    private final BriqueKowasuRenga[] briques;

    /**
     * Construit un etat initial.
     */
    public EtatKowasuRenga() {
        this.positionXBalle = LARGEUR / 2;
        this.positionYBalle = 80;
        this.dx = 0.0;
        this.dy = 0;
        this.positionXRaquette = (LARGEUR / 2) - 40;
        this.positionXRaquetteFin = (LARGEUR / 2) + 40;
        this.nbVies = 3;
        this.score = 0;
        this.vitesseCourante = VITESSE_INITIALE;
        this.impactsDepuisAcceleration = 0;
        this.briques = new BriqueKowasuRenga[75];
    }

    /**
     * Retourne la position X de la balle.
     *
     * @return position X.
     */
    public int getPositionXBalle() {
        return positionXBalle;
    }

    /**
     * Met a jour la position X de la balle.
     *
     * @param position position X.
     */
    public void setPositionXBalle(int position) {
        this.positionXBalle = position;
    }

    /**
     * Retourne la position Y de la balle.
     *
     * @return position Y.
     */
    public int getPositionYBalle() {
        return positionYBalle;
    }

    /**
     * Met a jour la position Y de la balle.
     *
     * @param position position Y.
     */
    public void setPositionYBalle(int position) {
        this.positionYBalle = position;
    }

    /**
     * Retourne la direction horizontale.
     *
     * @return direction X.
     */
    public double getDx() {
        return dx;
    }

    /**
     * Met a jour la direction horizontale.
     *
     * @param direction direction X.
     */
    public void setDx(double direction) {
        this.dx = direction;
    }

    /**
     * Retourne la direction verticale.
     *
     * @return direction Y.
     */
    public int getDy() {
        return dy;
    }

    /**
     * Met a jour la direction verticale.
     *
     * @param direction direction Y.
     */
    public void setDy(int direction) {
        this.dy = direction;
    }

    /**
     * Retourne le debut de la raquette.
     *
     * @return abscisse de debut.
     */
    public int getPositionXRaquette() {
        return positionXRaquette;
    }

    /**
     * Met a jour le debut de la raquette.
     *
     * @param position abscisse de debut.
     */
    public void setPositionXRaquette(int position) {
        this.positionXRaquette = position;
    }

    /**
     * Retourne la fin de la raquette.
     *
     * @return abscisse de fin.
     */
    public int getPositionXRaquetteFin() {
        return positionXRaquetteFin;
    }

    /**
     * Met a jour la fin de la raquette.
     *
     * @param position abscisse de fin.
     */
    public void setPositionXRaquetteFin(int position) {
        this.positionXRaquetteFin = position;
    }

    /**
     * Retourne le nombre de vies restantes.
     *
     * @return nombre de vies.
     */
    public int getNbVies() {
        return nbVies;
    }

    /**
     * Met a jour le nombre de vies restantes.
     *
     * @param vies nouveau nombre de vies.
     */
    public void setNbVies(int vies) {
        this.nbVies = vies;
    }

    /**
     * Retourne le score courant.
     *
     * @return score.
     */
    public int getScore() {
        return score;
    }

    /**
     * Met a jour le score courant.
     *
     * @param scoreCourant nouveau score.
     */
    public void setScore(int scoreCourant) {
        this.score = scoreCourant;
    }

    /**
     * Retourne le delai de jeu courant.
     *
     * @return delai courant.
     */
    public int getVitesseCourante() {
        return vitesseCourante;
    }

    /**
     * Met a jour le delai courant.
     *
     * @param vitesse delai courant.
     */
    public void setVitesseCourante(int vitesse) {
        this.vitesseCourante = vitesse;
    }

    /**
     * Retourne le compteur d impacts depuis acceleration.
     *
     * @return nombre d impacts.
     */
    public int getImpactsDepuisAcceleration() {
        return impactsDepuisAcceleration;
    }

    /**
     * Met a jour le compteur d impacts depuis acceleration.
     *
     * @param impacts nouveau compteur.
     */
    public void setImpactsDepuisAcceleration(int impacts) {
        this.impactsDepuisAcceleration = impacts;
    }

    /**
     * Retourne le tableau de briques.
     *
     * @return tableau de briques.
     */
    public BriqueKowasuRenga[] getBriques() {
        return briques;
    }
}
