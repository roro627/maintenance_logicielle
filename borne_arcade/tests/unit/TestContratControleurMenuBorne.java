import java.awt.Canvas;
import java.awt.event.KeyEvent;
import java.util.List;

/**
 * Verifie la logique headless du menu de la borne.
 */
public class TestContratControleurMenuBorne {

    /**
     * Point d entree du test de controleur.
     *
     * @param args arguments CLI non utilises.
     * @throws Exception si un lancement simule echoue.
     */
    public static void main(String[] args) throws Exception {
        testerAlignementCatalogueEtBoutons();
        testerSelectionInitialeEtNavigation();
        testerConfirmationFermeture();
        testerLancementJeuStandard();
        testerVerrouillageEtDeblocageMaintenance();
    }

    /**
     * Verifie que l index visuel des boutons suit le meme ordre que le catalogue logique.
     */
    private static void testerAlignementCatalogueEtBoutons() {
        List<JeuCatalogue> jeux = CatalogueJeux.listerJeux();

        for (int index = 0; index < jeux.size(); index++) {
            assertCondition(
                Bouton.calculerIndexTableauDepuisPositionCatalogue(index) == index,
                "Le bouton " + index + " doit conserver le meme index que le catalogue logique"
            );
        }
    }

    /**
     * Verifie la selection initiale et la navigation circulaire.
     */
    private static void testerSelectionInitialeEtNavigation() {
        List<JeuCatalogue> jeux = CatalogueJeux.listerJeux();
        ControleurMenuBorne controleur = creerControleur(jeux, new EtatModeMaintenance(), new LanceurJeuFactice());

        assertCondition(
            controleur.getEtat().getIndexSelection() == jeux.size() - 1,
            "La selection initiale doit pointer sur le dernier bouton historique"
        );
        assertCondition(
            controleur.getEtat().getJeuSelectionne().getNom().equals(jeux.get(jeux.size() - 1).getNom()),
            "Le jeu initial doit correspondre au dernier element du catalogue"
        );

        controleur.deplacerHaut();
        assertCondition(controleur.getEtat().getIndexSelection() == 0, "Le deplacement haut doit boucler vers le debut");

        controleur.deplacerBas();
        assertCondition(
            controleur.getEtat().getIndexSelection() == jeux.size() - 1,
            "Le deplacement bas doit reboucler vers la fin"
        );
    }

    /**
     * Verifie l ouverture, l annulation et la confirmation de fermeture.
     */
    private static void testerConfirmationFermeture() {
        ControleurMenuBorne controleur = creerControleur(
            CatalogueJeux.listerJeux(),
            new EtatModeMaintenance(),
            new LanceurJeuFactice()
        );

        controleur.demanderFermeture();
        assertCondition(
            controleur.getEtat().isConfirmationFermetureOuverte(),
            "La confirmation de fermeture doit etre ouverte"
        );

        controleur.annulerFermeture();
        assertCondition(
            !controleur.getEtat().isConfirmationFermetureOuverte(),
            "L annulation doit fermer la confirmation"
        );
        assertCondition(!controleur.getEtat().isQuitterDemande(), "L annulation ne doit pas demander la fermeture");

        controleur.demanderFermeture();
        controleur.confirmerFermeture();
        assertCondition(
            controleur.getEtat().isQuitterDemande(),
            "La confirmation doit marquer la fermeture comme demandee"
        );
    }

    /**
     * Verifie qu un jeu standard est bien transmis au lanceur injecte.
     *
     * @throws Exception si le lancement simule echoue.
     */
    private static void testerLancementJeuStandard() throws Exception {
        List<JeuCatalogue> jeux = CatalogueJeux.listerJeux();
        EtatModeMaintenance etatMaintenance = new EtatModeMaintenance();
        LanceurJeuFactice lanceur = new LanceurJeuFactice();
        ControleurMenuBorne controleur = creerControleur(jeux, etatMaintenance, lanceur);

        JeuCatalogue jeuStandard = trouverPremierJeuHorsMaintenance(jeux, etatMaintenance.getNomJeuMaintenance());
        assertCondition(
            controleur.selectionnerJeuParNom(jeuStandard.getNom()),
            "Le controleur doit pouvoir cibler un jeu standard"
        );

        boolean jeuLance = controleur.lancerJeuSelectionne();
        assertCondition(jeuLance, "Le lancement d un jeu standard doit etre autorise");
        assertCondition(
            lanceur.getNomDernierJeuLance().equals(jeuStandard.getNom()),
            "Le lanceur factice doit recevoir le bon jeu"
        );
        assertCondition(lanceur.getNombreLancements() == 1, "Un seul lancement doit etre enregistre");
    }

    /**
     * Verifie le verrouillage puis le debloquage du mode maintenance.
     *
     * @throws Exception si le lancement simule echoue.
     */
    private static void testerVerrouillageEtDeblocageMaintenance() throws Exception {
        List<JeuCatalogue> jeux = CatalogueJeux.listerJeux();
        EtatModeMaintenance etatMaintenance = new EtatModeMaintenance();
        LanceurJeuFactice lanceur = new LanceurJeuFactice();
        ControleurMenuBorne controleur = creerControleur(jeux, etatMaintenance, lanceur);

        assertCondition(
            controleur.selectionnerJeuParNom(etatMaintenance.getNomJeuMaintenance()),
            "Le jeu maintenance doit exister dans le catalogue"
        );

        boolean lancementVerrouille = controleur.lancerJeuSelectionne();
        assertCondition(!lancementVerrouille, "Le jeu maintenance ne doit pas etre lancable avant debloquage");
        assertCondition(lanceur.getNombreLancements() == 0, "Aucun lancement ne doit etre enregistre tant que le mode est verrouille");

        debloquerModeMaintenance(etatMaintenance);
        assertCondition(etatMaintenance.estDebloque(), "La sequence secrete doit debloquer le mode maintenance");

        boolean lancementAutorise = controleur.lancerJeuSelectionne();
        assertCondition(lancementAutorise, "Le mode maintenance doit devenir lancable apres debloquage");
        assertCondition(
            lanceur.getNomDernierJeuLance().equals(etatMaintenance.getNomJeuMaintenance()),
            "Le lancement debloque doit cibler le jeu maintenance"
        );
    }

