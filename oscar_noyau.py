# ==============================================================================
"""NOYAU : OSCAR: Outil de Simulation Comportemental par Attraction-Répulsion"""
# ==============================================================================
__author__  = "Pastureau Romain, Rodriguez Charlotte"
__version__ = "2.0"
__date__    = "2015-12-11"
# ------------------------------------------------------------------------------
import pickle
import copy
from ezCLI import *
import random
import pygame
from pygame.locals import *
#===============================================================================
#===============================================================================
class Mineral(object):

    def __init__(self,d):
        assert isinstance(d,dict),"pas un dict"
        self.d=d #status caracteristics from the text
#-------------------------------------------------------------------------------
    @property
    def image(self):
        """icon of the mineral"""
        assert 'image' in self.d,"pas d'image"
        return self.d['image']
    @property
    def var(self):
        """ Informations about initialisation,
            incrementation and decrementation of variables"""
        if 'var' in self.d:return self.d['var']
        else:return{}
    @property
    def status(self):
        if 'status' in self.d:return self.d['status']
        else:return{}
    @property
    def field(self):
        if 'field' in self.d:return self.d['field']
        else:return{}
    @property
    def sensor(self):
        if 'sensor' in self.d:return self.d['sensor']
        else:return{}
#-------------------------------------------------------------------------------
    def __repr__(self):
        return("Mineral(Var=%s, Status=%s, Field=%s, Sensor=%s)"
               %(self.var, self.status, self.field, self.sensor))
#===============================================================================
#===============================================================================
class Vegetal(Mineral):

    @property
    def birth(self):
        if 'birth' in self.d:return self.d['birth']
        else:return{}
    @property
    def field(self):
        if 'field' in self.d:return self.d['field']
        else:return{}
#-------------------------------------------------------------------------------
    def __repr__(self):
        return("Animal(Var=%s, Status=%s, Field=%s, Birth=%s, Sensor=%s)"
               %(self.var, self.status, self.birth, self.field, self.sensor))
#===============================================================================
#===============================================================================
class Animal(Vegetal):

    @property
    def trace(self):
        if 'trace' in self.d:return self.d['trace']
        else:return{}
#-------------------------------------------------------------------------------
    def __repr__(self):
        return("Animal(Status=%s, Birth=%s, Trace=%s, Field=%s, Sensor=%s)"
               %(self.status, self.birth, self.trace, self.field, self.sensor))
#===============================================================================
#===============================================================================
class Agent(object):

    def __init__(self,world,x,y,status,sommet,v={}):
        assert isinstance(world,World),"pas un World"
        assert isinstance(x,int),"pas un int"
        assert isinstance(y,int),"pas un int"
        assert isinstance(status,str),"pas un str"
        assert isinstance(sommet,(Mineral,Vegetal,Animal)),"pas un ordre"
        assert isinstance(v,dict),"pas un dict"
        self.world=world
        self.x=x
        self.y=y
        self.status=status
        self.sommet=sommet #graphe entry
        self.v=v #agent's variables
        self.trace=False
#-------------------------------------------------------------------------------
    def __lt__(self,other):
        """        
        returns True if self<other, False otherwise
        When two agents are in the same square,
        calculates the amount of field each of them absorbs
        self<other if other absorbs more field than self
        """
        
        assert isinstance(other,Agent),"pas un Agent"
        
        self_val=0
        other_val=0

        for cle in self.sommet.sensor:
            if cle in other.sommet.field:
                self_val+=other.v[cle]
        #if no cle ==> self_val==0
                
        for cle in other.sommet.sensor:
            if cle in self.sommet.field:
                other_val+=self.v[cle]
        #if no cle ==> other_val==0
                
        if self_val>other_val:return False
        elif self_val<other_val:return True
        else:return not random.randint(0,1)#in case of equality, hazard chooses
#-------------------------------------------------------------------------------
    def breed(self):
        """ if the status contains birth
        we look if the agent can breed
        if it can then it gives birth in the case containing
        the bigger amount of positive field"""

        if self.sommet.birth!={}:
            for elem in self.sommet.birth:

                #value of the variable
                if elem[0] in self.sommet.sensor:#something the agent must detect
                    val=self.radar(elem[0])
                else:#or a basic variable
                    val=self.v[elem[0]]
                    
                if eval(str(val)+''.join(elem[1:3])):#if it's ok to breed
                    status=elem[3]

                    case=self.move(False)#better square
                    if case==None:return 0
                    x,y=self.move(False)

                    ordre=type(self.sommet).__name__.lower()

                    #new agent's variables:
                    v={}
                    for cle in self.world.graphes[ordre][status].var:
                        v[cle]=self.world.graphes[ordre][status].var[cle]['init']
                        
                    self.world.agents.append(Agent(self.world,x,y, status,
                                     self.world.graphes[ordre][status],
                                     copy.deepcopy(v)))
