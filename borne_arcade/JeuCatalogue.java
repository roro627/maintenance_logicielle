import java.util.Arrays;
import java.util.Collections;
import java.util.List;

/**
 * Decrit un jeu expose par le catalogue de la borne.
 */
public final class JeuCatalogue {
    /** Nom logique du jeu. */
    private final String nom;

    /** Chemin relatif du dossier du jeu depuis borne_arcade/. */
    private final String cheminJeu;

    /** Chemin relatif du lanceur depuis borne_arcade/. */
    private final String cheminLanceur;

    /** Lignes de description visibles dans le menu. */
    private final List<String> description;

    /** Mapping joystick + boutons du jeu. */
    private final String[] boutons;

    /**
     * Construit une entree de catalogue immutable.
     *
     * @param nomJeu nom logique du jeu.
     * @param cheminDossier chemin relatif du dossier.
     * @param cheminScript chemin relatif du lanceur.
     * @param lignesDescription lignes de description.
     * @param mappingBoutons mapping joystick + boutons.
     */
    public JeuCatalogue(
        String nomJeu,
        String cheminDossier,
        String cheminScript,
        List<String> lignesDescription,
        String[] mappingBoutons
    ) {
        this.nom = nomJeu;
        this.cheminJeu = cheminDossier;
        this.cheminLanceur = cheminScript;
        this.description = Collections.unmodifiableList(lignesDescription);
        this.boutons = Arrays.copyOf(mappingBoutons, mappingBoutons.length);
    }

    /**
     * Retourne le nom logique du jeu.
     *
     * @return nom du jeu.
     */
    public String getNom() {
        return nom;
    }

    /**
     * Retourne le chemin relatif du dossier du jeu.
     *
     * @return chemin relatif depuis borne_arcade/.
     */
    public String getCheminJeu() {
        return cheminJeu;
    }

    /**
     * Retourne le chemin relatif du lanceur du jeu.
     *
     * @return chemin relatif depuis borne_arcade/.
     */
    public String getCheminLanceur() {
        return cheminLanceur;
    }

    /**
     * Retourne la description du jeu.
     *
     * @return liste immutable de lignes de description.
     */
    public List<String> getDescription() {
        return description;
    }

    /**
     * Retourne le mapping joystick + boutons.
     *
     * @return copie defensive du mapping.
     */
    public String[] getBoutons() {
        return Arrays.copyOf(boutons, boutons.length);
    }
}
