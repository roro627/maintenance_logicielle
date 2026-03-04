from ball import Ball
from bullet import Bullet
from player import Player
from constantes import WHITE, BLACK, RED, GREEN, BLUE, SCREEN_WIDTH, SCREEN_HEIGHT, FONT, FIRERATE, BALL_EQUIVALENT, FONT_SCORE

import pygame
import random

NOMBRE_IMAGES_EXPLOSION = 17
DECALAGE_SCISSION_BALLE = 10
LARGEUR_BOITE_SCORE = 150
HAUTEUR_BOITE_SCORE = 50
POSITION_BOITE_SCORE = (10, 10)
POSITION_TEXTE_SCORE = (10, 10)


def calculer_scissions_balle(detruite, niveau, position_x, position_y, niveaux_balles):
    """Retourne les specifications des boules filles a creer apres destruction.

    Args:
        detruite: Indique si la boule touchee a ete detruite.
        niveau: Niveau actuel de la boule detruite.
        position_x: Abscisse de reference.
        position_y: Ordonnee de reference.
        niveaux_balles: Table des niveaux de boules ``[couleur, rayon]``.

    Returns:
        Liste des specifications de boules filles a instancier.
    """

    if not detruite or niveau >= len(niveaux_balles) - 1:
        return []

    couleur, rayon = niveaux_balles[niveau + 1]
    return [
        {
            "x": position_x,
            "y": position_y,
            "rayon": rayon,
            "niveau": niveau + 1,
            "couleur": couleur,
            "decalage": DECALAGE_SCISSION_BALLE,
        },
        {
            "x": position_x,
            "y": position_y,
            "rayon": rayon,
            "niveau": niveau + 1,
            "couleur": couleur,
            "decalage": -DECALAGE_SCISSION_BALLE,
        },
    ]


def charger_images_explosion(dossier_images):
    """Charge en memoire les images de l animation d explosion.

    Args:
        dossier_images: Dossier contenant les frames numerotees.

    Returns:
        Liste ordonnee des surfaces prechargees.
    """

    images = []
    for index in range(1, NOMBRE_IMAGES_EXPLOSION + 1):
        chemin_image = f"{dossier_images}/frame-{index:02d}.png"
        images.append(pygame.image.load(chemin_image).convert_alpha())
    return images


