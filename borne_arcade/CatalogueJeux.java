import java.io.IOException;
import java.nio.file.DirectoryStream;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

/**
 * Centralise la decouverte des jeux de la borne sans dependre de l interface graphique.
 */
public final class CatalogueJeux {
    /** Repertoire des jeux depuis borne_arcade/. */
    private static final Path CHEMIN_REPERTOIRE_JEUX = FileSystems.getDefault().getPath("projet");

    /** Nombre de lignes de description affichees dans le menu. */
    private static final int NOMBRE_LIGNES_DESCRIPTION = ConstantesMenu.NB_LIGNES_DESCRIPTION;

    /**
     * Interdit l instanciation de cette classe utilitaire.
     */
    private CatalogueJeux() {
    }

    /**
     * Charge toutes les entrees du catalogue de jeux.
     *
     * @return liste triee des jeux detectes.
     */
    public static List<JeuCatalogue> listerJeux() {
        List<Path> dossiersJeux = listerDossiersJeux();
        List<JeuCatalogue> jeux = new ArrayList<JeuCatalogue>();
        for (Path dossierJeu : dossiersJeux) {
            jeux.add(construireJeuCatalogue(dossierJeu));
        }
        return jeux;
    }

    /**
     * Recherche une entree du catalogue par son nom.
     *
     * @param nomJeu nom logique recherche.
     * @return entree correspondante, ou null si absente.
     */
    public static JeuCatalogue trouverJeuParNom(String nomJeu) {
        for (JeuCatalogue jeu : listerJeux()) {
            if (jeu.getNom().equals(nomJeu)) {
                return jeu;
            }
        }
        return null;
    }

    /**
     * Retourne la liste triee des dossiers de jeux.
     *
     * @return liste triee des dossiers detectes.
     */
    private static List<Path> listerDossiersJeux() {
        List<Path> dossiers = new ArrayList<Path>();
        try (DirectoryStream<Path> flux = Files.newDirectoryStream(CHEMIN_REPERTOIRE_JEUX)) {
            for (Path chemin : flux) {
                if (Files.isDirectory(chemin)) {
                    dossiers.add(chemin);
                }
            }
        } catch (IOException exception) {
            throw new IllegalStateException(
                "Impossible de lire le catalogue jeux dans " + CHEMIN_REPERTOIRE_JEUX,
                exception
            );
        }
        dossiers.sort(Comparator.comparing(path -> path.getFileName().toString()));
        return dossiers;
    }

    /**
     * Construit une entree de catalogue a partir d un dossier jeu.
     *
     * @param dossierJeu dossier a convertir.
     * @return entree de catalogue prete a l emploi.
     */
    private static JeuCatalogue construireJeuCatalogue(Path dossierJeu) {
        String nomJeu = dossierJeu.getFileName().toString();
        String cheminRelatifJeu = CHEMIN_REPERTOIRE_JEUX.resolve(nomJeu).toString().replace('\\', '/');
        String cheminLanceur = nomJeu + ".sh";
        List<String> description = AnalyseurConfigJeu.lireDescription(cheminRelatifJeu, NOMBRE_LIGNES_DESCRIPTION);
        String[] boutons = AnalyseurConfigJeu.lireBoutons(cheminRelatifJeu);
        return new JeuCatalogue(nomJeu, cheminRelatifJeu, cheminLanceur, description, boutons);
    }
}
