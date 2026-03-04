import java.awt.Font;
import java.io.IOException;
import java.io.File;
import java.nio.file.DirectoryStream;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

import MG2D.geometrie.*;
import MG2D.geometrie.Point;
import MG2D.audio.*;
import MG2D.*;
import MG2D.FenetrePleinEcran;

/**
 * Gere l affichage et la navigation du menu principal de la borne.
 */
public class Graphique {

    //private final Fenetre f;
    private static final FenetrePleinEcran f = new FenetrePleinEcran("_Menu Borne D'arcade_");
    private int TAILLEX;
    private int TAILLEY;
    private ClavierBorneArcade clavier;
    private BoiteSelection bs;
    private BoiteImage bi;
    private BoiteDescription bd;
    public static Bouton[] tableau;
    private Pointeur pointeur;
    private EtatModeMaintenance etatModeMaintenance;
    private ControleurMenuBorne controleurMenu;
    private LanceurJeuMenu lanceurJeu;
    private Texte texteModeMaintenance;
    private boolean texteModeMaintenanceAffiche;
    Font font;
	public static boolean[] textesAffiches;
	public static Bruitage musiqueFond;
    private static String[] tableauMusiques;
	private static int cptMus;


    /**
     * Initialise le menu graphique, charge les jeux et lance la musique de fond.
     */
    public Graphique(){
    	

	TAILLEX = ConstantesMenu.LARGEUR_MENU;
	TAILLEY = ConstantesMenu.HAUTEUR_MENU;

	font = null;
	try{
	    File in = new File("fonts/PrStart.ttf");
	    font = font.createFont(Font.TRUETYPE_FONT, in);
	    font = font.deriveFont(32.0f);
	}catch (Exception e) {
	    System.err.println(e.getMessage());
	}

	//f = new Fenetre("_Menu Borne D'arcade_",TAILLEX,TAILLEY);
	f.setVisible(true);
	clavier = new ClavierBorneArcade();
	f.addKeyListener(clavier);
	f.getP().addKeyListener(clavier);

	List<JeuCatalogue> jeuxCatalogue = CatalogueJeux.listerJeux();
	int cpt = jeuxCatalogue.size();

	tableau = new Bouton[cpt];
	textesAffiches = new boolean[cpt];
	for(int i=0;i<cpt;i++){
		textesAffiches[i]=true;
	}
	
	Bouton.remplirBouton(jeuxCatalogue);
	etatModeMaintenance = new EtatModeMaintenance();
	lanceurJeu = new LanceurJeuProcessus();
	controleurMenu = new ControleurMenuBorne(jeuxCatalogue, etatModeMaintenance, lanceurJeu);
	pointeur = new Pointeur();
	pointeur.setValue(controleurMenu.getEtat().getIndexSelection());
	Font policeModeMaintenance = new Font("Dialog", Font.PLAIN, 16);
	if(font != null){
	    policeModeMaintenance = font.deriveFont(16.0f);
	}
	texteModeMaintenance = new Texte(Couleur.NOIR, "", policeModeMaintenance, new Point(960, 165));
	texteModeMaintenanceAffiche = false;
	bs = new BoiteSelection(new Rectangle(Couleur .GRIS_CLAIR, new Point(0, 0), new Point(640, TAILLEY), true), pointeur);
	//f.ajouter(bs.getRectangle());
	//System.out.println(tableau[pointeur.getValue()].getChemin());
	bi = new BoiteImage(new Rectangle(Couleur .GRIS_FONCE, new Point(640, 512), new Point(TAILLEX, TAILLEY), true), new String(tableau[pointeur.getValue()].getChemin()));
	//f.ajouter(bi.getRectangle());
	bd = new BoiteDescription(new Rectangle(Couleur .GRIS, new Point(640, 0), new Point(TAILLEX, 512), true));
	bd.lireFichier(tableau[pointeur.getValue()].getChemin());
	bd.lireHighScore(tableau[pointeur.getValue()].getChemin());
	//f.ajouter(bd.getRectangle());

	Texture fond = new Texture("img/fondretro3.png", new Point(0, 0), TAILLEX, TAILLEY);
	f.ajouter(fond);
	//ajout apres fond car bug graphique sinon
	f.ajouter(bi.getImage());
	for(int i = 0 ; i < bd.getMessage().length ; i++){
	    f.ajouter(bd.getMessage()[i]);
	}
	//f.ajouter(bd.getMessage());
	f.ajouter(pointeur.getTriangleGauche());
	f.ajouter(pointeur.getTriangleDroite());
	for(int i = 0 ; i < tableau.length ; i++){
	    f.ajouter(tableau[i].getTexture());
	}
	f.ajouter(pointeur.getRectangleCentre());
	for(int i = 0 ; i < tableau.length ; i++){
	    f.ajouter(tableau[i].getTexte());
	    tableau[i].getTexte().setPolice(font);
	    tableau[i].getTexte().setCouleur(Couleur.BLANC);
	}
	//add texture
	for(int i = 0 ; i < bd.getBouton().length ; i++){
	    f.ajouter(bd.getBouton()[i]);
	}
	f.ajouter(bd.getJoystick());
	//add texte
	for(int i = 0 ; i < bd.gettBouton().length ; i++){
	    f.ajouter(bd.gettBouton()[i]);
	}
	f.ajouter(bd.gettJoystick());
	f.ajouter(new Ligne(Couleur.NOIR,new Point(670,360), new Point(1250,360)));
	f.ajouter(new Ligne(Couleur.NOIR,new Point(670,190), new Point(1250,190)));
	f.ajouter(new Ligne(Couleur.NOIR,new Point(960,210), new Point(960,310)));
	f.ajouter(bd.getHighscore());
	for(int i = 0 ; i < bd.getListeHighScore().length ; i++){
	    f.ajouter(bd.getListeHighScore()[i]);
	}
	mettreAJourAffichageModeMaintenance();
	
	/*Musique de fond*/
	//Comptage du nombre de musiques disponibles
	Path cheminMusiques = FileSystems.getDefault().getPath("sound/bg/");
	cptMus=0;
	if(Files.isDirectory(cheminMusiques)){
	    try (DirectoryStream<Path> directoryStream = Files.newDirectoryStream(cheminMusiques)) {
		for (Path path : directoryStream) {
		    cptMus++;
		}
	    } catch (IOException e) {
		cptMus = 0;
	    }
	    //Creation d'un tableau de musiques
	    tableauMusiques = new String[cptMus];
	    try (DirectoryStream<Path> directoryStream = Files.newDirectoryStream(cheminMusiques)) {
		int i = cptMus-1;
		for (Path path : directoryStream) {
		    tableauMusiques[i]=path.getFileName().toString();
		    i--;
		}
	    } catch (IOException e) {
		cptMus = 0;
		tableauMusiques = new String[0];
	    }
	}else{
	    tableauMusiques = new String[0];
	}
	//Choix d'une musique aleatoire et lecture de celle-ci
	if(cptMus>0){
	    this.lectureMusiqueFond();
	}
    }

