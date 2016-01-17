# ==============================================================================
""" """
# ==============================================================================
__author__  = ""
__version__ = "1.0"
__date__    = "2015-12-12"
# ==============================================================================
from ezTK import *
##import tkinter as tk
from random import randrange,choice
# ------------------------------------------------------------------------------
class Board(Win):
  """a clickable 8x8 board"""
  # ----------------------------------------------------------------------------
  def __init__(self):
    """create the main window and pack the widgets"""
    Win.__init__(self, title='BOARD', opad=5)
    coltext, rowtext, font = 'ABCDEFGH', '12345678', 'Arial 12 bold'
    self.colors = ('#F00','#0F0')
##    colors = ('#F00', '#0F0', '#00F', '#0FF', '#F0F', '#FF0')
    # --------------------------------------------------------------------------
##    self.label = Label(self, font=font, relief=SOLID, border=2, height=2)
    self.button=Button(self, height=1, text="ok", command=self.cb_ok)
##    w = tk.Scrollbar(self,orient=tk.VERTICAL)
##    o = tk.Scrollbar(self,orient=tk.HORIZONTAL)
##    w.pack()
##    c = tk.Canvas(self,yscrollcommand=w.set, xscrollcommand=o.set)
##    w.config(command=c.yview)
##    o.config(command=c.xview)
##    f0 = tk.Frame(c)
##    f0.pack(fill=tk.BOTH)
    # --------------------------------------------------------------------------
    self.cols, self.rows, self.cells = 36, 19, {} # create a dictionnary to store grid cells
    board = Grid(self, side=BOTTOM, cols=self.cols, rows=self.rows, opad=2)
##    for loop in range(self.cols*self.rows):
##      col, row = loop%self.cols, loop//self.rows
##      #bg = colors[randrange(0,len(colors))] # generate background color for current cell
##      bg = self.colors[1] # generate background color for current cell
##      self.cells[row,col] = Button(board, width=1, height=1, bg=bg,
##                            command=lambda cell=(row,col): self.cb_cell(cell))
    for row in range(self.rows):
      for col in range(self.cols):
        #bg = colors[randrange(0,len(colors))] # generate background color for current cell
        bg = self.colors[1] # generate background color for current cell
        self.cells[row,col] = Button(board, width=1, height=1, bg=bg,
                              command=lambda cell=(row,col): self.cb_cell(cell))
        #print(row,col)

    self.t=[["agent %d %d animal dead" % (row+1,col+1) for col in
             range(self.cols)] for row in range(self.rows)]
    # --------------------------------------------------------------------------
    self.loop()
  # ----------------------------------------------------------------------------
  def cb_cell(self, cell):
    """callback function for each cell of the board"""
##    self.label['text'] = "cell = %s   text = %s   color = %s" % (cell,
##                         self.cells[cell]['text'], self.cells[cell]['bg'])
    if self.cells[cell]['bg']==self.colors[1]:
      self.cells[cell]['bg']=self.colors[0]
    else:self.cells[cell]['bg']=self.colors[1]

  def cb_ok(self):
##    for cle in self.cells:print(cle)
    with open("FichierAgentsJDV.txt", "w") as fic:
      for row in range(self.rows):
        for col in range(self.cols):
          if self.cells[(row,col)]['bg']==self.colors[0]:
            self.t[row][col]="agent %d %d animal alive" % (row+1,col+1)
          fic.write(self.t[row][col]+"\n")
# ==============================================================================
if __name__ == "__main__": # testcode for class 'Board'
  Board()
# ==============================================================================
