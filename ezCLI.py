# ==============================================================================
"""ezCLI : a toolbox for easy development of Command Line Interface"""
# ==============================================================================
__author__  = "Christophe Schlick"
__version__ = "1.0"
__date__    = "2015-07-01"
# ==============================================================================
__all__ = ['convert', 'parse', 'inject', 'grid', 'pause', 'userloop', 'timer',
           'inspect', 'testcode', 'read_txt', 'write_txt', 'read_blk',
           'write_blk','read_csv','write_csv','read_ini','write_ini']
# ==============================================================================
# String manipulation tools : convert, parse, inject, grid
# ==============================================================================
def convert(string):
  """convert each literal expression in 'string' into its canonical data type

  - 'string' may contain an arbitrary sequence of comma-separated expressions
  - any non-convertible literal expression is simply returned as a string
  """
  try: string = eval(string) # check if 'eval' can be applied on 'string'
  except Exception: pass # keep 'string' unchanged if 'eval' fails
  return string
# ------------------------------------------------------------------------------
def parse(string, default='', vsep=' ', nsep='='):
  """parse 'string' and return a tuple of values or a dictionary of named values

  string:str = input string to be parsed into values and/or named values
  default:str = optional string storing default values and named values
  vsep:str = separator string used between values 
  nsep:str = separator string used between name and value

  Note: almost arbitrary strings may be used for vsep and nsep, except
  that they cannot start with any of the 8 delimiters: ' " ( ) [ ] { }
  """
  # ------------------------------------------------------------------------------
  def splitstring(string, vsep, nsep):
    """split 'string' into a dictionary of values and/or named values"""
    # algorithm: the string is parsed with a 3-state stack machine, where:
    # - state 0 = normal code, state 1 = '' string, state 2 = "" string
    # - stack memorizes paired brackets (round, square or curly brackets)
    # during the char-by-char parsing, any separator that neither appears in
    # strings nor in brackets is replaced by a standard control character:
    # - 'vsep' is replaced by ASCII/Unicode RS (Record Separator) = chr(30)
    # - 'nsep' is replaced by ASCII/Unicode US (Unit Separator) = chr(31)
    stack, vlen, nlen, enter, leave = [], len(vsep), len(nsep), '([{', ')]}'
    state, vmod, nmod, code = 0, chr(30), chr(31), list(string)
    for n, c in enumerate(code):
      if c == "'" and state in (0,1): state = 1-state # enter/leave '' string
      elif c == '"' and state in (0,2): state = 2-state # enter/leave "" string
      elif c in enter and not state: stack.append(c) # enter bracket zone
      elif c in leave and not state: # leave bracket zone
        if leave.find(c) == enter.find(stack[-1]): stack.pop() # bracket match
      elif string[n:n+vlen] == vsep and not state and not stack: # found vsep
        code[n:n+vlen] = [vmod]*vlen # replace vsep by vmod (RS control char) 
      elif string[n:n+nlen] == nsep and not state and not stack: # found nsep
        code[n:n+nlen] = [nmod]*nlen # replace nsep by nmod (US control char)
    # split code into name/value items, using RS and US delimiters, then
    # apply 'strip' and 'convert' to all items, and store in 'dic'
    dic, items = {'':[]}, [item for item in ''.join(code).split(vmod) if item]
    for item in items: # convert all items and insert in dictionary
      if not item.count(nmod): dic[''].append(convert(item.strip())); continue
      *names, val = item.split(nmod) # multiple names assignment is allowed
      names, val = [name.strip() for name in names if name.strip()], val.strip()
      for name in names: dic[convert(name)] = convert(val)
    if not dic['']: del dic[''] # remove key for non-named values if empty
    else: dic[''] = tuple(dic['']) # store non-named values as tuple
    return dic # that's all folks!
  # ------------------------------------------------------------------------------
  dic = splitstring(string.strip(), vsep, nsep)
  if default: # a string or a dictionary of default values is provided
    if isinstance(default,str): default = splitstring(default.strip(),vsep,nsep)
    dic = dict(list(default.items()) + list(dic.items())) # merge dictionaries
    diff = dic.keys() - default.keys() # check differences between dictionaries
    if '' in diff: raise ValueError("only named values are allowed here")
    elif len(diff): raise NameError("unallowed names %r" % ','.join(diff))
  return dic[''] if dic.keys() == {''} else dic # either tuple or dict