    /**
     * Boucle principale de selection de jeu.
     */
    public void selectionJeu(){	
		Texture fondBlancTransparent = new Texture("./img/blancTransparent.png", new Point(0,0));
		Rectangle boutonNon = new Rectangle(Couleur.ROUGE, new Point(340, 600), 200, 100, true);
		Rectangle boutonOui = new Rectangle(Couleur.VERT, new Point(740, 600), 200, 100, true);
		Texte message = new Texte(Couleur.NOIR, "Voulez vous vraiment quitter ?", font, new Point(640, 800));
		Texte non = new Texte(Couleur.NOIR, "NON", font, new Point(440, 650));
		Texte oui = new Texte(Couleur.NOIR, "OUI", font, new Point(840, 650));
		Rectangle rectSelection = new Rectangle(Couleur.BLEU, new Point(330,590),220,120, true);
		int frame=0;
		boolean fermetureMenu=false;
		int selectionSur = 0;
		while(true){
			try {
				if(frame==0){
					if(textesAffiches[pointeur.getValue()]==true){
						f.supprimer(tableau[pointeur.getValue()].getTexte());
						textesAffiches[pointeur.getValue()]=false;
					}
				}
				if(frame==3){
					if(textesAffiches[pointeur.getValue()]==false){
						f.ajouter(tableau[pointeur.getValue()].getTexte());
						textesAffiches[pointeur.getValue()]=true;
					}
				}
				if(frame == (ConstantesMenu.FRAMES_CLIGNOTEMENT - 1)){
					frame=-1;
				}
				frame++;
				// System.out.println("frame n°"+frame);
			}
			catch (Exception e) {
				System.err.println(e.getMessage());
			}
			try{
				Thread.sleep(ConstantesMenu.DELAI_BOUCLE_MS);
			}catch(Exception e){}
			
			if(!fermetureMenu){
				etatModeMaintenance.appliquerDemandeVerrouillageExterne();
				if(etatModeMaintenance.traiterSequenceSecrete(clavier)){
					mettreAJourAffichageModeMaintenance();
				}
				if(etatModeMaintenance.ouvertureDemandee(clavier)){
					lancerModeMaintenance();
					etatModeMaintenance.appliquerDemandeVerrouillageExterne();
					mettreAJourAffichageModeMaintenance();
					continue;
				}
				traiterNavigationMenu();
				bi.setImage(tableau[pointeur.getValue()].getChemin());
				tableau[pointeur.getValue()].getTexte().setPolice(font);
				bd.lireFichier(tableau[pointeur.getValue()].getChemin());
				bd.lireHighScore(tableau[pointeur.getValue()].getChemin());
				bd.lireBouton(tableau[pointeur.getValue()].getChemin());

				if(clavier.getBoutonJ1ATape()){
					if(!lancerJeuSelectionneDepuisControleur()){
						mettreAJourAffichageModeMaintenance();
						f.rafraichir();
						continue;
					}
					if(estJeuMaintenanceSelectionne()){
						etatModeMaintenance.appliquerDemandeVerrouillageExterne();
						mettreAJourAffichageModeMaintenance();
					}
				}

				if(clavier.getBoutonJ1ZTape()){
					controleurMenu.demanderFermeture();
					f.ajouter(fondBlancTransparent);
					f.ajouter(message);
					f.ajouter(rectSelection);
					f.ajouter(boutonNon);
					f.ajouter(boutonOui);
					f.ajouter(non);
					f.ajouter(oui);
					fermetureMenu=true;
				}
			}else{
					if(clavier.getJoyJ1DroiteEnfoncee()){
						selectionSur=1;
					}
						
					if(clavier.getJoyJ1GaucheEnfoncee()){
						selectionSur=0;
					}
					   
					
					if(selectionSur==0){
						rectSelection.setA(new Point(330,590));
						rectSelection.setB(new Point(550,710));
					}
					else{
						rectSelection.setB(new Point(950,710));
						rectSelection.setA(new Point(730,590));
						
					}
					if(clavier.getBoutonJ1ATape()){
						if(selectionSur==0){
							controleurMenu.annulerFermeture();
							f.supprimer(fondBlancTransparent);
							f.supprimer(message);
							f.supprimer(rectSelection);
							f.supprimer(boutonNon);
							f.supprimer(boutonOui);
							f.supprimer(non);
							f.supprimer(oui);
							fermetureMenu=false;
						}
						else{
							controleurMenu.confirmerFermeture();
							System.exit(0);
						}
					}

			}
			f.rafraichir();
		}//fin while true
    }

