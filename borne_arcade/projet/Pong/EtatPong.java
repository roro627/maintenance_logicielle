/**
 * Transporte l etat pur d une manche de Pong.
 */
public final class EtatPong {
    /** Largeur logique de l aire de jeu. */
    public static final int LARGEUR = 1280;

    /** Hauteur logique de l aire de jeu. */
    public static final int HAUTEUR = 1024;

    /** Epaisseur des bordures. */
    public static final int EPAISSEUR_LIGNE = 10;

    /** Rayon de la balle. */
    public static final int RAYON_BALLE = 20;

    /** Vitesse de deplacement des raquettes. */
    public static final int VITESSE_RAQUETTE = 6;

    /** Vitesse initiale de la balle. */
    public static final int VITESSE_BALLE_INITIALE = 6;

    /** Hauteur initiale d une raquette. */
    public static final int TAILLE_RAQUETTE_INITIALE = HAUTEUR / 5;

    /** Position X de la balle. */
    private int positionXBalle;

    /** Position Y de la balle. */
    private int positionYBalle;

    /** Direction horizontale de la balle. */
    private int dx;

    /** Direction verticale de la balle. */
    private int dy;

    /** Score joueur gauche. */
    private int scoreGauche;

    /** Score joueur droit. */
    private int scoreDroit;

    /** Hauteur courante des raquettes. */
    private int tailleRaquette;

    /** Position Y de la raquette gauche. */
    private int positionYRaquetteGauche;

    /** Position Y de la raquette droite. */
    private int positionYRaquetteDroite;

    /** Nombre de rebonds a consommer. */
    private int nbRebond;

    /** Vitesse courante de la balle. */
    private int vitesseBalle;

    /** Indique si la manche est demarree. */
    private boolean demarrer;

    /** Indique si un retour menu est demande. */
    private boolean retourMenu;

    /**
     * Construit un etat pret a etre initialise.
     */
    public EtatPong() {
        this.scoreGauche = 0;
        this.scoreDroit = 0;
        this.tailleRaquette = TAILLE_RAQUETTE_INITIALE;
        this.positionXBalle = LARGEUR / 2;
        this.positionYBalle = HAUTEUR / 2;
        this.positionYRaquetteGauche = HAUTEUR / 2;
        this.positionYRaquetteDroite = HAUTEUR / 2;
        this.dx = 0;
        this.dy = 0;
        this.nbRebond = 0;
        this.vitesseBalle = VITESSE_BALLE_INITIALE;
        this.demarrer = false;
        this.retourMenu = false;
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
    public int getDx() {
        return dx;
    }

    /**
     * Met a jour la direction horizontale.
     *
     * @param direction direction X.
     */
    public void setDx(int direction) {
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
     * Retourne le score du joueur gauche.
     *
     * @return score gauche.
     */
    public int getScoreGauche() {
        return scoreGauche;
    }

    /**
     * Met a jour le score du joueur gauche.
     *
     * @param score score a appliquer.
     */
    public void setScoreGauche(int score) {
        this.scoreGauche = score;
    }

    /**
     * Retourne le score du joueur droit.
     *
     * @return score droit.
     */
    public int getScoreDroit() {
        return scoreDroit;
    }

    /**
     * Met a jour le score du joueur droit.
     *
     * @param score score a appliquer.
     */
    public void setScoreDroit(int score) {
        this.scoreDroit = score;
    }

    /**
     * Retourne la taille courante des raquettes.
     *
     * @return hauteur de raquette.
     */
    public int getTailleRaquette() {
        return tailleRaquette;
    }

    /**
     * Met a jour la taille courante des raquettes.
     *
     * @param taille nouvelle hauteur.
     */
    public void setTailleRaquette(int taille) {
        this.tailleRaquette = taille;
    }

    /**
     * Retourne la position Y de la raquette gauche.
     *
     * @return position Y raquette gauche.
     */
    public int getPositionYRaquetteGauche() {
        return positionYRaquetteGauche;
    }

    /**
     * Met a jour la position Y de la raquette gauche.
     *
     * @param position position Y.
     */
    public void setPositionYRaquetteGauche(int position) {
        this.positionYRaquetteGauche = position;
    }

    /**
     * Retourne la position Y de la raquette droite.
     *
     * @return position Y raquette droite.
     */
    public int getPositionYRaquetteDroite() {
        return positionYRaquetteDroite;
    }

    /**
     * Met a jour la position Y de la raquette droite.
     *
     * @param position position Y.
     */
    public void setPositionYRaquetteDroite(int position) {
        this.positionYRaquetteDroite = position;
    }

    /**
     * Retourne le compteur de rebonds.
     *
     * @return nombre de rebonds.
     */
    public int getNbRebond() {
        return nbRebond;
    }

    /**
     * Met a jour le compteur de rebonds.
     *
     * @param nombre compteur courant.
     */
    public void setNbRebond(int nombre) {
        this.nbRebond = nombre;
    }

    /**
     * Retourne la vitesse courante de la balle.
     *
     * @return vitesse balle.
     */
    public int getVitesseBalle() {
        return vitesseBalle;
    }

    /**
     * Met a jour la vitesse de la balle.
     *
     * @param vitesse nouvelle vitesse.
     */
    public void setVitesseBalle(int vitesse) {
        this.vitesseBalle = vitesse;
    }

    /**
     * Indique si la manche a demarre.
     *
     * @return true si la manche est active.
     */
    public boolean isDemarrer() {
        return demarrer;
    }

    /**
     * Met a jour l etat de demarrage.
     *
     * @param actif true si la manche est active.
     */
    public void setDemarrer(boolean actif) {
        this.demarrer = actif;
    }

    /**
     * Indique si un retour menu est demande.
     *
     * @return true si la partie est terminee.
     */
    public boolean isRetourMenu() {
        return retourMenu;
    }

    /**
     * Met a jour l etat de retour menu.
     *
     * @param retour true si le menu doit reprendre la main.
     */
    public void setRetourMenu(boolean retour) {
        this.retourMenu = retour;
    }
}