#-------------------------------------------------------------------------------
    def move(self,move=True):
        """if move==True ==> moves the animal to the most attractive juxtaposed
        square of the world
        Else ==> returns the coordinates of the most attractive juxtaposed
        square of the world"""
        res={}
        if self.sommet.sensor=={}:#the agent can't detect anything
            for i in range(self.x-1,self.x+2):
                    for j in range(self.y-1,self.y+2):
                        if (i!=self.x or j!=self.y) and self.world.in_world(i,j) :
                            #self.board represents the world states at time t-1,
                            #here we are constructing time t.
                            #The agent can't go to a square containing another
                            #agent at time t-1.
                            if self.world.board[i][j]==[]:
                                res[i,j]=0
                            #it will move to a square, through hazard
        else:
            for cle in self.sommet.sensor:#fields the agent can detect
                tab=self.world.champ(cle,self.x,self.y)#matrix containing these fields
                #we only look around the agent:
                for i in range(self.x-1,self.x+2):
                    for j in range(self.y-1,self.y+2):
                        if (i!=self.x or j!=self.y) and self.world.in_world(i,j) :
                            #self.board represents the world states at time t-1,
                            #here we are constructing time t.
                            #The agent can't go to a square containing another
                            #agent at time t-1.
                            if self.world.board[i][j]==[]:
                                if (i,j) not in res:res[i,j]=0
                                res[i,j]+=tab[i][j]
        if res!={}:#if a square is free
            tri=sorted(res,key=res.get)
            list_better=[cle for cle in res if res[cle]==res[tri[len(tri)-1]]]
            better=list_better[random.randint(0,len(list_better)-1)]
            if move:#if the agent is to move

                #trace:
                for cle in self.sommet.trace:
                    if cle[0] in self.sommet.sensor:#shouldn't go there
                        val=self.radar(cle[0])
                    else:
                        val=self.v[cle[0]]
                    change=eval(str(val)+''.join(cle[1:3]))
                    if change:#if have a trace status

                        ordre=type(self.sommet).__name__.lower()
                        status=cle[3]

                        #new agent's trace variables:
                        v={}
                        for cle in self.world.graphes[ordre][status].var:
                            v[cle]=self.world.graphes[ordre][status].var[cle]['init']
                        a=Agent(self.world,self.x,self.y,status,
                                self.world.graphes[ordre][status],
                                copy.deepcopy(v))
                        a.status=status
                        a.trace=True
                        self.world.agents.append(a)

                #move:       
                self.x,self.y=better
                
            else:return better
#-------------------------------------------------------------------------------
    def change_status(self):
        """ verifies if the agent must change it's status
        if it's the cases then changes the status"""
        n=len(self.sommet.status)
        i=0
        while i<n:#for each status
            if self.sommet.status[i][0] in self.sommet.sensor:
                val=self.radar(self.sommet.status[i][0])
            else:
                val=self.v[self.sommet.status[i][0]]
            change=eval(str(val)+''.join(self.sommet.status[i][1:3]))
            if change:#if must change status
                self.status=self.sommet.status[i][3]
                if self.status=='DEATH':
                    self.world.agents.remove(self)
                else:
                    ordre=type(self.sommet).__name__.lower()
                    self.sommet=self.world.graphes[ordre][self.status]
                    self.maj_variables()
                break
            i+=1
#-------------------------------------------------------------------------------
    def live(self):
        """one 'time' of an agent's life"""

        #incremantation or decrementation of variables
        for cle in self.sommet.var:
            self.v[cle]+=self.sommet.var[cle]['step']
        if not self.trace:     
            #breed and move
            if isinstance(self.sommet,(Animal,Vegetal)):self.breed();
            if isinstance(self.sommet,Animal):self.move()
            
        #status change:
        self.change_status()
#-------------------------------------------------------------------------------
    def radar(self,nom_champ):
        """
        detects field nom_champ around the agent
        returns the sum of this field
        """
        tab=self.world.champ(nom_champ,self.x,self.y)
        res=0
        vision=self.sommet.sensor[nom_champ]
        for i in range(self.x-vision,self.x+vision+1):
            for j in range(self.y-vision,self.y+vision+1):
                if self.world.in_world(i,j):
                    res+=tab[i][j]
        return res