    /**
     * Construit un controleur de test.
     *
     * @param jeux catalogue a utiliser.
     * @param etatMaintenance etat maintenance a reutiliser.
     * @param lanceur lanceur factice.
     * @return controleur preconfigure.
     */
    private static ControleurMenuBorne creerControleur(
        List<JeuCatalogue> jeux,
        EtatModeMaintenance etatMaintenance,
        LanceurJeuFactice lanceur
    ) {
        return new ControleurMenuBorne(jeux, etatMaintenance, lanceur);
    }

    /**
     * Retourne un jeu standard pour le test de lancement.
     *
     * @param jeux catalogue complet.
     * @param nomMaintenance nom du jeu maintenance.
     * @return premier jeu non maintenance.
     */
    private static JeuCatalogue trouverPremierJeuHorsMaintenance(List<JeuCatalogue> jeux, String nomMaintenance) {
        for (JeuCatalogue jeu : jeux) {
            if (!jeu.getNom().equals(nomMaintenance)) {
                return jeu;
            }
        }
        throw new IllegalStateException("Aucun jeu standard hors maintenance n a ete trouve");
    }

    /**
     * Debloque le mode maintenance via sa vraie sequence de touches.
     *
     * @param etatMaintenance etat a debloquer.
     */
    private static void debloquerModeMaintenance(EtatModeMaintenance etatMaintenance) {
        ClavierBorneArcade clavier = new ClavierBorneArcade();
        Canvas source = new Canvas();
        String[] sequence = ConfigurationModeMaintenance.charger().getSequenceSecrete();
        for (String entree : sequence) {
            int codeTouche = convertirEntreeEnCode(entree);
            simulerAppui(clavier, source, codeTouche);
            etatMaintenance.traiterSequenceSecrete(clavier);
            simulerRelachement(clavier, source, codeTouche);
            etatMaintenance.traiterSequenceSecrete(clavier);
        }
    }

    /**
     * Convertit une entree symbolique en code clavier AWT.
     *
     * @param entree identifiant symbolique.
     * @return code AWT.
     */
    private static int convertirEntreeEnCode(String entree) {
        if ("J1A".equals(entree)) {
            return KeyEvent.VK_F;
        }
        if ("J1B".equals(entree)) {
            return KeyEvent.VK_G;
        }
        if ("J1C".equals(entree)) {
            return KeyEvent.VK_H;
        }
        if ("J1X".equals(entree)) {
            return KeyEvent.VK_R;
        }
        if ("J1Y".equals(entree)) {
            return KeyEvent.VK_T;
        }
        if ("J1Z".equals(entree)) {
            return KeyEvent.VK_Y;
        }
        if ("J1HAUT".equals(entree)) {
            return KeyEvent.VK_UP;
        }
        if ("J1BAS".equals(entree)) {
            return KeyEvent.VK_DOWN;
        }
        if ("J1GAUCHE".equals(entree)) {
            return KeyEvent.VK_LEFT;
        }
        if ("J1DROITE".equals(entree)) {
            return KeyEvent.VK_RIGHT;
        }
        throw new IllegalArgumentException("Entree maintenance inconnue: " + entree);
    }

    /**
     * Simule un appui de touche.
     *
     * @param clavier clavier borne.
     * @param source composant source.
     * @param codeTouche code de touche.
     */
    private static void simulerAppui(ClavierBorneArcade clavier, Canvas source, int codeTouche) {
        KeyEvent evenement = new KeyEvent(
            source,
            KeyEvent.KEY_PRESSED,
            System.currentTimeMillis(),
            0,
            codeTouche,
            KeyEvent.CHAR_UNDEFINED
        );
        clavier.keyPressed(evenement);
    }

    /**
     * Simule un relachement de touche.
     *
     * @param clavier clavier borne.
     * @param source composant source.
     * @param codeTouche code de touche.
     */
    private static void simulerRelachement(ClavierBorneArcade clavier, Canvas source, int codeTouche) {
        KeyEvent evenement = new KeyEvent(
            source,
            KeyEvent.KEY_RELEASED,
            System.currentTimeMillis(),
            0,
            codeTouche,
            KeyEvent.CHAR_UNDEFINED
        );
        clavier.keyReleased(evenement);
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

    /**
     * Lanceur factice pour verifier les appels du controleur.
     */
    private static final class LanceurJeuFactice implements LanceurJeuMenu {
        /** Nom du dernier jeu lance. */
        private String nomDernierJeuLance = "";

        /** Nombre total de lancements. */
        private int nombreLancements = 0;

        /**
         * Memorise simplement le jeu demande.
         *
         * @param jeu jeu a lancer.
         */
        @Override
        public void lancerJeu(JeuCatalogue jeu) {
            this.nomDernierJeuLance = jeu.getNom();
            this.nombreLancements += 1;
        }

        /**
         * Retourne le nom du dernier jeu lance.
         *
         * @return nom du jeu.
         */
        public String getNomDernierJeuLance() {
            return nomDernierJeuLance;
        }

        /**
         * Retourne le nombre de lancements enregistres.
         *
         * @return compteur de lancements.
         */
        public int getNombreLancements() {
            return nombreLancements;
        }
    }
}