# ------------------------------------------------------------------------------
def inject(string, cells, pattern='###', trunc=True):
  """replace all instances of 'pattern' in 'string' by items of 'cells'

  string:str = arbitrary string including several instances of 'pattern'
  cells:list = list of values that are sequentially injected in 'string' 
  pattern:str = string defining replacement pattern for injection
  trunc:bool = truncate (or not) cell content to the length of 'pattern'
  """
  trunc = slice(len(pattern) if trunc else None)
  for cell in cells: string = string.replace(pattern, str(cell)[trunc], 1)
  return string
# ------------------------------------------------------------------------------
def grid(matrix, inner=True, outer=True, label=False, size=None):
  """return a string containing a 2D grid representation for 'matrix'

  matrix:list|tuple = 2D matrix containing arbitrary data in cells
  inner:bool = draw (or not) inner lines of the grid
  outer:bool = draw (or not) outer lines of the grid
  label:bool = add (or not) labels (letters for cols, digits for rows)
  size:int = horizontal size for each cell (default = compute best size)

  Note: the width of each cell is truncated to 'size' when provided
  """
  rows, cols = len(matrix), max(map(len,matrix)) # get number of rows and cols
  # first create a rectangular matrix by adding empty strings in missing cells
  matrix = [line[col] if line[col:col+1] else ''
            for line in matrix for col in range(cols)]
  # define 'width' as the length of the longest value stored in matrix
  width = max(len(str(val)) for val in matrix)
  if size is None: size = width # default size when no user-provided size
  elif width > size: width = size # all cells will be truncated to 'size'
  # convert each cell to a centered string of length 'size'
  matrix = [str(val)[:size].center(size) if not isinstance(val,(int,float))
            else str(val)[:size].rjust(width).center(size) for val in matrix]
  # create matrix frame by combining a set of frame drawing characters
  frames = ['    \n, #  \n,    \n,    \n', '  │ \n, #│ \n,──┼─\n,  │ \n',
            '┌──┐\n,│# │\n,│  │\n,└──┘\n', '┌─┬┐\n,│#││\n,├─┼┤\n,└─┴┘\n']
  frame = frames[2*outer+inner].split(',') # select correct drawing set
  # repeat frame drawing characters to get correct number of rows and cols 
  repeat = lambda lst,p,q: lst[0]+(lst[1]*p+lst[2])*(q-1)+lst[1]*p+lst[3]+lst[4] 
  frame = repeat([repeat(frame, size, cols) for frame in frame]+[''], 1, rows)
  frame = inject(frame[:-1], matrix, '#'*size).split('\n') # inject matrix
  if label: # add letters for col labels and digits for row labels
    clabel = ' ABCDEFGHIJKLMNOQRSTUVWXYZ'
    clabel = [(a+b).strip() for a in clabel for b in clabel[1:]][:cols]
    rlabel = [str(a) if a and b else ' ' for a in range(rows+1) for b in (1,0)]
    rlabel = ["%*s " % (len(str(rows)), r) for r in rlabel]
    # insert col labels at the top of grid and row labels at the left 
    frame[0:0] = [' ' + ' '.join(c.center(size) for c in clabel)]
    frame = [a+b for a,b in zip(rlabel, frame)]
  return '\n'.join(frame)

# ==============================================================================
# Command line tools : pause, userloop
# ==============================================================================
def pause(*args, sep=' ', end='\n', ask='', prompt='', ok=' '):
  """'pause' is similar to 'print', but offers pause for user confirmation

  args:tuple = tuple of objects to be displayed sequentially on screen
  sep:str = string inserted between each object in 'args'
  end:str = string inserted after the last object, before the prompt
  ask:object = special value in 'args' that triggers prompt for user
  prompt:str = string displayed each time the 'ask' value is found
  ok:str|set = (set of) string(s) corresponding to allowed answers for
    the user input. All other strings are considered as invalid answers

  The function loops over the arguments in 'args' and displays them on
  screen, as the standard 'print' function. However, each time the
  special value stored in 'ask' is encountered, the 'prompt' string is
  displayed and the function pauses and waits for user confirmation.
  
  If the user enters an empty string (i.e. just hit the <ENTER> key),
  the display loop continues with the next object. If the user enters
  another string, the display loop is interrupted if this string is
  present in the 'ok' set. The prompt is repeated until the user enters
  either a string from 'ok' or an empty string. The function returns
  the string entered by the user or None if no interruption has occured
"""
  if not prompt: # default prompt string
    prompt = ' <ENTER> TO CONTINUE, <SPACE> TO BREAK '.center(79,'─')
  if not isinstance(ok,set): ok = {str(ok)} # force 'ok' to become a set
  ok = {item.lower() for item in ok} # lowercase all strings from 'ok'
  stops, start = [n for n,arg in enumerate(args+(ask,)) if arg == ask], None
  for stop in stops: # iterate over slices from 'args'
    print(*args[slice(start,stop)], sep=sep, end=end); start = stop+1
    while(True): # loop until correct user input
      answer = input(prompt).lower() # also lowercase user input
      if answer in ok: return answer # stop loop and return user answer 
      if not answer: break # empty answer means continue display loop 
