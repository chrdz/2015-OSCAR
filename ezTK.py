# ==============================================================================
"""ezTK : a toolbox for easy development of Tk-based user-interface"""
# ==============================================================================
__author__  = "Christophe Schlick"
__version__ = "1.0"
__date__    = "2015-07-01"
# ==============================================================================
import tkinter as tk
from tkinter.constants import *
# ------------------------------------------------------------------------------
PhotoImage = tk.PhotoImage
# ------------------------------------------------------------------------------
class Win(tk.Tk):
  """..."""
  # ----------------------------------------------------------------------------
  def __init__(self, title=None, font=None, side=None, bg=None, fg=None,
               opad=None, ipad=None):
    self.font, self.side = font if font else 'Arial 12', side if side else TOP
    self.bg, self.fg, self.opad, self.ipad = bg, fg, opad, ipad
    self.frame = self # create a dummy sub-frame for compatibility with 'Grid'
    tk.Tk.__init__(self); self.title(title)
  # ---------------------------------------------------------------------------- 
  def loop(self):
    self.update(); # wait for packer to display all widgets in window
    self.minsize(self.winfo_width(), self.winfo_height()); self.mainloop()
  # ----------------------------------------------------------------------------
  def pack(self, widget, grow):
    widget.pack(fill=BOTH, expand=grow, side=self.side, padx=self.opad,
                pady=self.opad, ipadx=self.ipad, ipady=self.ipad)
# ------------------------------------------------------------------------------
class Frame(tk.Frame):
  """..."""
  # ----------------------------------------------------------------------------
  def __init__(self, master, grow=True, font=None, side=None,
               bg=None, fg=None, opad=None, ipad=None, **keys):
    sm = lambda slave, master: master if slave is None else slave
    self.font = sm(font, master.font)
    self.bg, self.opad = sm(bg, master.bg), sm(opad, master.opad)
    self.fg, self.ipad = sm(fg, master.fg), sm(ipad, master.ipad)
    self.side = sm(side, LEFT if master.side in (TOP,BOTTOM) else TOP) 
    keys['bg'] = self.bg
    tk.Frame.__init__(self, master, **keys)
    tk.Frame.pack(self, side=master.side, ipadx=master.ipad, ipady=master.ipad,
                  fill=BOTH, expand=grow, padx=master.opad, pady=master.opad)
    self.frame = self # create a dummy sub-frame for compatibility with 'Grid'
  # ----------------------------------------------------------------------------
  def pack(self, widget, grow):
    widget.pack(fill=BOTH, expand=grow, side=self.side, padx=self.opad,
                pady=self.opad, ipadx=self.ipad, ipady=self.ipad)
# ------------------------------------------------------------------------------
class Grid(tk.Frame):
  """..."""
  # ----------------------------------------------------------------------------
  def __init__(self, master, grow=True, rows=1, cols=1, font=None, side=None,
               bg=None, fg=None, opad=None, ipad=None, **keys):
    sm = lambda slave, master: master if slave is None else slave
    self.font, self.side = sm(font, master.font), TOP if side is None else side
    self.bg, self.opad = sm(bg, master.bg), sm(opad, master.opad)
    self.fg, self.ipad = sm(fg, master.fg), sm(ipad, master.ipad)
    self.rows, self.cols, self.index = rows, cols, 0; keys['bg'] = self.bg
    tk.Frame.__init__(self, master, **keys)
    tk.Frame.pack(self, side=master.side, ipadx=master.ipad, ipady=master.ipad,
                  fill=BOTH, expand=grow, padx=master.opad, pady=master.opad)
    self.frame = Frame(self, True) # create sub-frame for first row or col
  # ----------------------------------------------------------------------------
  def pack(self, widget, grow):
    # create inner Frame for first col in row
    widget.pack(fill=BOTH, expand=grow, side=self.frame.side, padx=self.opad,
                pady=self.opad, ipadx=self.ipad, ipady=self.ipad)
    self.index += 1
    if self.side in (TOP,BOTTOM): # insert order: cols first, rows second
      if not self.index%self.cols and self.index//self.cols < self.rows:
        self.frame = Frame(self, True) # create sub-frame for next row
    else: # insert order: rows first, cols second
      if not self.index%self.rows and self.index//self.rows < self.cols:
        self.frame = Frame(self, True) # create sub-frame for next col