#-------------------------------------------------------------------------------
    def maj_variables(self):
        """
        variables update with new status
        only for variables present in the new status
        other variables stay untouched
        """
        for cle in self.sommet.var:
            self.v[cle]=self.sommet.var[cle]['init']
#-------------------------------------------------------------------------------
    @property
    def image(self):
        """ agent's icon """
        return self.sommet.image
#-------------------------------------------------------------------------------
    def __repr__(self):
        return "Agent((%d,%d), stat=%s, som=%s, v=%s)\n"%(self.x,
                                               self.y,
                                               self.status,
                                               self.sommet,
                                               self.v)
#===============================================================================
#===============================================================================
class World(object):

    def __init__(self,nom_fichier):
        
        self.d=self.read_fic(nom_fichier)#data of the text file

        #graphes
        self.graphes=self.creation_graphe(self.d['data'],self.d['noms_status'])

        #agents
        self.agents=self.creation_agents(self.d['agents'])#updated (time t)
        self.oldagents=copy.deepcopy(self.agents)#save of time t-1

        #simulation
        self.simu()
        
#-------------------------------------------------------------------------------
    def conflict(self):
        """ if there are several agents in the same square
        only one of them keep existing:
        the one detecting the bigger amount of field from the others"""
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                elem=[agent for agent in self.newboard[i][j]
                      if agent.status!='STATUS']
                t=len(elem)
                if t>1:
                    l=sorted(elem)
                    for agent in l[0:t-1]:
                        self.agents.remove(agent)                                   
#-------------------------------------------------------------------------------
    def life(self):
        """one more time of life for each agent"""
        for a in self.agents:
            a.live()#one more time of life for a
        del self.oldagents
        self.oldagents=copy.deepcopy(self.agents)#update of oldagents
        self.conflict()#resolve conflicts
#-------------------------------------------------------------------------------
    def simu(self):
        """ simulation """
        while self.continue_simu():
            self.life()
#-------------------------------------------------------------------------------
    def in_world(self,a,b):
        """ returns True if the (a,bà square is in the world ,
        False otherwise"""
        return (a<self.size[0] and a>=0 and b>=0 and b<self.size[1])
#-------------------------------------------------------------------------------
    def champ(self,nom_champ,x,y):
        """
        Returns an interger matrix corresponding to the values of the
        field nom_champ emmitted by each agent exept the one in square (x,y)
        """
        assert isinstance(nom_champ,str),"pas un str"
        assert isinstance(x,int),"pas un int"
        assert isinstance(y,int),"pas un int"
        res=[[0 for j in range(self.size[1])]for i in range(self.size[0])]
        for agent in self.oldagents:
            if agent.x!=x or agent.y!=y:
                if nom_champ in agent.sommet.field:
                    portee=agent.v[nom_champ]#max value (pos or neg)
                    portee_depart=portee
                    res[agent.x][agent.y]+=portee
                    if portee<0 and agent.sommet.field[nom_champ]>0:sign="+"
                    elif portee<0 and agent.sommet.field[nom_champ]<0:sign="-"
                    elif portee>0 and agent.sommet.field[nom_champ]<0:sign="+"
                    else:sign="-"
                    portee=eval("portee"+sign+"agent.sommet.field[nom_champ]")

                    e=1 #extent of the field
                    while (portee*portee_depart)>0:
                        i1=agent.x-e;i2=agent.x+e
                        for j in range(agent.y-e,agent.y+e+1):
                            if self.in_world(i1,j):res[i1][j]+=portee
                            if self.in_world(i2,j):res[i2][j]+=portee
                        j1=agent.y-e;j2=agent.y+e
                        for i in range(agent.x-e+1,agent.x+e+1-1):
                            if self.in_world(i,j1):res[i][j1]+=portee
                            if self.in_world(i,j2):res[i][j2]+=portee                        
                        e+=1
                        portee=eval("portee"+sign+"agent.sommet.field[nom_champ]")
        return(res)
#-------------------------------------------------------------------------------
    @property
    def newboard(self):
        """ Matrix containing agents at time t (updated) """
        l=len(self.agents)
        newagents=[[[] for j in range(self.size[1])]
             for i in range(self.size[0])]
        b=0
        while b<l:
            i=self.agents[b].x
            j=self.agents[b].y
            newagents[i][j].append(self.agents[b])
            b+=1
        return newagents
#-------------------------------------------------------------------------------
    @property
    def board(self):
        """ Matrix containing agents at time t-1 (save) """
        l=len(self.oldagents)
        res_oldagents=[[[] for j in range(self.size[1])]
             for i in range(self.size[0])]
        b=0
        while b<l:
            i=self.oldagents[b].x
            j=self.oldagents[b].y
            res_oldagents[i][j].append(self.oldagents[b])
            b+=1
        return res_oldagents
