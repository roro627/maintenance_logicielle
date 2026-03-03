/**
 * Abstraction du lancement d un jeu depuis le menu de la borne.
 */
public interface LanceurJeuMenu {

    /**
     * Lance un jeu et attend sa fin.
     *
     * @param jeu jeu a lancer.
     * @throws Exception si le lancement echoue.
     */
    void lancerJeu(JeuCatalogue jeu) throws Exception;
}
