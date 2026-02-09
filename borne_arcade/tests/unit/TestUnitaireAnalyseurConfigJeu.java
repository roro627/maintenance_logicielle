import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.List;

/**
 * Verifie le parsing des fichiers de configuration d un jeu.
 */
public class TestUnitaireAnalyseurConfigJeu {

    /**
     * Point d entree du test unitaire.
     *
     * @param args arguments CLI non utilises.
     * @throws IOException en cas d erreur de fichier.
     */
    public static void main(String[] args) throws IOException {
        File dossier = creerJeuTemporaire();

        List<String> description = AnalyseurConfigJeu.lireDescription(dossier.getAbsolutePath(), 3);
        assertCondition(description.size() == 2, "Description doit contenir 2 lignes");
        assertCondition("Ligne un".equals(description.get(0)), "Premiere ligne invalide");

        String[] boutons = AnalyseurConfigJeu.lireBoutons(dossier.getAbsolutePath());
        assertCondition(boutons.length == 7, "Le tableau boutons doit contenir 7 champs");
        assertCondition("Joystick".equals(boutons[0]), "Le champ joystick est invalide");
        assertCondition("B6".equals(boutons[6]), "Le dernier champ bouton est invalide");

        supprimerRecursivement(dossier);
    }

    /**
     * Cree un dossier de jeu temporaire avec ses fichiers de config.
     *
     * @return le dossier cree.
     * @throws IOException en cas d erreur IO.
     */
    private static File creerJeuTemporaire() throws IOException {
        File dossier = new File("test_jeu_temporaire");
        dossier.mkdirs();

        try (FileWriter description = new FileWriter(new File(dossier, "description.txt"), false)) {
            description.write("Ligne un\n");
            description.write("Ligne deux\n");
        }

        try (FileWriter boutons = new FileWriter(new File(dossier, "bouton.txt"), false)) {
            boutons.write("Joystick:B1:B2:B3:B4:B5:B6\n");
        }

        return dossier;
    }

    /**
     * Supprime recursivement un dossier de test.
     *
     * @param fichier racine a supprimer.
     */
    private static void supprimerRecursivement(File fichier) {
        if (fichier.isDirectory()) {
            File[] enfants = fichier.listFiles();
            if (enfants != null) {
                for (File enfant : enfants) {
                    supprimerRecursivement(enfant);
                }
            }
        }
        fichier.delete();
    }

    /**
     * Verifie une condition et leve une exception en cas d echec.
     *
     * @param condition resultat attendu.
     * @param message message d erreur.
     */
    private static void assertCondition(boolean condition, String message) {
        if (!condition) {
            throw new IllegalStateException(message);
        }
    }
}
