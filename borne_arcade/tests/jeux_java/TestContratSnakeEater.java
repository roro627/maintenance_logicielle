import java.io.File;
import java.util.ArrayList;

/**
 * Verifie les contrats critiques de persistence de Snake Eater.
 */
public class TestContratSnakeEater {

    /**
     * Point d entree du test de contrat.
     *
     * @param args arguments CLI non utilises.
     * @throws Exception si la preparation de fichier echoue.
     */
    public static void main(String[] args) throws Exception {
        testerCycleCaracteres();
        testerInsertionTrieeEtTroncature();
    }

    /**
     * Verifie le cycle des caracteres de saisie de high score.
     */
    private static void testerCycleCaracteres() {
        assertCondition(HighScore.suivant('A') == 'B', "Le caractere suivant de A doit etre B");
        assertCondition(HighScore.suivant('Z') == '.', "Le caractere suivant de Z doit etre .");
        assertCondition(HighScore.suivant('.') == ' ', "Le caractere suivant de . doit etre un espace");
        assertCondition(HighScore.suivant(' ') == 'A', "Le caractere suivant de l espace doit etre A");

        assertCondition(HighScore.precedent('B') == 'A', "Le caractere precedent de B doit etre A");
        assertCondition(HighScore.precedent('A') == ' ', "Le caractere precedent de A doit etre l espace");
        assertCondition(HighScore.precedent(' ') == '.', "Le caractere precedent de l espace doit etre .");
        assertCondition(HighScore.precedent('.') == 'Z', "Le caractere precedent de . doit etre Z");
    }

    /**
     * Verifie l insertion triee d un score et la troncature au top 10.
     *
     * @throws Exception si le fichier temporaire ne peut pas etre manipule.
     */
    private static void testerInsertionTrieeEtTroncature() throws Exception {
        File fichier = File.createTempFile("snake_eater_highscore", ".txt");
        fichier.deleteOnExit();

        ArrayList<LigneHighScore> listeInitiale = new ArrayList<LigneHighScore>();
        for (int index = 0; index < 10; index++) {
            listeInitiale.add(new LigneHighScore("J" + index + " " + "-" + (100 - index)));
        }
        HighScore.enregistrerFichier(fichier.getAbsolutePath(), listeInitiale, "AAA", 101);

        ArrayList<LigneHighScore> resultat = HighScore.lireFichier(fichier.getAbsolutePath());
        assertCondition(resultat.size() == 10, "Le fichier high score doit rester limite au top 10");
        assertCondition("AAA".equals(resultat.get(0).getNom()), "Le nouveau score doit etre insere a la bonne position");
        assertCondition(resultat.get(0).getScore() == 101, "Le score insere doit etre conserve");
        assertCondition(resultat.get(9).getScore() == 92, "Le moins bon score doit etre ecarte apres troncature");
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