    /**
     * Indique si le jeu actuellement selectionne correspond au mode maintenance.
     *
     * @return true si le pointeur est sur le jeu maintenance.
     */
    private boolean estJeuMaintenanceSelectionne(){
	if(etatModeMaintenance == null || !etatModeMaintenance.estActif()){
	    return false;
	}
	if(controleurMenu == null || controleurMenu.getEtat().getJeuSelectionne() == null){
	    return false;
	}
	return controleurMenu.getEtat().getJeuSelectionne().getNom().equals(etatModeMaintenance.getNomJeuMaintenance());
    }
    
    /**
     * Met a jour l affichage de l etat du mode maintenance.
     */
    private void mettreAJourAffichageModeMaintenance(){
	if(etatModeMaintenance == null){
	    return;
	}

	String messageModeMaintenance = etatModeMaintenance.getMessageStatut();
	if(messageModeMaintenance == null || messageModeMaintenance.isEmpty()){
	    if(texteModeMaintenanceAffiche){
		f.supprimer(texteModeMaintenance);
		texteModeMaintenanceAffiche = false;
	    }
	    return;
	}

	texteModeMaintenance.setTexte(messageModeMaintenance);
	if(!texteModeMaintenanceAffiche){
	    f.ajouter(texteModeMaintenance);
	    texteModeMaintenanceAffiche = true;
	}
    }

    /**
     * Lance le mode maintenance cache.
     */
    private void lancerModeMaintenance(){
	if(etatModeMaintenance == null || !etatModeMaintenance.estActif()){
	    return;
	}

	try{
	    Graphique.stopMusiqueFond();
	    ProcessBuilder constructeur = new ProcessBuilder("./"+etatModeMaintenance.getNomJeuMaintenance()+".sh");
	    Process process = constructeur.start();
	    process.waitFor();
	}catch(IOException exception){
	    System.err.println("Impossible de lancer le mode maintenance: "+exception.getMessage());
	}catch(InterruptedException exception){
	    Thread.currentThread().interrupt();
	}finally{
	    Graphique.lectureMusiqueFond();
	}
    }

