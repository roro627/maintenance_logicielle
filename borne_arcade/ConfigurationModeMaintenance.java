import java.io.FileInputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;

/**
 * Centralise la configuration du mode maintenance cache.
 */
public final class ConfigurationModeMaintenance {
    /** Fichier de configuration du mode maintenance. */
    private static final String CHEMIN_CONFIGURATION = "config/maintenance_mode.properties";

    /** Valeur par defaut: mode maintenance actif. */
    private static final boolean DEFAUT_ACTIF = true;

    /** Valeur par defaut: nom du jeu maintenance. */
    private static final String DEFAUT_NOM_JEU = "MaintenanceMode";

    /** Valeur par defaut: sequence secrete de debloquage. */
    private static final String DEFAUT_SEQUENCE = "J1X,J1Y,J1Z,J1C";

    /** Valeur par defaut: bouton de lancement du mode maintenance. */
    private static final String DEFAUT_BOUTON_OUVERTURE = "J1B";

    /** Valeur par defaut: nom du fichier de verrouillage. */
    private static final String DEFAUT_FICHIER_VERROUILLAGE = ".verrouillage_mode_maintenance";

    /** Active ou non la fonctionnalite. */
    private final boolean actif;

    /** Nom du jeu a lancer en mode maintenance. */
    private final String nomJeu;

    /** Sequence de debloquage. */
    private final String[] sequenceSecrete;

    /** Bouton de lancement une fois debloque. */
    private final String boutonOuverture;

    /** Fichier de verrouillage emis par le jeu maintenance. */
    private final String fichierVerrouillage;

    /**
     * Construit une configuration immuable.
     *
     * @param modeActif etat actif/inactif du mode maintenance.
     * @param nomDuJeu nom du jeu maintenance.
     * @param sequence sequence de debloquage.
     * @param bouton bouton de lancement du jeu maintenance.
     * @param fichierCommandeVerrouillage fichier signal de verrouillage.
     */
    private ConfigurationModeMaintenance(
        boolean modeActif,
        String nomDuJeu,
        String[] sequence,
        String bouton,
        String fichierCommandeVerrouillage
    ) {
        this.actif = modeActif;
        this.nomJeu = nomDuJeu;
        this.sequenceSecrete = sequence;
        this.boutonOuverture = bouton;
        this.fichierVerrouillage = fichierCommandeVerrouillage;
    }

    /**
     * Charge la configuration depuis le fichier proprietes.
     *
     * @return la configuration prete a l emploi.
     */
    public static ConfigurationModeMaintenance charger() {
        Properties proprietes = new Properties();
        try (FileInputStream flux = new FileInputStream(CHEMIN_CONFIGURATION)) {
            proprietes.load(flux);
        } catch (IOException exception) {
            return new ConfigurationModeMaintenance(
                DEFAUT_ACTIF,
                DEFAUT_NOM_JEU,
                parserSequence(DEFAUT_SEQUENCE),
                DEFAUT_BOUTON_OUVERTURE,
                DEFAUT_FICHIER_VERROUILLAGE
            );
        }

        boolean modeActif = lireBooleen(proprietes, "maintenance.actif", DEFAUT_ACTIF);
        String nomDuJeu = lireTexte(proprietes, "maintenance.nom_jeu", DEFAUT_NOM_JEU);
        String sequence = lireTexte(proprietes, "maintenance.sequence_secrete", DEFAUT_SEQUENCE);
        String bouton = lireTexte(proprietes, "maintenance.bouton_ouverture", DEFAUT_BOUTON_OUVERTURE);
        String fichierCommandeVerrouillage = lireTexte(
            proprietes,
            "maintenance.fichier_verrouillage",
            DEFAUT_FICHIER_VERROUILLAGE
        );

        return new ConfigurationModeMaintenance(
            modeActif,
            nomDuJeu,
            parserSequence(sequence),
            bouton,
            fichierCommandeVerrouillage
        );
    }

    /**
     * Lit un booleen depuis les proprietes.
     *
     * @param proprietes source de configuration.
     * @param cle cle a lire.
     * @param valeurParDefaut valeur de secours.
     * @return la valeur booleenne lue.
     */
    private static boolean lireBooleen(Properties proprietes, String cle, boolean valeurParDefaut) {
        String valeur = proprietes.getProperty(cle);
        if (valeur == null) {
            return valeurParDefaut;
        }
        String normalise = valeur.trim();
        if ("1".equals(normalise) || "true".equalsIgnoreCase(normalise)) {
            return true;
        }
        if ("0".equals(normalise) || "false".equalsIgnoreCase(normalise)) {
            return false;
        }
        return valeurParDefaut;
    }

    /**
     * Lit un texte depuis les proprietes.
     *
     * @param proprietes source de configuration.
     * @param cle cle a lire.
     * @param valeurParDefaut valeur de secours.
     * @return texte lu ou valeur par defaut.
     */
    private static String lireTexte(Properties proprietes, String cle, String valeurParDefaut) {
        String valeur = proprietes.getProperty(cle);
        if (valeur == null || valeur.trim().isEmpty()) {
            return valeurParDefaut;
        }
        return valeur.trim();
    }

    /**
     * Parse une sequence "A,B,C" en tableau de boutons.
     *
     * @param sequenceBrute sequence au format texte.
     * @return tableau de boutons normalises.
     */
    private static String[] parserSequence(String sequenceBrute) {
        List<String> sequenceNormalisee = new ArrayList<String>();
        String[] elements = sequenceBrute.split(",");
        for (String element : elements) {
            String valeur = element.trim();
            if (!valeur.isEmpty()) {
                sequenceNormalisee.add(valeur.toUpperCase());
            }
        }

        if (sequenceNormalisee.isEmpty()) {
            return parserSequence(DEFAUT_SEQUENCE);
        }

        return sequenceNormalisee.toArray(new String[0]);
    }

    /**
     * Indique si le mode maintenance est actif.
     *
     * @return true si actif.
     */
    public boolean estActif() {
        return actif;
    }

    /**
     * Retourne le nom du jeu maintenance.
     *
     * @return nom du jeu.
     */
    public String getNomJeu() {
        return nomJeu;
    }

    /**
     * Retourne la sequence secrete de debloquage.
     *
     * @return sequence de boutons.
     */
    public String[] getSequenceSecrete() {
        return sequenceSecrete;
    }

    /**
     * Retourne le bouton de lancement du mode maintenance.
     *
     * @return bouton de lancement.
     */
    public String getBoutonOuverture() {
        return boutonOuverture;
    }

    /**
     * Retourne le fichier signal de verrouillage.
     *
     * @return nom de fichier de verrouillage.
     */
    public String getFichierVerrouillage() {
        return fichierVerrouillage;
    }
}