#-------------------------------------------------------------------------------
    @property
    def size(self):
        """
        Returns a tuple containing the world's size
        """
        assert (len(self.d['world'])<4 and len(self.d['world'])>1),"world pas 2 caracteristiques au moins"
        return tuple(self.d['world'][0:2])
#-------------------------------------------------------------------------------
    @property
    def image(self):
        assert len(self.d['world'])==3,"world pas 3 caracteristiques"
        return self.d['world'][2]
#-------------------------------------------------------------------------------
    def continue_simu(self):
        """the simulation keep going as long as at least one agent is alive"""
        return len(self.agents)!=0
#-------------------------------------------------------------------------------
    def elt_vide(self,l):
        """
        returns true if l doesn't contains an empty string, False other wise
        """
        assert isinstance(l,list),"pas une liste"
        t=True
        for elem in l:
            if elem=='':t=False
        return t
#-------------------------------------------------------------------------------
    def read_fic(self,nom_fic):
        """
        Reads the file nom_fic and stores the informations in dict, tuple or
        list. Returns a dict containing theses dict tuple and list.
        
        --> d={'mineral':{'nom_status1':{],'nom_status2':{},...},
        'vegetal':{'nom_status1':{},...},'animal':{'nom_status1':{},...}}
        > Each {} above is : {'var':{},'status':{},'birth':{},
        'trace':{},'field:{},'sensor':{}}
        > The fields 'var', 'status', etc are only created if needed

        --> ld={d={'mineral':{'nom_status1','nom_status2',...},
        'vegetal':{'nom_status1',...},'animal':{'nom_status1',...}}

        --> a=[[info_agent1],[infos_agent2],...]
        [info_agent] contains str or int

        -->w=(size and char representation of the world)
        """
        assert isinstance(nom_fic,str),"pas un str"
        
        d={}
        ld={}
        a=[]
        signes=('<','<=','>','>=','==','!=')
        newstatus=False
        newstatus2=False
        num=0
        try:
            with open(nom_fic,'r') as fic :
                for l in fic:
                    num+=1
                    if l[-1:]=='\n':l=l[:-1] #removes \n at the end of a line
                    l.strip()
                    if l[-1:]==' ':l=l[:-1]
                    
                    #reads the world line
                    if l.startswith('world'):
                        w=[]
                        w=l[6:].split(' ')
                        assert len(w)==3,"manque information(s) sur world"
                        w[0]=int(w[0]);w[1]=int(w[1])
                        w=tuple(w)

                    #do we begin a new status:
                    if l.startswith('animal'):
                        newstatus=True;s=tuple(l.split(' '));newstatus2=True
                        assert len(s)==3,"probleme info status : "+l
                    elif l.startswith('vegetal'):
                        newstatus=True;s=tuple(l.split(' '));newstatus2=True
                        assert len(s)==3,"probleme info status : "+l
                    elif l.startswith('mineral'):
                        newstatus=True;s=tuple(l.split(' '));newstatus2=True
                        assert len(s)==3,"probleme info status : "+l
                        
                    #dict containing the status's names, grouped by order
                    if newstatus2==True:
                        if s[0] not in ld:ld[s[0]]=[]
                        assert s[1] not in ld[s[0]],"duplication du status "+s[1]
                        ld[s[0]].append(s[1])
                        newstatus2=False

                    #dict containing status (with status's data)
                    if newstatus:
                        if s[0] not in d:d[s[0]]={}
                        if s[1] not in d[s[0]]:
                            d[s[0]][s[1]]={}
                            d[s[0]][s[1]]['image']=s[2]
                        if l.startswith('var'):
                            l=l[4:]
                            if 'var' not in d[s[0]][s[1]]:
                                d[s[0]][s[1]]['var']={}
                            ligne=l.split(' ')
                            assert (ligne[0] not in
                                    d[s[0]][s[1]]['var']),"duplication de variable ligne "+str(num)+" : "+ligne[0]
                            assert len(ligne)==3,"probleme info var ligne "+str(num)+" : "+l
                            assert self.elt_vide(ligne),"trop d'espaces ligne "+str(num)+" : "+l
                            d[s[0]][s[1]]['var'][ligne[0]]={}
                            d[s[0]][s[1]]['var'][ligne[0]]['init']=float(ligne[1])
                            d[s[0]][s[1]]['var'][ligne[0]]['step']=float(ligne[2])
                        elif l.startswith('status'):
                            l=l[7:]
                            ligne=l.split(' ')
                            assert len(ligne)==4,"probleme info status ligne "+str(num)+" : "+l
                            assert ligne[1] in signes,"pb signe status: "+l
                            assert self.elt_vide(ligne),"trop d'espaces ligne "+str(num)+": "+l
                            if 'status' not in d[s[0]][s[1]]:
                                d[s[0]][s[1]]['status']=[]
                                d[s[0]][s[1]]['status'].append(ligne)
                            else:d[s[0]][s[1]]['status'].append(ligne)
                        elif l.startswith('birth'):
                            l=l[6:];
                            ligne=l.split(' ')
                            assert len(ligne)==4,"probleme info birth ligne "+str(num)+" : "+l
                            assert ligne[1] in signes,"pb signe birth ligne "+str(num)+": "+l
                            assert self.elt_vide(ligne),"trop d'espaces ligne "+str(num)+": "+l
                            if 'birth' not in d[s[0]][s[1]]:
                                d[s[0]][s[1]]['birth']=[]
                                d[s[0]][s[1]]['birth'].append(ligne)
                            else:d[s[0]][s[1]]['birth'].append(ligne)
                        elif l.startswith('trace'):
                            l=l[6:]
                            ligne=l.split(' ')
                            assert len(ligne)==4,"probleme info trace ligne "+str(num)+" : "+l
                            assert ligne[1] in signes,"pb signe trace ligne "+str(num)+" : "+l
                            assert self.elt_vide(ligne),"trop d'espaces ligne "+str(num)+": "+l
                            if 'trace' not in d[s[0]][s[1]]:
                                d[s[0]][s[1]]['trace']=[]
                                d[s[0]][s[1]]['trace'].append(ligne)
                            else:d[s[0]][s[1]]['trace'].append(ligne)
                        elif l.startswith('field'):
                            l=l[6:]
                            ligne=l.split(' ')
                            assert len(ligne)==2,"probleme info field ligne "+str(num)+" : "+l
                            assert self.elt_vide(ligne),"trop d'espaces ligne "+str(num)+": "+l
                            if 'field' not in d[s[0]][s[1]]:
                                d[s[0]][s[1]]['field']={}
                            d[s[0]][s[1]]['field'][ligne[0]]=int(ligne[1])
                        elif l.startswith('sensor'):
                            l=l[7:]
                            ligne=l.split(' ')
                            assert len(ligne)==2,"probleme info sensor ligne "+str(num)+" : "+l
                            assert self.elt_vide(ligne),"trop d'espaces ligne "+str(num)+": "+l
                            if 'sensor' not in d[s[0]][s[1]]:
                                d[s[0]][s[1]]['sensor']={}
                            d[s[0]][s[1]]['sensor'][ligne[0]]=int(ligne[1])
                            
                    if l=='':new_status=False;i=0 #do we end the status

                    #'agents reading'
                    if l.startswith('agent'):
                        l=l[6:]
                        tamp=l.split(' ')
                        tamp[0]=int(tamp[0])
                        tamp[1]=int(tamp[1])
                        a.append(tuple(tamp))
        except IOError:
            print("Erreur, le fichier n'a pas pu etre ouvert")
        assert 'w' in locals(),"pas d'infos sur world"
        return {'data':d,'noms_status':ld,'agents':a,'world':w}
#-------------------------------------------------------------------------------
    def creation_graphe(self,d,ld):
        """
        Creates a dict containing instances of each status
        --> keys are orders status
        --> values are instances of Animal, Vegetal or Mineral classes
        """
        ordres=['animal','vegetal','mineral']
        res={}
        for elem in ordres:
            if elem in ld:      
                i=0
                n=len(ld[elem])
                while i<n:
                    if elem not in res:res[elem]={}
                    res[elem][ld[elem][i]]=eval("%s(%s)"%(elem.capitalize(),d[elem][ld[elem][i]]))
                    i+=1
        return res
#-------------------------------------------------------------------------------
    def creation_agents(self,a):
        """
        Creates a list containing agents
        """
        assert isinstance(a,list),"pas une liste"
        n=len(a)
        i=0
        res=[]

        while i<n:
            
            #agent's variables
            v={}
            for cle in self.graphes[a[i][2]][a[i][3]].var:
                v[cle]=self.graphes[a[i][2]][a[i][3]].var[cle]['init']
                
            res.append(Agent(self,a[i][0]-1,a[i][1]-1, a[i][3],
                             self.graphes[a[i][2]][a[i][3]],
                             copy.deepcopy(v)))
            i+=1
        return res
#===============================================================================
