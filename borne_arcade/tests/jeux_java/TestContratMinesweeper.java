/**
 * Verifie les contrats non graphiques critiques de Minesweeper.
 */
public class TestContratMinesweeper {

    /**
     * Point d entree du test de contrat Minesweeper.
     *
     * @param args arguments CLI non utilises.
     */
    public static void main(String[] args) {
        testerDimensionsEtBombes();
        testerDefaiteSurBombeDecouverte();
        testerVictoireQuandSeulesLesBombesRestentMasquees();
    }

    /**
     * Verifie la coherence des dimensions et du nombre de bombes.
     */
    private static void testerDimensionsEtBombes() {
        Board plateau = new Board(6, 5, 7);
        assertCondition(plateau.getWidth() == 6, "Largeur de plateau invalide");
        assertCondition(plateau.getHeight() == 5, "Hauteur de plateau invalide");
        assertCondition(compterBombes(plateau) == 7, "Le nombre de bombes placees doit correspondre a la configuration");
    }

    /**
     * Verifie la detection de defaite sur bombe decouverte.
     */
    private static void testerDefaiteSurBombeDecouverte() {
        Board plateau = new Board(4, 4, 1);
        for (Tile tuile : plateau.getTiles()) {
            if (tuile instanceof Bomb) {
                tuile.setMasked(false);
                assertCondition(plateau.endGameMine(), "La decouverte d une bombe doit terminer la partie");
                return;
            }
        }
        throw new IllegalStateException("Aucune bombe trouvee sur le plateau de test");
    }

    /**
     * Verifie la detection de victoire quand seules les bombes restent masquees.
     */
    private static void testerVictoireQuandSeulesLesBombesRestentMasquees() {
        Board plateau = new Board(4, 4, 2);
        for (Tile tuile : plateau.getTiles()) {
            if (!(tuile instanceof Bomb)) {
                tuile.setMasked(false);
            }
        }
        assertCondition(plateau.endGameWin(), "La victoire doit etre detectee quand toutes les cases sures sont revelees");
    }

    /**
     * Compte les bombes presentes sur un plateau.
     *
     * @param plateau plateau a analyser.
     * @return nombre de bombes effectivement placees.
     */
    private static int compterBombes(Board plateau) {
        int nombreBombes = 0;
        for (Tile tuile : plateau.getTiles()) {
            if (tuile instanceof Bomb) {
                nombreBombes += 1;
            }
        }
        return nombreBombes;
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
