import java.io.File;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * Verifie le catalogue headless de la borne.
 */
public class TestUnitaireCatalogueJeux {

    /**
     * Point d entree du test de catalogue.
     *
     * @param args arguments CLI non utilises.
     */
    public static void main(String[] args) {
        List<JeuCatalogue> jeuxCatalogue = CatalogueJeux.listerJeux();
        assertCondition(!jeuxCatalogue.isEmpty(), "Le catalogue de jeux ne doit pas etre vide");

        List<String> nomsCatalogue = new ArrayList<String>();
        for (JeuCatalogue jeu : jeuxCatalogue) {
            nomsCatalogue.add(jeu.getNom());
            assertCondition(!jeu.getNom().trim().isEmpty(), "Nom de jeu vide dans le catalogue");
            assertCondition(new File(jeu.getCheminJeu()).isDirectory(), "Dossier jeu introuvable: " + jeu.getCheminJeu());
            assertCondition(new File(jeu.getCheminLanceur()).isFile(), "Lanceur introuvable: " + jeu.getCheminLanceur());
            assertCondition(!jeu.getDescription().isEmpty(), "Description vide pour " + jeu.getNom());
            assertCondition(auMoinsUnBoutonRenseigne(jeu.getBoutons()), "Mapping boutons vide pour " + jeu.getNom());
        }

        Set<String> nomsUniques = new HashSet<String>(nomsCatalogue);
        assertCondition(nomsUniques.size() == nomsCatalogue.size(), "Le catalogue contient des doublons de nom de jeu");

        File[] dossiersJeux = new File("projet").listFiles(File::isDirectory);
        assertCondition(dossiersJeux != null, "Impossible de lister le dossier projet/");
        assertCondition(dossiersJeux.length == jeuxCatalogue.size(), "Le nombre de jeux du disque doit correspondre au catalogue");

        ConfigurationModeMaintenance configurationMaintenance = ConfigurationModeMaintenance.charger();
        assertCondition(configurationMaintenance.estActif(), "Le mode maintenance doit etre actif pour la borne");
        assertCondition(!configurationMaintenance.getNomJeu().trim().isEmpty(), "Le nom du jeu maintenance ne doit pas etre vide");
        assertCondition(!configurationMaintenance.getFichierVerrouillage().trim().isEmpty(), "Le fichier de verrouillage maintenance ne doit pas etre vide");
        assertCondition(
            CatalogueJeux.trouverJeuParNom(configurationMaintenance.getNomJeu()) != null,
            "Le jeu maintenance configure doit exister dans le catalogue"
        );
    }

    /**
     * Indique si un mapping contient au moins une commande lisible.
     *
     * @param boutons mapping joystick + boutons.
     * @return true si au moins une valeur est renseignee.
     */
    private static boolean auMoinsUnBoutonRenseigne(String[] boutons) {
        for (String bouton : boutons) {
            if (bouton != null && !bouton.trim().isEmpty()) {
                return true;
            }
        }
        return false;
    }

    /**
     * Leve une erreur claire si la condition est fausse.
     *
     * @param condition condition attendue.
     * @param message message d erreur.
     */
    private static void assertCondition(boolean condition, String message) {
        if (!condition) {
            throw new IllegalStateException(message);
        }
    }
}
