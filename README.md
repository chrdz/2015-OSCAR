# 2015-OSCAR
## Multi-agent system OSCAR (OOP), 2015.

Mutli-agent system where the so-called "world" is a 2d grid in which different types of "agents" evolve (some may move, reproduce, fight, attract or repulse the other and so on). 
The user provides the initial state of the world via a text file, and the OSCAR program will give the evolution of the population of agents. 

In the code: there is a separation between the kernel where the different world and agent class, and with their respective methods, are implemented, and the text interface and graphical interface.

To try out the code: run either the file oscar_texte.py (text user interface) or oscar_graphique.py (graphical user interface).

The graphical interface requires to have the package "pygame" installed.