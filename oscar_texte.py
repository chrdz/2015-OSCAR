# coding: utf-8
# ==============================================================================
"""Interface TEXTE : OSCAR: Outil de Simulation Comportemental par Attraction-Répulsion"""
# ==============================================================================
__author__  = "Pastureau Romain, Rodriguez Charlotte"
__version__ = "1.0"
__date__    = "2015-12-11"
# ------------------------------------------------------------------------------
from oscar_noyau import * 
#===============================================================================
#===============================================================================
class TexteWorld(World):
    #-------------------------------------------------------------------------------
    def __repr__(self):
        return grid(self.monde['str'])
    #-------------------------------------------------------------------------------
    @property
    def monde(self):
        """
        Matrix containing either the world's or the agent's char representation
        """
        t=len(self.agents)
        res_str=[[self.image for j in range(self.size[1])]
             for i in range(self.size[0])]
        a=0
        while a<t:
            i=self.agents[a].x
            j=self.agents[a].y
            res_str[i][j]+=self.agents[a].image
            a+=1
        return {'str':res_str}
#-------------------------------------------------------------------------------
    def simu(self):
        """simulation """
        print(self)
        i=1
        while self.continue_simu():
            print(i,' :');i+=1
            self.life()
            print(self)
#===============================================================================
if __name__ == "__main__":

#Certaines simulations ne pourront être arrêtée que par la touche Ctrl+C
    
    nom_fichier="./fichiers_version_texte/t_animal_cailloux.txt"
    #nom_fichier="./fichiers_version_texte/t_animal_cailloux_vege_vieillesse.txt"
    #nom_fichier="./fichiers_version_texte/t_breed.txt"
    #nom_fichier="./fichiers_version_texte/t_jdv_36x19.txt"
    nom_fichier="./fichiers_version_texte/t_jdv_base.txt"
    #nom_fichier="./fichiers_version_texte/t_male_femelle.txt"
    #nom_fichier="./fichiers_version_texte/t_trace_seul.txt"
    #nom_fichier="./fichiers_version_texte/t_trace_seul_vieillesse.txt"
    a=TexteWorld(nom_fichier)
