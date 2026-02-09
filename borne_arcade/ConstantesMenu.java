import java.io.FileInputStream;
import java.io.IOException;
import java.util.Properties;

/**
 * Centralise les constantes de rendu du menu.
 */
public final class ConstantesMenu {

    /** Chemin du fichier de proprietes menu. */
    private static final String CHEMIN_FICHIER = "config/constantes_menu.properties";

    /** Largeur du menu. */
    public static final int LARGEUR_MENU = chargerEntier("menu.largeur", 1280);

    /** Hauteur du menu. */
    public static final int HAUTEUR_MENU = chargerEntier("menu.hauteur", 1024);

    /** Ecart vertical entre deux jeux. */
    public static final int ECART_ELEMENTS = chargerEntier("menu.ecart_elements", 110);

    /** Delai de la boucle principale en millisecondes. */
    public static final int DELAI_BOUCLE_MS = chargerEntier("menu.delai_boucle_ms", 50);

    /** Nombre de frames de clignotement. */
    public static final int FRAMES_CLIGNOTEMENT = chargerEntier("menu.frames_clignotement", 7);

    /** Nombre de lignes de description affichees. */
    public static final int NB_LIGNES_DESCRIPTION = chargerEntier("menu.nb_lignes_description", 10);

    /** Nombre de lignes de highscore affichees. */
    public static final int NB_LIGNES_HIGHSCORE = chargerEntier("menu.nb_lignes_highscore", 10);

    /**
     * Interdit l instanciation de cette classe utilitaire.
     */
    private ConstantesMenu() {
    }

    /**
     * Charge un entier depuis le fichier de configuration.
     *
     * @param cle cle de configuration a lire.
     * @param valeurParDefaut valeur utilisee si la cle est absente.
     * @return la valeur entiere lue ou la valeur par defaut.
     */
    private static int chargerEntier(String cle, int valeurParDefaut) {
        Properties proprietes = new Properties();
        try (FileInputStream flux = new FileInputStream(CHEMIN_FICHIER)) {
            proprietes.load(flux);
            String valeur = proprietes.getProperty(cle);
            if (valeur == null) {
                return valeurParDefaut;
            }
            return Integer.parseInt(valeur.trim());
        } catch (IOException | NumberFormatException exception) {
            return valeurParDefaut;
        }
    }
}