# ------------------------------------------------------------------------------
def userloop(process=None, prompt=None, hello=None, bye=None,
           usage=None, about=None, safe=False, n=-1):
  """command line loop with automatic user input processing and error checking 

  process:func = processing function called for each command line input
  prompt:str = message string displayed when waiting for user input
  hello:str = hello string displayed before starting the interactive loop
  bye:str = goodbye string displayed after ending the interactive loop
  usage:str = usage string displayed when user enters '?' or 'help'
  about:str = about string displayed when user enters '!' or 'about'
  safe:bool = ask (or not) for user confirmation before breaking loop
  n:int = number of iterations for interactive loop (default = infinite)
  """
  # merge: merge two strings and insert '\n' if both are non empty
  merge = lambda s,t: s.strip('\n') + ('\n' if s and t else '') + t
  # frame: print a full-width horizontal rule above and below a string
  frame = lambda s: print('\n'.join(('─'*80, s.strip('\n'), '─'*80)))
  if process is None: process = lambda s: s # default 'process' function
  # get documentation as global variables from the processing function 
  info = tuple(process.__globals__.get("__%s__" % s, '')
         for s in 'file author date version doc usage'.split())
  if about is None: # default 'about' string
    about = "File: %s\nAuthor: %s\nDate: %s\nVersion: %s" % info[:4]
  if usage is None: usage = merge(info[4],info[5]) # default 'usage' string
  if prompt is None: prompt = "Enter command line" # default 'prompt' string
  if hello is None: hello = usage # default 'hello' string
  if bye is None: bye = "See you later..." # default 'bye' string
  helper = ( # default help string for user loop
    "\nEnter 'help' or '?' to display some user instructions"
    "\nEnter 'about' or '!' to display some info about the application"
    "\nEnter 'exit' or an empty line to stop the interaction loop")
  # now that all information strings have been defined, it's time to loop
  if hello: frame(merge(hello,helper))
  confirm = "<> Please confirm: <ENTER> to stop, any other key to continue: "
  while(n): # do 'n' iterations at most (infinite loop by default)
    n -= 1; command = input("<> %s: " % prompt.strip())
    if command.lower() in ('','exit'):
      if not safe or (safe and pause(end='')): break
    if command.lower() in ('?','help'): frame(merge(usage,helper)); continue
    if command.lower() in ('!','about'): frame(about); continue
    try: output = process(command); print(output, end='\n' if output else '')
    except Exception as e: print("%s: %s" % (e.__class__.__name__, e)); n += 1
  if bye: frame(bye)

