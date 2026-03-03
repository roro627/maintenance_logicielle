import java.awt.Font;
import java.util.List;

import MG2D.Couleur;
import MG2D.geometrie.Point;
import MG2D.geometrie.Texture;
import MG2D.geometrie.Texte;

public class Bouton {
    private Texte texte;
    private String chemin;
    private String nom;
    private Texture texture;
    private int numeroDeJeu;


    public Bouton(){
	this.texte = null;
	this.texture = null;
	this.chemin = null;
	this.nom = null;
    }

    public Bouton(Texte texte, Texture texture, String chemin, String nom){
	this.texte = texte;
	this.texture = texture;
	this.chemin = chemin;
	this.nom = nom;
    }

    /**
     * Remplit les boutons du menu a partir du catalogue de jeux.
     *
     * @param jeuxCatalogue jeux detectes dans le catalogue borne.
     */
    public static void remplirBouton(List<JeuCatalogue> jeuxCatalogue){
	for(int i = 0 ; i < Graphique.tableau.length ; i++){
	    Graphique.tableau[i] = new Bouton();
	}

	for(int position = 0 ; position < jeuxCatalogue.size() ; position++){
	    JeuCatalogue jeu = jeuxCatalogue.get(position);
	    int indexTableau = calculerIndexTableauDepuisPositionCatalogue(position);
	    Graphique.tableau[indexTableau].setTexte(
		new Texte(Couleur.NOIR, jeu.getNom(), new Font("Calibri", Font.TYPE1_FONT, 30), new Point(310, 510))
	    );
	    Graphique.tableau[indexTableau].setTexture(new Texture("img/bouton2.png", new Point(100, 478), 400, 65));
	    Graphique.tableau[indexTableau].getTexte().translater(0, -ConstantesMenu.ECART_ELEMENTS * position);
	    Graphique.tableau[indexTableau].getTexture().translater(0, -ConstantesMenu.ECART_ELEMENTS * position);
	    Graphique.tableau[indexTableau].setChemin(jeu.getCheminJeu());
	    Graphique.tableau[indexTableau].setNom(jeu.getNom());
	    Graphique.tableau[indexTableau].setNumeroDeJeu(indexTableau);
	}
    }

    /**
     * Remplit les boutons du menu avec le catalogue courant.
     */
    public static void remplirBouton(){
	remplirBouton(CatalogueJeux.listerJeux());
    }

    /**
     * Retourne l index visuel associe a une position du catalogue logique.
     *
     * @param positionCatalogue position du jeu dans le catalogue.
     * @return index de stockage du bouton correspondant.
     */
    public static int calculerIndexTableauDepuisPositionCatalogue(int positionCatalogue){
	return positionCatalogue;
    }

    public String getChemin() {
	return chemin;
    }

    public void setChemin(String chemin) {
	this.chemin = chemin;
    }

    public String getNom() {
	return nom;
    }

    public void setNom(String nom) {
	this.nom = nom;
    }

    public Texte getTexte() {
	return texte;
    }

    public void setTexte(Texte texte) {
	this.texte = texte;
    }

    public Texture getTexture() {
	return texture;
    }

    public void setTexture(Texture texture) {
	this.texture = texture;
    }

    public int getNumeroDeJeu() {
	return numeroDeJeu;
    }

    public void setNumeroDeJeu(int numeroDeJeu) {
	this.numeroDeJeu = numeroDeJeu;
    }
}
