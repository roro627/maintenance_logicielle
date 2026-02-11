import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * Gere l etat de session du mode maintenance cache.
 */
public final class EtatModeMaintenance {
    /** Configuration lue depuis le fichier proprietes. */
    private final ConfigurationModeMaintenance configuration;

    /** Position courante dans la sequence secrete. */
    private int indexSequence;

    /** Etat de debloquage courant de la session. */
    private boolean debloque;

    /**
     * Construit l etat de session du mode maintenance.
     */
    public EtatModeMaintenance() {
        this.configuration = ConfigurationModeMaintenance.charger();
        this.indexSequence = 0;
        this.debloque = false;
    }

    /**
     * Indique si la fonctionnalite est active.
     *
     * @return true si active.
     */
    public boolean estActif() {
        return configuration.estActif();
    }

    /**
     * Indique si le mode est debloque pour la session courante.
     *
     * @return true si debloque.
     */
    public boolean estDebloque() {
        return debloque;
    }

    /**
     * Retourne le nom du jeu de maintenance.
     *
     * @return nom du jeu.
     */
    public String getNomJeuMaintenance() {
        return configuration.getNomJeu();
    }

    /**
     * Retourne le texte a afficher pour informer l operateur.
     *
     * @return message de statut du mode maintenance.
     */
    public String getMessageStatut() {
        if (!estActif()) {
            return "";
        }
        if (!debloque) {
            return "Mode maintenance verrouille";
        }
        return "Mode maintenance debloque - " + configuration.getBoutonOuverture() + " pour ouvrir";
    }

    /**
     * Traite la sequence secrete et debloque le mode si complete.
     *
     * @param clavier etat des controles borne.
     * @return true si le mode vient d etre debloque.
     */
    public boolean traiterSequenceSecrete(ClavierBorneArcade clavier) {
        if (!estActif() || debloque) {
            return false;
        }

        String entree = lireEntreeSequence(clavier);
        if (entree.isEmpty()) {
            return false;
        }

        String[] sequence = configuration.getSequenceSecrete();
        String attendu = sequence[indexSequence];
        if (entree.equals(attendu)) {
            indexSequence += 1;
            if (indexSequence >= sequence.length) {
                debloque = true;
                indexSequence = 0;
                return true;
            }
            return false;
        }

        if (entree.equals(sequence[0])) {
            indexSequence = 1;
            return false;
        }

        indexSequence = 0;
        return false;
    }

    /**
     * Indique si une commande d ouverture du mode maintenance est demandee.
     *
     * @param clavier etat des controles borne.
     * @return true si ouverture demandee.
     */
    public boolean ouvertureDemandee(ClavierBorneArcade clavier) {
        if (!estActif() || !debloque) {
            return false;
        }
        return boutonTape(clavier, configuration.getBoutonOuverture());
    }

    /**
     * Verifie si le jeu maintenance a demande un reverrouillage.
     */
    public void appliquerDemandeVerrouillageExterne() {
        if (!estActif()) {
            return;
        }

        Path cheminCommande = Paths.get(
            "projet",
            configuration.getNomJeu(),
            configuration.getFichierVerrouillage()
        );
        if (!Files.exists(cheminCommande)) {
            return;
        }

        try {
            Files.delete(cheminCommande);
        } catch (IOException exception) {
            // Ignore volontairement: le reverrouillage reste applique en memoire.
        }

        debloque = false;
        indexSequence = 0;
    }

    /**
     * Lit un evenement clavier utile a la sequence secrete.
     *
     * @param clavier etat des controles borne.
     * @return identifiant du bouton active, ou chaine vide.
     */
    private String lireEntreeSequence(ClavierBorneArcade clavier) {
        if (clavier.getBoutonJ1ATape()) {
            return "J1A";
        }
        if (clavier.getBoutonJ1BTape()) {
            return "J1B";
        }
        if (clavier.getBoutonJ1CTape()) {
            return "J1C";
        }
        if (clavier.getBoutonJ1XTape()) {
            return "J1X";
        }
        if (clavier.getBoutonJ1YTape()) {
            return "J1Y";
        }
        if (clavier.getBoutonJ1ZTape()) {
            return "J1Z";
        }
        if (clavier.getJoyJ1HautTape()) {
            return "J1HAUT";
        }
        if (clavier.getJoyJ1BasTape()) {
            return "J1BAS";
        }
        if (clavier.getJoyJ1GaucheTape()) {
            return "J1GAUCHE";
        }
        if (clavier.getJoyJ1DroiteTape()) {
            return "J1DROITE";
        }
        return "";
    }

    /**
     * Verifie si un bouton symbolique est tape.
     *
     * @param clavier etat des controles borne.
     * @param bouton identifiant du bouton a tester.
     * @return true si le bouton est detecte.
     */
    private boolean boutonTape(ClavierBorneArcade clavier, String bouton) {
        String boutonNormalise = bouton.toUpperCase();
        if ("J1A".equals(boutonNormalise)) {
            return clavier.getBoutonJ1ATape();
        }
        if ("J1B".equals(boutonNormalise)) {
            return clavier.getBoutonJ1BTape();
        }
        if ("J1C".equals(boutonNormalise)) {
            return clavier.getBoutonJ1CTape();
        }
        if ("J1X".equals(boutonNormalise)) {
            return clavier.getBoutonJ1XTape();
        }
        if ("J1Y".equals(boutonNormalise)) {
            return clavier.getBoutonJ1YTape();
        }
        if ("J1Z".equals(boutonNormalise)) {
            return clavier.getBoutonJ1ZTape();
        }
        return false;
    }
}