    /**
     * Traite la navigation haut/bas via le controleur logique.
     */
    private void traiterNavigationMenu(){
	int ancienIndex = controleurMenu.getEtat().getIndexSelection();
	if(clavier.getJoyJ1HautTape()){
	    controleurMenu.deplacerHaut();
	    appliquerTransitionSelection(ancienIndex, controleurMenu.getEtat().getIndexSelection());
	}

	ancienIndex = controleurMenu.getEtat().getIndexSelection();
	if(clavier.getJoyJ1BasTape()){
	    controleurMenu.deplacerBas();
	    appliquerTransitionSelection(ancienIndex, controleurMenu.getEtat().getIndexSelection());
	}
    }

    /**
     * Lance le jeu selectionne via le controleur logique.
     *
     * @return true si le jeu a ete lance.
     */
    private boolean lancerJeuSelectionneDepuisControleur(){
	try{
	    if(controleurMenu.estSelectionMaintenanceVerrouillee()){
		return false;
	    }
	    Graphique.stopMusiqueFond();
	    return controleurMenu.lancerJeuSelectionne();
	}catch(IOException exception){
	    System.err.println("Impossible de lancer le jeu: "+exception.getMessage());
	    return false;
	}catch(InterruptedException exception){
	    Thread.currentThread().interrupt();
	    return false;
	}catch(Exception exception){
	    System.err.println("Erreur inattendue lors du lancement du jeu: "+exception.getMessage());
	    return false;
	}finally{
	    Graphique.lectureMusiqueFond();
	}
    }

    /**
     * Applique la translation visuelle correspondant au changement de selection.
     *
     * @param ancienIndex index avant navigation.
     * @param nouvelIndex index apres navigation.
     */
    private void appliquerTransitionSelection(int ancienIndex, int nouvelIndex){
	if(ancienIndex == nouvelIndex){
	    return;
	}

	reafficherTexteCourantSiNecessaire(ancienIndex);
	if(ancienIndex == tableau.length - 1 && nouvelIndex == 0){
	    translaterElementsMenu(-ConstantesMenu.ECART_ELEMENTS * (tableau.length - 1));
	}else if(ancienIndex == 0 && nouvelIndex == tableau.length - 1){
	    translaterElementsMenu(ConstantesMenu.ECART_ELEMENTS * (tableau.length - 1));
	}else if(nouvelIndex > ancienIndex){
	    translaterElementsMenu(ConstantesMenu.ECART_ELEMENTS);
	}else{
	    translaterElementsMenu(-ConstantesMenu.ECART_ELEMENTS);
	}
	pointeur.setValue(nouvelIndex);
    }

    /**
     * Reaffiche un texte masque par le clignotement.
     *
     * @param index index du texte a reafficher.
     */
    private void reafficherTexteCourantSiNecessaire(int index){
	if(textesAffiches[index]){
	    return;
	}
	afficherTexte(index);
	textesAffiches[index] = true;
    }

    /**
     * Translate les widgets de menu d un decalage vertical.
     *
     * @param decalageY decalage a appliquer.
     */
    private void translaterElementsMenu(int decalageY){
	for(int index = 0 ; index < tableau.length ; index++){
	    tableau[index].getTexte().translater(0, decalageY);
	    tableau[index].getTexture().translater(0, decalageY);
	    tableau[index].getTexte().setPolice(font);
	    tableau[index].getTexte().setCouleur(Couleur.BLANC);
	}
    }

    /**
     * Lance une musique de fond choisie aleatoirement.
     */
    public static void lectureMusiqueFond() {
    	if(cptMus<=0 || tableauMusiques==null || tableauMusiques.length==0){
    	    return;
    	}
    	musiqueFond = new Bruitage ("sound/bg/"+tableauMusiques[(int)(Math.random()*cptMus)]);
    	musiqueFond.lecture();
    }
	
	/**
	 * Stoppe la musique de fond en cours.
	 */
	public static void stopMusiqueFond(){
		if(musiqueFond!=null){
		    musiqueFond.arret();
		}
	}
	
	/**
	 * Reaffiche le texte d un jeu du menu.
	 *
	 * @param valeur index du jeu dans le tableau.
	 */
	public static void afficherTexte(int valeur){
		f.ajouter(tableau[valeur].getTexte());
	}
}
