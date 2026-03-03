/**
 * Verifie les contrats purs de generation des ennemis Initial Drift.
 */
public class TestContratInitialDrift {

    /**
     * Point d entree du test de contrat.
     *
     * @param args arguments CLI non utilises.
     */
    public static void main(String[] args) {
        testerPoliceForceeAuDebut();
        testerJeepDisponibleAuScoreIntermediaire();
        testerTonneauDisponibleAuScoreEleve();
        testerPlafondDesPoliciers();
    }

    /**
     * Verifie le type force au debut de partie.
     */
    private static void testerPoliceForceeAuDebut() {
        FabriqueEnnemiInitialDrift fabrique = new FabriqueEnnemiInitialDrift();
        ConfigurationEnnemiInitialDrift configuration = fabrique.creerConfiguration(0, 0, 0.9, 0.0, 1024);

        assertCondition(configuration.getType() == FabriqueEnnemiInitialDrift.TYPE_POLICE, "Le debut de partie doit forcer la police");
        assertCondition(configuration.getAbscisse() == 350, "La premiere voie doit etre selectionnee pour un tirage minimum");
        assertCondition(configuration.getVitesse() == 15, "La vitesse police de base doit etre appliquee");
    }

    /**
     * Verifie l apparition possible d une jeep au score intermediaire.
     */
    private static void testerJeepDisponibleAuScoreIntermediaire() {
        FabriqueEnnemiInitialDrift fabrique = new FabriqueEnnemiInitialDrift();
        ConfigurationEnnemiInitialDrift configuration = fabrique.creerConfiguration(10, 0, 0.0, 0.45, 1024);

        assertCondition(configuration.getType() == FabriqueEnnemiInitialDrift.TYPE_JEEP, "Une jeep doit etre possible entre 5 et 14 points");
        assertCondition("jeep".equals(configuration.getNomType()), "Le type logique jeep doit etre expose");
        assertCondition(configuration.getVitesse() == 11, "La vitesse jeep doit suivre le palier de score");
    }

    /**
     * Verifie l apparition du tonneau au score eleve.
     */
    private static void testerTonneauDisponibleAuScoreEleve() {
        FabriqueEnnemiInitialDrift fabrique = new FabriqueEnnemiInitialDrift();
        ConfigurationEnnemiInitialDrift configuration = fabrique.creerConfiguration(20, 0, 0.99, 0.99, 1024);

        assertCondition(configuration.getType() == FabriqueEnnemiInitialDrift.TYPE_TONNEAU, "Le tonneau doit etre possible a score eleve");
        assertCondition(configuration.getAbscisse() == 855, "La derniere voie doit etre choisie pour un tirage maximum");
        assertCondition(configuration.getVitesse() == 24, "La vitesse tonneau doit suivre le palier de score");
    }

    /**
     * Verifie le plafond des voitures de police.
     */
    private static void testerPlafondDesPoliciers() {
        FabriqueEnnemiInitialDrift fabrique = new FabriqueEnnemiInitialDrift();
        ConfigurationEnnemiInitialDrift configuration = fabrique.creerConfiguration(0, 6, 0.5, 0.2, 1024);

        assertCondition(
            !configuration.isCreationAutorisee(),
            "Le jeu ne doit pas creer une nouvelle voiture de police quand le plafond est atteint"
        );
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