# ==============================================================================
# Debugging tools : timer, inspect, testcode
# ==============================================================================
def timer(fcall, show=True, n=1000):
  """measure time required for 'n' successive executions of 'fcall'

  fcall:str = string defining the function call 'f(args)' to measure
    'f(args)' is evaluated in the namespace of the caller function, so
    'args' may contain expressions with either literals or binded names
  show:bool = display measured time on screen or return it as an float
  n:int = number of function calls performed during time measure

  Note: when the execution of 'fcall' fails, a 'RuntimeError' is raised   
  """
  from inspect import stack # use 'stack' to get namespace from caller function
  from time import time # use 'time' to get access to system clock
  # merge local and global namespaces with priority to local names
  global_names, local_names = stack()[1][0].f_globals, stack()[1][0].f_locals
  namespace = dict(list(global_names.items()) + list(local_names.items()))
  # split 'fcall' into name/arguments and add square brackets around arguments
  fcall = fcall.strip(); p,q = fcall.find('('), fcall.rfind(')')
  name, args = fcall[:p], '[' + fcall[p+1:q] + ']'
  try: # check if 'f(*args)' is valid in namespace from caller function
    f = eval(name, namespace); args = eval(args, namespace); f(*args)
  except TypeError: # if 'TypeError', try again by adding indirection to 'args'
    try: args = [args]; f(*args)
    except Exception: raise RuntimeError("incorrect function call %r" % fcall)
  except Exception: raise RuntimeError("incorrect function call %r" % fcall)
  chrono = time(); print("..TIMER IS RUNNING.."*4)
  for p in range(n): f(*args)
  chrono -= time(); fcall = '%s(%s)' % (name, str(args)[1:-1]);
  if not show: return abs(chrono)
  pause("Timing for %s = %.3g sec (%s calls)" % (fcall, abs(chrono), n))
