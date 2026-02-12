import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * Gere l etat de session du mode maintenance cache.
 */
public final class EtatModeMaintenance {
    /** Ordre de lecture des entrees supportees. */
    private static final String[] ORDRE_ENTREES = {
        "J1A",
        "J1B",
        "J1C",
        "J1X",
        "J1Y",
        "J1Z",
        "J1HAUT",
        "J1BAS",
        "J1GAUCHE",
        "J1DROITE"
    };

    /** Configuration lue depuis le fichier proprietes. */
    private final ConfigurationModeMaintenance configuration;

    /** Position courante dans la sequence secrete. */
    private int indexSequence;

    /** Etat de debloquage courant de la session. */
    private boolean debloque;

    /** Etats precedents des touches pour detecter les fronts montants. */
    private boolean precedentJ1A;
    private boolean precedentJ1B;
    private boolean precedentJ1C;
    private boolean precedentJ1X;
    private boolean precedentJ1Y;
    private boolean precedentJ1Z;
    private boolean precedentJ1Haut;
    private boolean precedentJ1Bas;
    private boolean precedentJ1Gauche;
    private boolean precedentJ1Droite;

    /**
     * Construit l etat de session du mode maintenance.
     */
    public EtatModeMaintenance() {
        this.configuration = ConfigurationModeMaintenance.charger();
        this.indexSequence = 0;
        this.debloque = false;
        reinitialiserMemoireTouches();
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
        return boutonFrontMontant(clavier, configuration.getBoutonOuverture());
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
        reinitialiserMemoireTouches();
    }

    /**
     * Lit un evenement clavier utile a la sequence secrete.
     *
     * @param clavier etat des controles borne.
     * @return identifiant du bouton active, ou chaine vide.
     */
    private String lireEntreeSequence(ClavierBorneArcade clavier) {
        for (String entree : ORDRE_ENTREES) {
            if (boutonFrontMontant(clavier, entree)) {
                return entree;
            }
        }
        return "";
    }

    /**
     * Verifie si un bouton symbolique est actuellement enfonce.
     *
     * @param clavier etat des controles borne.
     * @param bouton identifiant du bouton a tester.
     * @return true si le bouton est enfonce.
     */
    private boolean boutonEnfonce(ClavierBorneArcade clavier, String bouton) {
        String boutonNormalise = bouton.toUpperCase();
        if ("J1A".equals(boutonNormalise)) {
            return clavier.getBoutonJ1AEnfoncee();
        }
        if ("J1B".equals(boutonNormalise)) {
            return clavier.getBoutonJ1BEnfoncee();
        }
        if ("J1C".equals(boutonNormalise)) {
            return clavier.getBoutonJ1CEnfoncee();
        }
        if ("J1X".equals(boutonNormalise)) {
            return clavier.getBoutonJ1XEnfoncee();
        }
        if ("J1Y".equals(boutonNormalise)) {
            return clavier.getBoutonJ1YEnfoncee();
        }
        if ("J1Z".equals(boutonNormalise)) {
            return clavier.getBoutonJ1ZEnfoncee();
        }
        if ("J1HAUT".equals(boutonNormalise)) {
            return clavier.getJoyJ1HautEnfoncee();
        }
        if ("J1BAS".equals(boutonNormalise)) {
            return clavier.getJoyJ1BasEnfoncee();
        }
        if ("J1GAUCHE".equals(boutonNormalise)) {
            return clavier.getJoyJ1GaucheEnfoncee();
        }
        if ("J1DROITE".equals(boutonNormalise)) {
            return clavier.getJoyJ1DroiteEnfoncee();
        }
        return false;
    }

    /**
     * Detecte un front montant sur un bouton symbolique.
     *
     * @param clavier etat des controles borne.
     * @param bouton identifiant du bouton a tester.
     * @return true si le bouton vient juste d etre presse.
     */
    private boolean boutonFrontMontant(ClavierBorneArcade clavier, String bouton) {
        String boutonNormalise = bouton.toUpperCase();
        boolean etatActuel = boutonEnfonce(clavier, boutonNormalise);
        boolean etatPrecedent = lireEtatPrecedent(boutonNormalise);
        ecrireEtatPrecedent(boutonNormalise, etatActuel);
        return etatActuel && !etatPrecedent;
    }

    /**
     * Lit l etat precedent memorise pour une touche symbolique.
     *
     * @param bouton identifiant de la touche.
     * @return true si la touche etait enfoncee au cycle precedent.
     */
    private boolean lireEtatPrecedent(String bouton) {
        if ("J1A".equals(bouton)) {
            return precedentJ1A;
        }
        if ("J1B".equals(bouton)) {
            return precedentJ1B;
        }
        if ("J1C".equals(bouton)) {
            return precedentJ1C;
        }
        if ("J1X".equals(bouton)) {
            return precedentJ1X;
        }
        if ("J1Y".equals(bouton)) {
            return precedentJ1Y;
        }
        if ("J1Z".equals(bouton)) {
            return precedentJ1Z;
        }
        if ("J1HAUT".equals(bouton)) {
            return precedentJ1Haut;
        }
        if ("J1BAS".equals(bouton)) {
            return precedentJ1Bas;
        }
        if ("J1GAUCHE".equals(bouton)) {
            return precedentJ1Gauche;
        }
        if ("J1DROITE".equals(bouton)) {
            return precedentJ1Droite;
        }
        return false;
    }

    /**
     * Memorise l etat courant d une touche symbolique.
     *
     * @param bouton identifiant de la touche.
     * @param etat etat courant de la touche.
     */
    private void ecrireEtatPrecedent(String bouton, boolean etat) {
        if ("J1A".equals(bouton)) {
            precedentJ1A = etat;
            return;
        }
        if ("J1B".equals(bouton)) {
            precedentJ1B = etat;
            return;
        }
        if ("J1C".equals(bouton)) {
            precedentJ1C = etat;
            return;
        }
        if ("J1X".equals(bouton)) {
            precedentJ1X = etat;
            return;
        }
        if ("J1Y".equals(bouton)) {
            precedentJ1Y = etat;
            return;
        }
        if ("J1Z".equals(bouton)) {
            precedentJ1Z = etat;
            return;
        }
        if ("J1HAUT".equals(bouton)) {
            precedentJ1Haut = etat;
            return;
        }
        if ("J1BAS".equals(bouton)) {
            precedentJ1Bas = etat;
            return;
        }
        if ("J1GAUCHE".equals(bouton)) {
            precedentJ1Gauche = etat;
            return;
        }
        if ("J1DROITE".equals(bouton)) {
            precedentJ1Droite = etat;
        }
    }

    /**
     * Reinitialise les etats precedents des touches surveillees.
     */
    private void reinitialiserMemoireTouches() {
        precedentJ1A = false;
        precedentJ1B = false;
        precedentJ1C = false;
        precedentJ1X = false;
        precedentJ1Y = false;
        precedentJ1Z = false;
        precedentJ1Haut = false;
        precedentJ1Bas = false;
        precedentJ1Gauche = false;
        precedentJ1Droite = false;
    }
}
