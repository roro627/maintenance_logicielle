/**
 * Centralise la generation pure des ennemis d Initial Drift.
 */
public final class FabriqueEnnemiInitialDrift {
    /** Type jeep. */
    public static final int TYPE_JEEP = 1;

    /** Type police. */
    public static final int TYPE_POLICE = 2;

    /** Type tonneau. */
    public static final int TYPE_TONNEAU = 3;

    /** Liste des voies de circulation autorisees. */
    private static final int[] POSITIONS_X = {350, 451, 552, 653, 754, 855};

    /**
     * Construit une configuration pure a partir du score et de deux tirages.
     *
     * @param score score courant de la partie.
     * @param nombreEnnemis nombre d ennemis deja presents.
     * @param tirageType valeur dans l intervalle [0, 1[ pour choisir le type.
     * @param tiragePosition valeur dans l intervalle [0, 1[ pour choisir la voie.
     * @param hauteurFenetre hauteur de la fenetre de jeu.
     * @return configuration d ennemi complete.
     */
    public ConfigurationEnnemiInitialDrift creerConfiguration(
        int score,
        int nombreEnnemis,
        double tirageType,
        double tiragePosition,
        int hauteurFenetre
    ) {
        int type = resoudreType(score, tirageType);
        int abscisse = resoudrePosition(tiragePosition);
        int vitesse = resoudreVitesse(type, score);
        boolean creationAutorisee = !(type == TYPE_POLICE && nombreEnnemis >= 6);
        return new ConfigurationEnnemiInitialDrift(
            type,
            nommerType(type),
            cheminTexture(type),
            abscisse,
            hauteurFenetre,
            vitesse,
            creationAutorisee
        );
    }

    /**
     * Retourne le type d ennemi selon le score courant.
     *
     * @param score score courant.
     * @param tirageType tirage aleatoire normalise.
     * @return identifiant de type.
     */
    public int resoudreType(int score, double tirageType) {
        double tirageNormalise = normaliserTirage(tirageType);
        if (score < 5) {
            return TYPE_POLICE;
        }
        if (score < 15) {
            return (int) (tirageNormalise * 2) + 1;
        }
        return (int) (tirageNormalise * 3) + 1;
    }

    /**
     * Retourne une voie de circulation autorisee.
     *
     * @param tiragePosition tirage aleatoire normalise.
     * @return abscisse retenue.
     */
    public int resoudrePosition(double tiragePosition) {
        double tirageNormalise = normaliserTirage(tiragePosition);
        int index = (int) (tirageNormalise * POSITIONS_X.length);
        if (index >= POSITIONS_X.length) {
            index = POSITIONS_X.length - 1;
        }
        return POSITIONS_X[index];
    }

    /**
     * Calcule la vitesse d un type d ennemi.
     *
     * @param type type logique de l ennemi.
     * @param score score courant.
     * @return vitesse correspondante.
     */
    public int resoudreVitesse(int type, int score) {
        if (type == TYPE_JEEP) {
            return (int) (10 + score * 0.1);
        }
        if (type == TYPE_POLICE) {
            return (int) (15 + score * 0.2);
        }
        return (int) (18 + score * 0.3);
    }

    /**
     * Retourne le nom lisible d un type d ennemi.
     *
     * @param type type logique.
     * @return nom lisible.
     */
    public String nommerType(int type) {
        if (type == TYPE_JEEP) {
            return "jeep";
        }
        if (type == TYPE_POLICE) {
            return "police";
        }
        return "tonneau";
    }

    /**
     * Retourne le chemin texture associe au type.
     *
     * @param type type logique.
     * @return chemin texture.
     */
    public String cheminTexture(int type) {
        if (type == TYPE_JEEP) {
            return "img/jeep.png";
        }
        if (type == TYPE_POLICE) {
            return "img/police.png";
        }
        return "img/tonneau_ennemi.png";
    }

    /**
     * Borne un tirage a l intervalle [0, 0.999999].
     *
     * @param tirage tirage a normaliser.
     * @return tirage exploitable.
     */
    private double normaliserTirage(double tirage) {
        if (tirage < 0.0) {
            return 0.0;
        }
        if (tirage >= 1.0) {
            return 0.999999;
        }
        return tirage;
    }
}
