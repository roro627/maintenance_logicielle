import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/**
 * Gere le parsing des fichiers de configuration d un jeu.
 */
public final class AnalyseurConfigJeu {

    /** Nombre attendu de zones pour le mapping boutons. */
    private static final int NOMBRE_CHAMPS_BOUTONS = 7;

    /**
     * Interdit l instanciation de cette classe utilitaire.
     */
    private AnalyseurConfigJeu() {
    }

    /**
     * Lit les lignes de description d un jeu.
     *
     * @param cheminJeu chemin vers le dossier du jeu.
     * @param maxLignes nombre maximum de lignes a retourner.
     * @return la liste des lignes lues, possiblement vide.
     */
    public static List<String> lireDescription(String cheminJeu, int maxLignes) {
        List<String> lignes = new ArrayList<String>();
        String fichier = cheminJeu + "/description.txt";

        try (BufferedReader lecteur = new BufferedReader(new FileReader(fichier))) {
            String ligne;
            while ((ligne = lecteur.readLine()) != null && lignes.size() < maxLignes) {
                lignes.add(ligne);
            }
        } catch (IOException exception) {
            return lignes;
        }

        return lignes;
    }

    /**
     * Lit la premiere ligne du fichier bouton d un jeu.
     *
     * @param cheminJeu chemin vers le dossier du jeu.
     * @return un tableau de sept valeurs (joystick + 6 boutons).
     */
    public static String[] lireBoutons(String cheminJeu) {
        String[] valeurs = new String[NOMBRE_CHAMPS_BOUTONS];
        for (int index = 0; index < valeurs.length; index++) {
            valeurs[index] = "";
        }

        String fichier = cheminJeu + "/bouton.txt";
        try (BufferedReader lecteur = new BufferedReader(new FileReader(fichier))) {
            String ligne = lecteur.readLine();
            if (ligne == null || ligne.trim().isEmpty()) {
                return valeurs;
            }

            String[] morceaux = ligne.split(":");
            int limite = Math.min(morceaux.length, valeurs.length);
            for (int index = 0; index < limite; index++) {
                valeurs[index] = morceaux[index].trim();
            }
        } catch (IOException exception) {
            return valeurs;
        }

        return valeurs;
    }
}
