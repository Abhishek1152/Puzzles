#!/usr/bin/python

import random
import sys
from optparse import OptionParser

DEFAULT_WIDTH = 10
DEFAULT_HEIGHT = 10
DEFAULT_SEED = None   # using None will seed PRNG with current system time
DEFAULT_ANIMATE = False
DEFAULT_DELAY = 0.04

class Maze(object):
  """Class Maze defines basic behavior to which a maze should conform.
It provides basic initialization/construction for the maze class, 
and provides a method for drawing ASCII mazes.

Specific "maze-carving" techniques are implemented in subclasses."""
  
  #
  # Configure class variables
  #
  N,S,E,W = 1,2,4,8
  DX = { E:+1, W:-1, N:0, S:0 }
  DY = { E:0, W:0, N:-1, S:+1 }
  OPPOSITE = { E:W, W:E, N:S, S:N }

  def __init__(self,w=DEFAULT_WIDTH,h=DEFAULT_HEIGHT,s=DEFAULT_SEED):
    """Initialize a new 2D maze with the given width and height.

Default seed will given "random" behavior.
User-supplied seed will give deterministic behavior."""
    
    # Initialize the instance variables
    self.width = DEFAULT_WIDTH if w is None else w
    self.height = DEFAULT_HEIGHT if h is None else h
    self.seed = DEFAULT_SEED if s is None else s

    # seed the PRNG
    random.seed(self.seed)

    # build the grid to hold the maze
    self.grid = [[0 for col in range(self.width)] for row in range(self.height)]


  def draw(self,):
    """Draw the grid, starting in the upper-left hand corner."""
 
    #
    # Draw the top line
    #
    buffer = []; out = " " 
    for i in range(2*self.width - 1):
      out += "_"
    buffer.append(out)

    # 
    # Draw each of the rows.
    #
    for j in range(self.height):
      out = "|"
      for i in range(self.width):
        # draw the "bottom" using S switch
        out += " " if ((self.grid[j][i] & Maze.S) != 0) else "_"

        # draw the "side" using E switch
        if (self.grid[j][i] & Maze.E) != 0:
          out += " " if (((self.grid[j][i] | self.grid[j][i+1]) & Maze.S) != 0) else "_"
        else:
          out += "|"

      buffer.append(out)

    #
    # Output maze metadata.
    #
    buffer.append(Maze.metadata(self,))
    print "\r\n".join(buffer)

  def metadata(self,):
    """Output maze metadata."""
    return " ".join([sys.argv[0],str(self.width),str(self.height),str(self.seed)])

class Kruskal(Maze):
  """Generate a maze using randomized variant of Kruskal's algorithm.

Loosely speaking, the algorithm is implemented as follows:

(1) Designate the "walls" between cells as edges.
(2) Randomly select an edge.
(3) If the selected edge connects two disjoint trees, join the trees.
(4) Otherwise, throw that edge away.
(5) Repeat Step 2.
"""

  def __init__(self,w=DEFAULT_WIDTH,h=DEFAULT_HEIGHT,s=DEFAULT_SEED,a=DEFAULT_ANIMATE,d=DEFAULT_DELAY):
    """Initialize a new 2D maze with the given width and height.

Default seed value will give "random" behavior.
Used-supplied seed value will give "deterministic" behavior.
""" 
    #
    # Invoke super-constructor
    #
    super(Kruskal,self).__init__(w,h,s)

    #
    # Only prepare the maze beforehand if we are doing "static" (i.e., animate=false) drawing
    #
    self.delay = d
    self.animate = a
    if not self.animate:
      Kruskal.carve_passages(self)

  def carve_passages(self,):
    pass

  def draw(self,):
    """Methdon ly needs to be overwridden if we are animating.

If we are drawing the maze statically, defer to the superclass."""
    
    # 
    # Clear the screen.
    #
    sys.stdout.write("\x1b[2J")

    if not self.animate:
      # 
      # Move to upper left and defer to superclass.
      #
      sys.stdout.write("\x1b[H")
      Maze.draw(self) 
     
    else:
      # 
      # If we are animating, clear the screen and start carving:
      #
      Kruskal.carve_passages(self)

class Tree(object):
  """we will use a tree structure to model the "set" (or "vertex") that is used in Kruskal to build the graph."""

  def __init__(self,):
    """Build a new tree object."""
    self.parent = None
    self.root = None

  def root(self,):
    """If we are joined, return the root. Otherwise return self."""
    return self.parent.root if self.parent else self

  def connected(self,tree):
    """Are we connected to this tree?"""
    return self.root == tree.root

  def connect(self,tree):
    """Connect to tree"""
    tree.root.parent = self

#
# Parse the command line arguments
#
parser = OptionParser()
parser.set_conflict_handler("resolve")
parser.add_option("-w","--width",dest="width",help="width of maze",metavar="<maze-width>")
parser.add_option("-h","--height",dest="height",help="height of maze",metavar="<maze-height>")
parser.add_option("-s","--seed",dest="seed",help="seed for PRNG generator",metavar="<prng-seed>")
parser.add_option("-a","--animated",action="store_true",dest="animated",help="animate rendering?",metavar="<animated?>")
parser.add_option("-d","--delay",dest="delay",help="animation delay",metavar="<animation-delay>")
(options,args) = parser.parse_args()

#
# Set the arguments we will use
#
w = DEFAULT_WIDTH if options.width is None else int(options.width)
h = DEFAULT_HEIGHT if options.height is None else int(options.height)
s = DEFAULT_SEED if options.seed is None else int(options.seed)
a = True if options.animated else False
d = DEFAULT_DELAY if options.delay is None else float(options.delay)

#
# Build and draw a new maze
#
m = Kruskal(w,h,s,a,d)
m.draw()
