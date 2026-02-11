import java.awt.Font;
import java.io.File;
import MG2D.Couleur;
import MG2D.audio.Bruitage;
import MG2D.geometrie.Rectangle;

/**
 * Gere les deplacements dans la liste des jeux du menu principal.
 */
public class BoiteSelection extends Boite {
    /** Pointeur courant de selection. */
    private final Pointeur pointeur;

    /** Police appliquee aux textes du menu. */
    private final Font policeMenu;

    /** Son joue lors d un deplacement dans la liste. */
    private final Bruitage sonSelection;

    /**
     * Construit la boite de selection du menu.
     *
     * @param rectangle zone graphique de selection.
     * @param pointeurMenu pointeur de jeu selectionne.
     */
    public BoiteSelection(Rectangle rectangle, Pointeur pointeurMenu) {
        super(rectangle);
        this.pointeur = pointeurMenu;
        this.policeMenu = chargerPoliceMenu();
        this.sonSelection = chargerSonSelection();
    }

    /**
     * Charge la police du menu une seule fois.
     *
     * @return la police de menu, ou une police de secours.
     */
    private Font chargerPoliceMenu() {
        try {
            File fichierPolice = new File("fonts/PrStart.ttf");
            Font police = Font.createFont(Font.TRUETYPE_FONT, fichierPolice);
            return police.deriveFont(26.0f);
        } catch (Exception exception) {
            return new Font("Dialog", Font.PLAIN, 26);
        }
    }

    /**
     * Charge le son de navigation une seule fois.
     *
     * @return le son de navigation, ou null si indisponible.
     */
    private Bruitage chargerSonSelection() {
        try {
            return new Bruitage("sound/bip.mp3");
        } catch (Exception exception) {
            return null;
        }
    }

    /**
     * Joue le son de navigation si disponible.
     */
    private void jouerSonSelection() {
        if (sonSelection == null) {
            return;
        }
        try {
            sonSelection.lecture();
        } catch (Exception exception) {
            // Ignore volontairement les erreurs audio pour garder le menu fluide.
        }
    }

    /**
     * Applique la police et la couleur standards a tous les titres.
     */
    private void appliquerStyleTextesMenu() {
        for (int index = 0; index < Graphique.tableau.length; index++) {
            Graphique.tableau[index].getTexte().setPolice(policeMenu);
            Graphique.tableau[index].getTexte().setCouleur(Couleur.BLANC);
        }
    }

    /**
     * Translate la liste des jeux du decalage indique.
     *
     * @param decalageY decalage vertical a appliquer.
     */
    private void translaterElementsMenu(int decalageY) {
        for (int index = 0; index < Graphique.tableau.length; index++) {
            Graphique.tableau[index].getTexte().translater(0, decalageY);
            Graphique.tableau[index].getTexture().translater(0, decalageY);
        }
        appliquerStyleTextesMenu();
    }

    /**
     * Reaffiche le texte courant si le clignotement l a masque.
     */
    private void reafficherTexteCourantSiNecessaire() {
        if (Graphique.textesAffiches[pointeur.getValue()]) {
            return;
        }
        Graphique.afficherTexte(pointeur.getValue());
        Graphique.textesAffiches[pointeur.getValue()] = true;
    }

    /**
     * Gere la navigation sur un evenement joystick haut.
     */
    private void gererMontee() {
        reafficherTexteCourantSiNecessaire();
        jouerSonSelection();

        if (pointeur.getValue() == Graphique.tableau.length - 1) {
            pointeur.setValue(0);
            translaterElementsMenu(ConstantesMenu.ECART_ELEMENTS * (Graphique.tableau.length - 1));
            return;
        }

        translaterElementsMenu(-ConstantesMenu.ECART_ELEMENTS);
        pointeur.setValue(pointeur.getValue() + 1);
    }

    /**
     * Gere la navigation sur un evenement joystick bas.
     */
    private void gererDescente() {
        reafficherTexteCourantSiNecessaire();
        jouerSonSelection();

        if (pointeur.getValue() == 0) {
            pointeur.setValue(Graphique.tableau.length - 1);
            translaterElementsMenu(-ConstantesMenu.ECART_ELEMENTS * (Graphique.tableau.length - 1));
            return;
        }

        translaterElementsMenu(ConstantesMenu.ECART_ELEMENTS);
        pointeur.setValue(pointeur.getValue() - 1);
    }

    /**
     * Traite la navigation utilisateur dans le menu.
     *
     * @param clavier etat des controles borne.
     * @return false si l utilisateur demande la fermeture du menu.
     */
    public boolean selection(ClavierBorneArcade clavier) {
        if (clavier.getJoyJ1HautTape() && pointeur.getValue() <= Graphique.tableau.length - 1) {
            gererMontee();
        }

        if (clavier.getJoyJ1BasTape() && pointeur.getValue() >= 0) {
            gererDescente();
        }

        if (clavier.getBoutonJ1ZTape()) {
            return false;
        }
        return true;
    }

    /**
     * Retourne le pointeur de selection.
     *
     * @return pointeur menu.
     */
    public Pointeur getPointeur() {
        return pointeur;
    }
}
