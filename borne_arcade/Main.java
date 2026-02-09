public class Main {
    /**
     * Lance la boucle principale du menu de la borne.
     *
     * @param args arguments CLI non utilises.
     */
    public static void main(String[] args){
	Graphique g = new Graphique();
	while(true){
	    try{
		// Thread.sleep(250);
	    }catch(Exception e){};
	    g.selectionJeu();
	}
    }
}