# ------------------------------------------------------------------------------
class Label(tk.Label):
  """..."""
  # ----------------------------------------------------------------------------
  def __init__(self, master, grow=True, **keys):
    keys['font'] = keys.get('font', master.font)
    keys['bg'], keys['fg'] = keys.get('bg',master.bg), keys.get('fg',master.fg)
    tk.Label.__init__(self, master.frame, **keys)
    master.pack(self, grow)
# ------------------------------------------------------------------------------
class Button(tk.Button):
  """..."""
  # ----------------------------------------------------------------------------
  def __init__(self, master, grow=True, **keys):
    keys['font'] = keys.get('font',master.font)
    keys['bg'], keys['fg'] = keys.get('bg',master.bg), keys.get('fg',master.fg)
    tk.Button.__init__(self, master.frame, **keys)
    master.pack(self, grow)
# ------------------------------------------------------------------------------
class Canvas(tk.Canvas):
  """..."""
  # ----------------------------------------------------------------------------
  def __init__(self, master, grow=True, **keys):
    keys['bg'], keys['fg'] = keys.get('bg',master.bg), keys.get('fg',master.fg)
    keys['border'] = keys.get('border',0) - 2
    tk.Canvas.__init__(self, master.frame, **keys)
    master.pack(self, grow)
# ------------------------------------------------------------------------------
class Scale(tk.Scale):
  """..."""
  # ----------------------------------------------------------------------------
  def __init__(self, master, grow=True, scale=None, **keys):
    start, stop, step = 0, 100, 1
    get = lambda seq,n,val: seq[n] if seq[n:n+1] else val
    if isinstance(scale, (int, float)): stop = scale # only 'stop' value
    elif isinstance(scale, (tuple, list)): # get 'start,stop,step' values
      start,stop,step = get(scale,0,start), get(scale,1,stop), get(scale,2,step)
    keys['font'] = keys.get('font',master.font)
    keys['bg'], keys['fg'] = keys.get('bg',master.bg), keys.get('fg',master.fg)
    keys['orient'] = VERTICAL if keys.get('orient', None) == NS else HORIZONTAL 
    keys['from_'], keys['to'], keys['resolution'] = start, stop, step 
    tk.Scale.__init__(self, master.frame, **keys)
    master.pack(self, grow)
  # ----------------------------------------------------------------------------
  def __call__(self, value=None):
    if value is None: return self.get() # get current value
    else: self.set(value) # set new value
# ------------------------------------------------------------------------------
class Entry(tk.Entry):
  """..."""
  # ----------------------------------------------------------------------------
  def __init__(self, master, grow=True, **keys):
    keys['font'] = keys.get('font',master.font)
    keys['bg'], keys['fg'] = keys.get('bg',master.bg), keys.get('fg',master.fg)
    command = keys.get('command',None); del keys['command']
    tk.Entry.__init__(self, master.frame, **keys)
    if command: self.bind('<Return>', lambda event, *args: command(*args))
    master.pack(self, grow)
  # ----------------------------------------------------------------------------
  def __call__(self, value=None):
    if value is None: return self.get() # get current value
    else: self.delete(0,END); self.insert(0,value) # set new value
# ------------------------------------------------------------------------------
class Listbox(tk.Listbox):
  """..."""
  # ----------------------------------------------------------------------------
  def __init__(self, master, grow=True, scroll=False, **keys):
    keys['font'] = keys.get('font',master.font)
    keys['activestyle'] = keys.get('activestyle',NONE)
    keys['bg'], keys['fg'] = keys.get('bg',master.bg), keys.get('fg',master.fg)
    if scroll:
      self.frame = tk.Frame(master, bg=keys['bg'])
      self.frame.pack(fill=BOTH, ipadx=master.ipad, ipady=master.ipad,
        padx=master.opad, pady=master.opad, expand=grow, side=master.side)
      tk.Listbox.__init__(self, self.frame, **keys)
      self.xscroll = tk.Scrollbar(self.frame, orient=HORIZONTAL,
        command=self.xview); self.xscroll.pack(side=BOTTOM, fill=BOTH)
      self.yscroll = tk.Scrollbar(self.frame, orient=VERTICAL,
        command=self.yview); self.yscroll.pack(side=RIGHT, fill=BOTH)
      self.config(xscrollcommand=self.xscroll.set)
      self.config(yscrollcommand=self.yscroll.set)
      self.pack(side=LEFT, fill=BOTH, expand=YES)
    else:
      tk.Listbox.__init__(self, master.frame, **keys)
      master.pack(self, grow)
# ==============================================================================
if __name__ == '__main__':
  from ezTKdemo import ezTKdemo
  ezTKdemo()
# ==============================================================================
