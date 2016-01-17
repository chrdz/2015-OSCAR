# ==============================================================================
"""Interface GRAPHIQUE : OSCAR: Outil de Simulation Comportemental par
    Attraction-Répulsion"""
# ==============================================================================
__author__  = "Pastureau Romain, Rodriguez Charlotte"
__version__ = "1.0"
__date__    = "2015-12-11"
# ------------------------------------------------------------------------------
from oscar_noyau import *
import os
import sys
import time
#===============================================================================
#===============================================================================
class GraphiqueWorld(World):
    
    def __init__(self,nom_fichier):
        World.__init__(self,nom_fichier)
        
        
    def simu(self) :
        """simulation"""
        
        pygame.init()
        self.isplay = False
        self.emptyboard = False
        font = pygame.font.SysFont(pygame.font.get_default_font(), 30)
        #font = pygame.font.SysFont("fonts/GOTHICB.ttf", 30)

        t=25
        self.fenetre = pygame.display.set_mode((self.size[0]*t, self.size[1]*t+40))
    
        liste_soil = os.listdir("soil/")
        self.dict_soil={}

        for i in range(len(liste_soil)) :
            self.dict_soil[liste_soil[i]] = pygame.image.load("soil/"+liste_soil[i]).convert_alpha()

        self.images={}
        for ordre in self.graphes:
            self.images[ordre]={}
            for status in self.graphes[ordre]:
                self.images[ordre][status]=pygame.image.load("sprites/"+self.graphes[ordre][status].image)
        self.image_monde=pygame.image.load("sprites/"+self.image)

        self.background = pygame.image.load("background.png")
        self.generation = 0
        liste_icones = os.listdir("play/")
        dict_play = {}
        
        square_under = pygame.Surface((self.size[0]*t, 40))
        square_under.fill((0,0,0))
        
        for i in range(len(liste_icones)) :
            dict_play[liste_icones[i]] = pygame.image.load("play/"+liste_icones[i]).convert_alpha()

        self.soil = []
        for i in range(self.size[0]) :
            self.soil.append([])
            for j in range(self.size[1]) :
                z = random.choice(liste_soil)
                self.soil[i].append(z)

        self.blitplateau(t)

        clock = pygame.time.Clock()
        timer = 0

        counttime = [timer]

        while self.continue_simu() :
            for event in pygame.event.get() :

                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()

                mouseX, mouseY = pygame.mouse.get_pos()
                self.fenetre.blit(self.background, (0, self.size[1]*t))

            self.fenetre.blit(square_under, (0, self.size[1]*t))                
##                self.fenetre.blit(dict_play["back_button_unhover.png"], ((self.size[0]*t)//2-70, self.size[1]*t+5))
            if self.isplay == False :
                self.fenetre.blit(dict_play["play_button_unhover.png"], ((self.size[0]*t)//2-20, self.size[1]*t+5))
            else :
                self.fenetre.blit(dict_play["pause_button_unhover.png"], ((self.size[0]*t)//2-20, self.size[1]*t+5))
            self.fenetre.blit(dict_play["next_button_unhover.png"], ((self.size[0]*t)//2+30, self.size[1]*t+5))

            if event.type == MOUSEMOTION :

                ##Back
##                    if (self.size[0]*t)//2-70 < mouseX < (self.size[0]*t)//2-30 and self.size[1]*t+5 < mouseY < self.size[1]*t+35 :
##                        self.fenetre.blit(dict_play["back_button_hover.png"], ((self.size[0]*t)//2-70, self.size[1]*t+5))

                ##Play/Pause
                if self.isplay == False :
                    if (self.size[0]*t)//2-20 < mouseX < (self.size[0]*t)//2+20 and self.size[1]*t+5 < mouseY < self.size[1]*t+35 :
                        self.fenetre.blit(dict_play["play_button_hover.png"], ((self.size[0]*t)//2-20, self.size[1]*t+5))
                else :
                    if (self.size[0]*t)//2-20 < mouseX < (self.size[0]*t)//2+20 and self.size[1]*t+5 < mouseY < self.size[1]*t+35 :
                        self.fenetre.blit(dict_play["pause_button_hover.png"], ((self.size[0]*t)//2-20, self.size[1]*t+5))

                ##Forward
                if (self.size[0]*t)//2+30 < mouseX < (self.size[0]*t)//2+70 and self.size[1]*t+5 < mouseY < self.size[1]*t+35 :
                    self.fenetre.blit(dict_play["next_button_hover.png"], ((self.size[0]*t)//2+30, self.size[1]*t+5))

            if event.type == MOUSEBUTTONDOWN :
                if (self.size[0]*t)//2-20 < mouseX < (self.size[0]*t)//2+20 and self.size[1]*t+5 < mouseY < self.size[1]*t+35 :
                    self.play()
                if (self.size[0]*t)//2+30 < mouseX < (self.size[0]*t)//2+70 and self.size[1]*t+5 < mouseY < self.size[1]*t+35 :
                    self.life()
                    self.generation += 1
                    self.blitplateau(t)

            if self.isplay == True :
                if timer > counttime[self.generation]+1000 :
                    if self.emptyboard == True :
                        self.isplay = False
                    self.life()
                    self.blitplateau(t)
    ##                    print("Génération ", self.generation)
    ##                    for i in range(self.size[0]) :
    ##                        for j in range(self.size[1]) :
    ##                            if self.board[i][j] == [] :
    ##                                print("|  ", end="")
    ##                            else :
    ##                                print("|XX", end="")
    ##                        print("|", end="\n")
    ##                    print("\n\n")
                    counttime.append(timer)
                    self.generation += 1

            blitgen = font.render(str(self.generation), 1, (255, 255, 255))
            self.fenetre.blit(blitgen,(10, self.size[1]*t+10))
      
            dt = clock.tick(30)
            timer += dt            

            pygame.display.flip()

    def play(self) :
        if self.isplay == False :
            self.isplay = True
        else :
            self.isplay = False

    def blitplateau(self, t) :
        self.emptyboard = True
        for i in range(self.size[0]) :
            for j in range(self.size[1]) :
                self.fenetre.blit(self.dict_soil[self.soil[i][j]], (i*t,j*t))
                            
                if self.board[i][j] == [] :
                    self.fenetre.blit(self.image_monde, (i*t,j*t))
                    
                else :
                    self.emptyboard = False
                    agent=self.board[i][j][0]
                    ordre=type(agent.sommet).__name__.lower()
                    status=agent.status
                    self.fenetre.blit(self.images[ordre][status],(i*t, j*t))
#===============================================================================
#===============================================================================
if __name__ == "__main__":
    #trop lent:
    #nom_fichier="./fichiers_version_graphique/g_jdv_36x19.txt"
    
    nom_fichier="./fichiers_version_graphique/g_animal_cailloux.txt"
    #nom_fichier="./fichiers_version_graphique/g_animal_cailloux_vege_vieillesse.txt"
    #nom_fichier="./fichiers_version_graphique/g_breed.txt"
    #nom_fichier="./fichiers_version_graphique/g_jdv_base.txt"

    #nom_fichier="./fichiers_version_graphique/g_trace_seul.txt"
    #nom_fichier="./fichiers_version_graphique/g_trace_seul_vieillesse.txt"

    #nom_fichier="jeu_de_la_vie.txt"
    a=GraphiqueWorld(nom_fichier)