class Game():
    def __init__(self, screen: pygame.Surface):
        """Initialise l etat runtime d une partie.

        Args:
            screen: Surface principale de rendu.
        """

        self.screen: pygame.Surface = screen
        self.level = 0
        self.ball_level = [[BLACK, 50], [RED, 40], [GREEN, 33], [BLUE, 25]]
        self.ballEquivalents = [10,7,3,1]
        self.ballsToSpawn = BALL_EQUIVALENT
        self.perdu: bool = False
        self.shootCD: int = 0
        self.texture: pygame.Surface = pygame.transform.scale(
            pygame.image.load('./assets/bg_pxl.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.images_explosion = charger_images_explosion("./assets/explosion_frames")
        self.surface_score = pygame.Surface((LARGEUR_BOITE_SCORE, HAUTEUR_BOITE_SCORE), pygame.SRCALPHA)
        self.score_affiche = -1

        self.frameNumberLoseAnim: int = 0
        self.frameNumberWinAnim : int = 0
        self.frameNumberSpawnBalls : int = 0
        self.frameNumberBeginLevel: int = 0
        self.perdu = False

        self.player = Player()
        wheels = self.player.getWheels()
        self.playerGroup = pygame.sprite.Group()
        self.playerGroup.add(self.player)
        self.balls = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.playerGroup)
        self.all_sprites.add(wheels[0])
        self.all_sprites.add(wheels[1])
        self._mettre_a_jour_surface_score(force=True)

    def createBalls(self):
        """Cree une nouvelle boule compatible avec le budget du niveau.

        Returns:
            Aucun.
        """

        while True:
            ballType : int = random.randint(0,len(self.ball_level)-1)
            if self.ballEquivalents[ballType] <= self.ballsToSpawn:
                newball = Ball(random.randint(100, SCREEN_WIDTH-100),
                        random.randint(-100, -40), self.ball_level[ballType][1], ballType, self.ball_level[ballType][0])
                self.balls.add(newball)
                self.all_sprites.add(newball)
                self.ballsToSpawn -= self.ballEquivalents[ballType]
                return
       
    def nextLevel(self):
        """Passe au niveau suivant et reinitialise les compteurs de transition.

        Returns:
            Aucun.
        """

        self.level += 1
        self.ballsToSpawn = BALL_EQUIVALENT + self.level * 5
        
        self.frameNumberWinAnim : int = 0
        self.frameNumberSpawnBalls : int = 0
        self.frameNumberBeginLevel = 0

    def _mettre_a_jour_surface_score(self, force=False):
        """Met a jour le cache graphique du score si necessaire.

        Args:
            force: Force la regeneration meme si le score est identique.

        Returns:
            Aucun.
        """

        if not force and self.score_affiche == self.player.score:
            return

        self.surface_score = pygame.Surface((LARGEUR_BOITE_SCORE, HAUTEUR_BOITE_SCORE), pygame.SRCALPHA)
        pygame.draw.rect(self.surface_score, (255, 255, 255, 180), self.surface_score.get_rect())
        texte_score = FONT_SCORE.render("Score : " + str(self.player.score), True, (0, 0, 0))
        self.surface_score.blit(texte_score, POSITION_TEXTE_SCORE)
        self.score_affiche = self.player.score

    def showGame(self):
        """Execute une iteration de la boucle de jeu.

        Returns:
            Tuple `(fin_de_partie, retour_menu)`.
        """
        
        if self.frameNumberBeginLevel < 60:
            self.frameNumberBeginLevel += 1
            self.screen.blit(self.texture, (0,0))
            texte_niveau = FONT.render('NIVEAU ' + str(self.level), True, (0, 0, 0))
            rectangle_niveau = texte_niveau.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(texte_niveau, rectangle_niveau)
            return False, False
            
        if pygame.key.get_pressed()[pygame.K_f]:
            if self.perdu:
                return True,False
            else:
                return False, True

        self.shootCD += 1
        
        if self.ballsToSpawn > 0:
            if self.frameNumberSpawnBalls % 20 == 0:
                self.createBalls()
            self.frameNumberSpawnBalls += 1

        # Toutes les 10 frames, on tire
        if self.shootCD == FIRERATE and not self.perdu:
            self.shootCD = 0
            bullet = Bullet(self.player.rect.centerx, self.player.rect.top)
            self.all_sprites.add(bullet)
            self.bullets.add(bullet)

        self.all_sprites.update()

        hitBalls = pygame.sprite.groupcollide(
            self.balls, self.bullets, False, True)
        for hit in hitBalls:

            destroyed: bool = hit.take_damage()
            if destroyed:
                self.player.score += hit.base_life_points
                for specification in calculer_scissions_balle(
                    destroyed,
                    hit.level,
                    hit.rect.x,
                    hit.rect.y,
                    self.ball_level,
                ):
                    boule_fille = Ball(
                        specification["x"],
                        specification["y"],
                        specification["rayon"],
                        specification["niveau"],
                        specification["couleur"],
                    )
                    boule_fille.decale(specification["decalage"])
                    self.balls.add(boule_fille)
                    self.all_sprites.add(boule_fille)
                hit.kill()

        self.screen.blit(self.texture, (0,0))

        self.all_sprites.draw(self.screen)

        self._mettre_a_jour_surface_score()
        self.screen.blit(self.surface_score, POSITION_BOITE_SCORE)

        hitPlayer = pygame.sprite.groupcollide(
            self.balls, self.playerGroup, False, False)

        if hitPlayer:
            self.perdu = True
            self.player.kill()

        if self.perdu:
            text_surface = FONT.render('PERDUUUUUUU', False, (0, 0, 0))
            self.screen.blit(text_surface, text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
            if self.frameNumberLoseAnim == 0:
                pygame.mixer.music.load("./assets/sound//musicdeath.mp3")
                pygame.mixer.music.play()

            if self.frameNumberLoseAnim < len(self.images_explosion):
                self.frameNumberLoseAnim += 1
                deathImage = self.images_explosion[self.frameNumberLoseAnim - 1]
                self.screen.blit(deathImage, (self.player.rect.left -
                                              20, self.player.rect.top-80))

        if len(self.balls.sprites()) == 0 and not self.perdu:
            text_surface = FONT.render('GAGNÉ', False, (0, 0, 0))
            self.screen.blit(text_surface, text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
            
            if self.frameNumberWinAnim == 240 and not self.perdu:
                self.nextLevel()
            self.frameNumberWinAnim += 1

        return False, False

    def registerScore(self):
        """Affiche l ecran de saisie du pseudo.

        Returns:
            Tuple `(fin_de_partie, retour_menu)`.
        """

        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        pseudo_chars = [0, 0, 0]
        current_position = 0
        input_active = True
        cursor_visible = True
        cursor_timer = 0
        horloge_saisie = pygame.time.Clock()
        
        while input_active:
            cursor_timer += 1
            if cursor_timer >= 20:
                cursor_visible = not cursor_visible
                cursor_timer = 0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    input_active = False
                    pygame.quit()
                    break
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        pseudo = ''.join([alphabet[i] for i in pseudo_chars])
                        self._saveScore(pseudo)
                        input_active = False
                    elif event.key == pygame.K_f:
                        input_active = False
                    elif event.key == pygame.K_UP:
                        pseudo_chars[current_position] = (pseudo_chars[current_position] + 1) % len(alphabet)
                    elif event.key == pygame.K_DOWN:
                        pseudo_chars[current_position] = (pseudo_chars[current_position] - 1) % len(alphabet)
                    elif event.key == pygame.K_LEFT:
                        current_position = (current_position - 1) % 3
                    elif event.key == pygame.K_RIGHT:
                        current_position = (current_position + 1) % 3
            
            self.screen.blit(self.texture, (0,0))
            
            title_text = FONT.render("ENREGISTRER LE SCORE !", True, WHITE)
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
            self.screen.blit(title_text, title_rect)
            
            score_text = FONT.render(f"Score: {self.player.score}", True, WHITE)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
            self.screen.blit(score_text, score_rect)
            
            instruction_text = FONT_SCORE.render("Entrez votre pseudo (3 lettres):", True, WHITE)
            instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            self.screen.blit(instruction_text, instruction_rect)
            
            char_spacing = 60
            start_x = SCREEN_WIDTH // 2 - char_spacing
            
            for i in range(3):
                char_box = pygame.Surface((50, 50), pygame.SRCALPHA)
                
                if i == current_position:
                    pygame.draw.rect(char_box, (255, 255, 0, 200), char_box.get_rect())
                    pygame.draw.rect(char_box, BLACK, char_box.get_rect(), 3)
                else:
                    pygame.draw.rect(char_box, (255, 255, 255, 200), char_box.get_rect())
                    pygame.draw.rect(char_box, BLACK, char_box.get_rect(), 2)
                
                letter = alphabet[pseudo_chars[i]]
                letter_surface = FONT.render(letter, True, BLACK)
                letter_rect = letter_surface.get_rect(center=(25, 25))
                char_box.blit(letter_surface, letter_rect)
                
                box_rect = char_box.get_rect(center=(start_x + i * char_spacing, SCREEN_HEIGHT // 2 + 20))
                self.screen.blit(char_box, box_rect)
                
                if i == current_position and cursor_visible:
                    cursor_y = SCREEN_HEIGHT // 2 + 50
                    pygame.draw.line(self.screen, WHITE, 
                                   (start_x + i * char_spacing - 15, cursor_y), 
                                   (start_x + i * char_spacing + 15, cursor_y), 3)
            
            controls_text = [
                "↑↓ : Changer la lettre",
                "←→ : Changer de position", 
                "R : Valider",
                "F : Annuler"
            ]
            
            for j, text in enumerate(controls_text):
                control_surface = FONT_SCORE.render(text, True, WHITE)
                control_rect = control_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90 + j * 20))
                self.screen.blit(control_surface, control_rect)
            
            pygame.display.flip()
            horloge_saisie.tick(40)
        
        return False,False
    
    def _saveScore(self, pseudo):
        """Sauvegarde le score courant dans le fichier local.

        Args:
            pseudo: Pseudo a associer au score.

        Returns:
            Aucun.
        """
        try:
            scores = []
            try:
                with open("highscore", "r", encoding="utf-8") as file:
                    for line in file:
                        line = line.strip()
                        parts = line.split('-')
                        pseudo_existing = parts[0]
                        score_existing = int(parts[1])
                        scores.append((pseudo_existing, score_existing))
            except FileNotFoundError:
                pass
            
            scores.append((pseudo, self.player.score))
            
            scores.sort(key=lambda x: x[1], reverse=True)
            
            with open("highscore", "w", encoding="utf-8") as file:
                for pseudo_score, score in scores:
                    file.write(f"{pseudo_score}-{score}\n")
                    
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du score: {e}")
        