# ------------------------------------------------------------------------------
def inspect(names=False, show=True, wrap=True, field=80):
  """inspect the values for a set of comma-separated variable names

  names:str = string containing a set of comma-separated variable names
    'names' gets a special meaning when it is set to bool instead of str
    - names=False: displays all non-hidden local and global variables
    - names=True: also displays hidden local and global variables
      where hidden names means all names starting with the '__' prefix
  show:bool = display values on screen or return them as a single string
  wrap:bool = wrap or truncate values exceeding maximal field width
  field:int = maximal field width before applying wrapping or truncating 
  """
  from inspect import stack # use 'stack' to get namespace from caller function
  #from pprint import pformat # use 'pformat' to format recursive structures
  # ----------------------------------------------------------------------------
  def trunc(val, width):
    """remove the middle part of 'val' to get a string of length 'width'"""
    return val[:width//2-2] + ' ... ' + val[-width//2+3:]
  # ----------------------------------------------------------------------------
  def split(val, width, offset):
    """split and wrap 'val' to get a set of strings of length 'width'"""
    splits, n, p = [], len(val), 0
    while n-p > width:
      q = val.rfind(' ', p, p+width); splits.append(val[p:q]); p = q
    splits.append(val[p:]); return offset.join(splits)  
    # return pformat(val,width=rsize,compact=True).replace('\n',offset)
  # ----------------------------------------------------------------------------
  # get items of local and global namespaces from the caller function
  global_names, local_names = stack()[1][0].f_globals, stack()[1][0].f_locals
  items = list(global_names.items()) + list(local_names.items())
  # discard unwanted names and types before merging namespaces
  discard_types = {'builtin_function_or_method', 'function', 'method',
                   'generator', 'module', 'type'}
  discard_names = {'__builtins__','__loader__','__spec__','__cached__'}
  namespace = dict([item for item in items if item[0] not in discard_names
                    and item[1].__class__.__name__ not in discard_types])
  if isinstance(names, bool): # special meaning for 'names' if boolean
    names = [name for name in namespace if names or not name.startswith('__')]
  else: # standard meaning for 'names' if string
    # keep only variable names that are present in the merged namespace 
    names = [name.strip() for name in names.split(',')]
    names = [name for name in names if name in namespace]
  if not names: raise NameError('no valid names to inspect')
  # extract all values corresponding to the provided names
  values = [namespace[name] for name in names]
  # create left-hand fields by aligning names to the width of the longest name   
  lsize = max(map(len,names)) # size of left-hand field
  lhand = [name.ljust(lsize) for name in names] # align by left justification
  # create right-hand fields by wrapping or truncating values to remaining space
  rsize = field-lsize-3 # size of right-hand field (3 chars are taken by ' = ')
  offset = '\n' + ' '*(lsize+3) # offset from left margin to right-hand field
  rhand = [repr(val) if len(repr(val)) <= rsize else trunc(repr(val), rsize) \
           if not wrap else split(repr(val), rsize, offset) for val in values]
  # sort all fields and store into a single multi-line string
  fields = tuple(sorted(' = '.join(item) for item in zip(lhand,rhand)))
  return pause(*fields, sep='\n') if show else '\n'.join(fields)
# ------------------------------------------------------------------------------
def testcode(code, wrap=True, field=80):
  """loop over all statements of 'code' and eval/exec sequentially

  code:str = input string defining a sequence of Python statements
  wrap:bool = wrap or truncate values exceeding maximal field width
  field:int = maximal field width before applying wrapping or truncating 
  """
  # ------------------------------------------------------------------------------
  def splitcode(code):
    """split 'code' at all newline characters, except those found in strings"""
    state, code = 0, list(code.lstrip())
    # algorithm: parse code with a 4-state machine: state 0 = normal code, 
    #   state 1 = '' string, state 2 = "" string, state 3 = comment
    # during the char-by-char parsing, any newline that does not appear in
    # strings is replaced by an ASCII/Unicode NUL character = chr(0)
    for n, c in enumerate(code):
      if c == '\n' and state in (0,3): state = 0; code[n] = chr(0) # newline
      elif c == "'" and state in (0,1): state = 1-state # enter/leave '' string
      elif c == '"' and state in (0,2): state = 2-state # enter/leave "" string
      elif c == '#' and state == 0: state = 3 # enter comment
    # split code into lines, using the NUL delimiter, apply 'strip' to all
    # lines, and finally return as a list of strings
    return [line.strip() for line in ''.join(code).split(chr(0))]
  # ------------------------------------------------------------------------------
  def evalexec(statement, namespace):
    """eval/exec 'statement', according to names and values in 'namespace'"""
    try: return 1, eval(statement, namespace)
    except SyntaxError:
      try: return 0, exec(statement, namespace)
      except Exception as e: return -1, "%s: %s" % (e.__class__.__name__, e)
    except Exception as e: return -1, "%s: %s" % (e.__class__.__name__, e)
  # ------------------------------------------------------------------------------
  from inspect import stack # use 'stack' to get namespace from caller function
  # merge local and global namespaces with priority to local names
  global_names, local_names = stack()[1][0].f_globals, stack()[1][0].f_locals
  namespace = dict(list(global_names.items()) + list(local_names.items()))
  # split 'code' into lines and loop over lines
  for line in splitcode(code):
    if line: # non-empty lines in 'code' are either statements or comments
      print("%s%s" % ('' if line.startswith('#') else '>>> ', line))
      mode, val = evalexec(line, namespace) # try to eval/exec statement
      if val is None: continue # remove any 'None' returned by statement
      if isinstance(val,str) and wrap: mode = 0 # standard wrapping for strings
      # use 'inspect' for display but remove left-field (6 chars from "val = ")
      print(inspect('val', False, wrap, field+6)[6:].replace('\n      ','\n')
            if mode > 0 else val)
    elif pause(end=''): break # break loop if user interruption

# ==============================================================================
# File manipulation tools : read_[txt|blk|csv|ini], write_[txt|blk|csv|ini]
# ==============================================================================
def read_txt(filename, start=None, stop=0, step=1, sep='\n'):
  """read a slice of lines from a TXT file and return a multi-line string

  filename:str = input filename
    filename may include absolute or relative path using '/' separators
  (start,stop,step):(int,int,int) = standard slice parameters for lines
    default values for (start,stop,step) returns the whole file content
    default values for (stop,step) returns the line at index 'start'
    any other combination returns the lines in slice(start,stop,step)
  sep:str = line separator string
  """
  try:
    with open(filename, 'r') as file:
      if (start,stop,step) == (None,0,1): return file.read() # whole content
      if (stop,step) == (0,1): stop = start+1 if start+1 else None # single line
      return sep.join(file.read().split(sep)[slice(start,stop,step)])
  except OSError:
    from os.path import realpath
    raise OSError("cannot read file '%s'" % realpath(filename))
# ------------------------------------------------------------------------------
def write_txt(filename, string, start=None, stop=0, step=1, sep='\n'):
  """replace or insert a multi-line string in the content of a text file

  filename:str = output filename
    filename may include absolute or relative path using '/' separators
  string:str = string to be written in file
  (start,stop,step):(int,int,int) = standard slice parameters for lines
    default values for (start,stop,step) replaces the whole file content
    default values for (stop,step) inserts string at line index 'start'
    any other combination replaces the lines in slice(start,stop,step)
  sep:str = line separator string

  Note: the function always returns the whole file content as a string  
  """
  if (start,stop,step) != (None,0,1):
    lines = read_txt(filename).split(sep)
    if (stop,step) == (0,1): # insert when only 'start' is provided
      start = stop = (start + len(lines) + 1 if start < 0 else start)
    lines[slice(start, stop, step)] = string.split(sep)
    string = sep.join(lines)
  try:
    with open(filename, 'w') as file:
      file.write(string); return string
  except OSError:
    from os.path import realpath
    raise OSError("cannot write file '%s'" % realpath(filename))
# ------------------------------------------------------------------------------
def read_blk(filename, sep='\n', filters={}):
  """return the content of a BLK file and process blocks by a set of filters

  filename:str = input filename
  sep:str = block separator string
  filters:dict = dictionary of block filters as 'prefix:operator' items
    'prefix' are prefix strings characterizing the type of each block 
    'operator' are functions used to decode each block of a given type
    'None:operator' registers the filter used for block without a prefix
    'prefix:None' registers identity function as the filter for 'prefix'  

  With default parse configuration, all blocks starting with '#' are
  removed, all space-indended blocks are returned after processing by
  'convert', and all other blocks, are simply returned unchanged.
  """
  # merge default and user-provided filters with priority to user-provided ones
  void = lambda block: None  # default filter for comment blocks = void block
  filters = dict([(None,None),('#',void),(' ',convert)] + list(filters.items()))
  blocks, string = [], read_txt(filename)
  for block in string.split(sep): # look over blocks found in file content
    for key in filters: # loop over registered prefix strings
      if key and filters[key] and block.startswith(key):
        block = filters[key](block); break # apply corresponding block filter
    else: # if no registered prefix has been found, apply regular block filter
      if filters[None]: block = filters[None](block) 
    if block: blocks.append(block) # remove all empty blocks after filtering
  return blocks
# ------------------------------------------------------------------------------
def write_blk(filename, blocks, start=None, stop=0, step=1, sep='\n'):
  """replace or insert a set of blocks in the content of a BLK file

  filename:str = output filename
  blocks:str|list|tuple = set of blocks to be written in file
    if blocks:str, it is written unchanged as a slice in file
    if blocks:list|tuple, each item is written as a new block in file
  (start,stop,step):(int,int,int) = standard slice parameters
    default values for (start,stop,step) replaces the whole file content
    default values for (stop,step) inserts blocks at line index 'start'
    any other combination replaces the lines in slice(start,stop,step)
  sep:str = block separator string
  Note: the function always returns the whole file content as a string  
  """
  if isinstance(blocks,str): blocks = blocks.split(sep)
  elif not isinstance(blocks,(list,tuple)): blocks = [blocks]
  return write_txt(filename, sep.join("%s%s" % ('' if isinstance(block,str)
         else ' ', block) for block in blocks), start, stop, step, sep) 
# ------------------------------------------------------------------------------
def read_csv(filename, raw=False, colsep=',', rowsep='\n', sep='\n\n'):
  """return the content of a CSV file converted to a 1D, 2D or 3D matrix

  filename:str = input filename
  raw:bool = return cells as strings or apply 'convert' to each cell
  colsep:str = col separator string
  rowsep:str = row separator string
  sep:str = block separator string
  """
  # ----------------------------------------------------------------------------
  def csv(string, raw, colsep, rowsep):
    """extract the CSV data stored in 'string' and return a 1D or 2D matrix"""
    matrix = [[cell.strip() if raw else convert(cell.strip())
              for cell in row.split(colsep)] for row in string.split(rowsep)
              if not row.startswith('#')]
    return matrix if len(matrix) != 1 else matrix[0] # 1D or 2D matrix 
  # ----------------------------------------------------------------------------
  # read the CSV file as a BLK file, where 'csv_filter' is applied to all lines 
  csv_filter = lambda block: csv(block, raw, colsep, rowsep)
  matrix = read_blk(filename, sep=sep, filters={None:csv_filter, '#':None})
  return matrix if len(matrix) != 1 else matrix[0]
# ------------------------------------------------------------------------------
def write_csv(filename, matrix, start=None, stop=0, step=1,
              colsep=',', rowsep='\n', sep='\n\n'):
  """replace or insert a 1D, 2D or 3D matrix in the content of a CSV file

  filename:str = output filename
  matrix:str|list|tuple = matrix to be written in file
    if matrix:str, it is written unchanged at 'start' line index
    if matrix:list|tuple, it is first converted into a CSV string
  (start,stop,step):(int,int,int) = standard slice parameters for lines
    default values for (start,stop,step) replaces the whole file content
    default values for (stop,step) inserts matrix at line index 'start'
    any other combination replaces the lines in slice(start,stop,step)
  colsep:str = col separator string  
  rowsep:str = row separator string
  sep:str = block separator string
  Note: the function always returns the whole file content as a string  
  """
  # single: check whether an object contains single or multiple data
  single = lambda data: not isinstance(data,(list,tuple))
  # flat: apply one-level matrix flattening 
  flat = lambda mat: sum(([m] if single(m) else list(m) for m in mat), [])
  # convert matrix to a string or a list of strings, according to its dimension
  if single(matrix): # whole matrix is one single data = 0D matrix
    matrix = str(matrix)
  elif all(single(m) for m in matrix): # only single in matrix = 1D matrix
    matrix = colsep.join(map(str,matrix))
  elif all(single(m) for m in flat(matrix)): # only single in flat = 2D matrix
    matrix = rowsep.join(str(row) if single(row) else colsep.join(map(str,row))
                         for row in matrix)
  else: # at least one multiple data in flat = 3D matrix
    matrix = [str(blk) if single(blk) else rowsep.join(str(row) if single(row)\
              else colsep.join(map(str,row)) for row in blk) for blk in matrix]
  # then write the converted matrix as a list of blocks in a standard BLK file
  return write_blk(filename, matrix, start, stop, step, sep)
# ------------------------------------------------------------------------------
def read_ini(filename, raw=False, sep='\n'):
  """return the content of an INI file converted to a 2-level dictionary

  filename:str = input filename
  raw:bool = return values as strings or apply 'convert' to each value
  sep:str = line separator string
  """
  # sect_filter: extract the name from section lines
  sect_filter = lambda block: (':', block.split('[')[1].split(']')[0])
  # cont_filter: extract the value from continuation lines
  cont_filter = lambda block: (' ', block)
  # name_filter: extract the (name,value) pair from property lines
  prop_filter = lambda block: (block.partition('=')[::2]) 
  filters = {None:prop_filter, '[':sect_filter, ' ':cont_filter}
  items, section, name, value = {'':{}}, '', '', ''
  # loop over file lines and add a blank line if final line break is missing
  for lhand, rhand in read_blk(filename, filters=filters) + [('','')]:
    if lhand == ':': # section line
      if name: items[section][name] = value if raw else convert(value)
      section, name, value = rhand.strip(), '', ''; items[section] = {}
    elif lhand == ' ': # continuation line
      value = value + rhand.lstrip()
    else: # property line
      if name: items[section][name] = value if raw else convert(value)
      name, value = lhand.rstrip(), rhand.lstrip()
    if value and not name: # syntax error detected by parse
      raise SyntaxError("%r in file %r" % (rhand, filename))
  if len(items) == 1: items = items[''] # remove sections if only one section
  elif not items['']: del items[''] # remove default section if empty
  return items
# ------------------------------------------------------------------------------
def write_ini(filename, items, start=None, stop=0, step=1, sep='\n'):
  """replace or insert a set of items in the content of an INI file

  filename:str = output filename
  items:str|dict = set of items to be written in file
    if items:str, it is written unchanged at 'start' line index
    if items:dict, it is first converted into an INI string
  (start,stop,step):(int,int,int) = standard slice parameters for lines
    default values for (start,stop,step) replaces the whole file content
    default values for (stop,step) inserts items at line index 'start'
    any other combination replaces the lines in slice(start,stop,step)
  sep:str = line separator string
  Note: the function always returns the whole file content as a string
  """
  # nosections: check whether there are sections or not in input dictionary
  nosections = lambda dic: not any(isinstance(d,dict) for d in dic.values())
  # order: return items from dictionary with alphabetically ordered keys
  order = lambda dic: sorted(dic.items())
  if isinstance(items,dict):
    if nosections(items): items = {'': items} # create a default section
    items = '\n'.join(("\n[%s]\n" % sect if sect else '') + '\n'.join("%s = %s"
            % (n,v) for n,v in order(prop)) for sect, prop in order(items))
  else: items = str(items)
  return write_txt(filename, items, start, stop, step, sep) 

# ==============================================================================
if __name__ == '__main__':
  from ezCLIdemo import ezCLIdemo
  ezCLIdemo()
# ==============================================================================
