# Memory
# http://inventwithpython.com
# By Al Sweigart al@inventwithpython.com

"""
HOW TO PLAY MEMORY:
"""

import random
import time
import pygame
import sys
import numpy 
from pygame.locals import *

FPS = 30
WINDOWWIDTH = 640*2
WINDOWHEIGHT = 480*2
REVEALSPEED = 8
COLS = 10
ROWS = 6
BOXSIZE = 40
GAPSIZE = 10
TILESIDEWIDTH = 30*2
CENTERCOORD = (WINDOWWIDTH/2,WINDOWHEIGHT/2)
BOARDSIDEWIDTH = 3

DARKGRAY = (60, 60, 60)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 128, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)
BLACK = (0,0,0)

BGCOLOR = DARKGRAY
BOXCOLOR = WHITE


DONUT = 1
SQUARE = 2
DIAMOND = 3
LINES = 4
OVAL = 5

POINTMAP = {0: [(-1,-1), 7],
        1: [(-1,-1), 6],
        2: [(0,-2), 9],
        3: [(0,-2), 8],
        4: [(1,-1), 11],
        5: [(1,-1), 10],
        6: [(1,1), 1],
        7: [(1,1), 0],
        8: [(0,2), 3],
        9: [(0,2), 2],
        10: [(-1,1), 5],
        11: [(-1,1), 4]}

TILECOLOUR = {"PATH": YELLOW, "EMPTY": WHITE, "START": PURPLE, "CURRENT": CYAN}

class Tile:
    """A class to represent each tile. Note there are 3 types of tile: PATH, EMPTY, MIDDLE"""
    def __init__(self, pos, lines=[], type="PATH"):
        self.current = False
        self.orientation = 0
        self.lines = lines
        self.type = type
        self.center = pos
        self.sidesize = TILESIDEWIDTH
        self.coord = self.pos2coord()          
        self.exit = -1
        self.start = -1
        self.drawtile()
        
    def get_end(self, start):
        print self.lines
        sys.stdout.flush()
        for l in self.lines:
            if l[0] == start:
                print "start0:",  start, l[0], l[1]
                sys.stdout.flush()
                return l[1]
            elif l[1] == start:
                print "start1:",  start, l[0], l[1]
                sys.stdout.flush()
                return l[0]
                
    def use_line(self,start):
        # Mark the line as used. 
        for i,l in enumerate(self.lines[:]):
            if start in l:
                used = list(l[:])
                used[2] = "USED"
                self.lines[i] = tuple(used)
    
    def drawhexagon(self):
        type = self.type
        if (self.current is True):
            type = "CURRENT"
        color = TILECOLOUR[type]
        drawhexagon(self.coord, color=color)
    
    def pos2coord(self):
        v = TILESIDEWIDTH/2
        h = v *3**.5
        vpos, hpos = self.center
        
        # Find horizontal
        x = h*(hpos - BOARDSIDEWIDTH*2)
        y = 3*v*(vpos - BOARDSIDEWIDTH)
        
        coord = int(CENTERCOORD[0] + x), int(CENTERCOORD[1] + y)
        self.coord = coord
        return coord
    
    def drawlines(self):
        v = TILESIDEWIDTH/2
        h = v*3**.5
        slope1 = numpy.array([3**.5, -1])/2.
        slope2 = numpy.array([3**.5, 1])/2.
        LINEPOSITIONS = {-1: numpy.array([0,0]),
                    0: numpy.array([0, -2*v])-(v*2/3.)*slope1,
                    1: numpy.array([0, -2*v])-(v*4./3.)*slope1,
                    2: numpy.array([-h, 0]) - numpy.array([0,v/3.]),
                    3: numpy.array([-h, 0]) + numpy.array([0,v/3.]),
                    4: numpy.array([0, 2*v])-(TILESIDEWIDTH*2./3.)*slope2,
                    5: numpy.array([0, 2*v])-(TILESIDEWIDTH/3.)*slope2,
                    6: numpy.array([0, 2*v])+(TILESIDEWIDTH/3.)*slope1,
                    7: numpy.array([0, 2*v])+(TILESIDEWIDTH*2/3.)*slope1,
                    8: numpy.array([h, 0]) + numpy.array([0,v/3.]),
                    9: numpy.array([h, 0]) - numpy.array([0,v/3.]),
                    10: numpy.array([0, -2*v])+(TILESIDEWIDTH*2/3.)*slope2,
                    11: numpy.array([0, -2*v])+(TILESIDEWIDTH/3.)*slope2}
        
        for line in self.lines:
            LINECOLOUR = {"USED": RED, "UNUSED": GREEN}
            color = LINECOLOUR[line[2]]
            start = self.coord + LINEPOSITIONS[line[0]]
            end = self.coord +  LINEPOSITIONS[line[1]]
            pygame.draw.aaline(MAINSURF, color,start, end,1)
            #pygame.draw.circle(MAINSURF, PURPLE, start, 1)    
            #pygame.draw.circle(MAINSURF, RED, end, 1)    
        
        pygame.draw.circle(MAINSURF, BLACK, self.coord, 1)
            
    def drawtile(self):
        self.drawhexagon()
        self.drawlines()
        
def drawhexagon(center,sidesize=TILESIDEWIDTH, color=CYAN):
    """Draw a hexagon with center and size"""
    v = TILESIDEWIDTH/2
    h = v * 3**.5
    pointlist = [(0,2*v), (-h, v), (-h,-v), (0, -2*v), (h, -v), (h,v)]
    pointlist = map(lambda a: tuple(map(sum,zip(a,center))), pointlist)
    pygame.draw.polygon(MAINSURF, color, pointlist, 0)
    pygame.draw.aalines(MAINSURF, BLACK, 0, pointlist)
    
    
class Board:
    """ A class to represent the board"""
    def __init__(self):
        # set up tiles:
        size = BOARDSIDEWIDTH
        maxwidth = 2*size + 1
        self.board = []
        board2 = []
        for i in range(0,size):
            
            start = (size - i)
            row = [None]* start
            brow = [None]* start
            for j in range(start, 2*maxwidth - start  +(i+1)/2 -1,2):
                row.append(Tile((i,j), type="EMPTY"))
                row.append(None)
                brow.append(Tile((maxwidth-1-i,j), type="EMPTY" ))
                brow.append(None)
            
            del row[-1], brow[-1]
            row.extend([None]*start)
            brow.extend([None]*start)
            self.board.append(row)
            board2.append(brow)
       
        # Add the middle row    
        row = []
        for i in range(maxwidth):
            row.append(Tile((size, 2*i), type="EMPTY"))
            row.append(None)
        del row[-1]
        row[maxwidth-1] = generateCenterTile()
        self.board.append(row)
        
        # Add the bottom board to the top one
        board2.reverse()
        self.board.extend(board2)
    
    def drawboard(self):
        for row in self.board:
            for tile in row:
                if (tile is not None):
                    tile.drawtile()
                    
    def getNeighbour(self, tile, laytile=False, beginning=False):
        # If laytile is 0, simply follows the open pipe till its end. If laytile is 1, it also 'uses' or lays the tiles.
        # If the neighbour is not valid (i.e. in the event of a win), return None
        
        #Cycle through the pipes till you get to the next available one
        while (((tile is not None) and (tile.type == "PATH")) or (beginning==True)):
            beginning = False
            start = tile.start
            end = tile.get_end(start)
            
            if (laytile==1):
                tile.use_line(start)
                tile.current = False
            neighbour = POINTMAP[end][:]
    
            # adjust for center and update tile to its neighbour
            neighbour[0] = tuple(map(sum,zip(tile.center,neighbour[0])))
            try:
                tile = self.board[neighbour[0][0]][neighbour[0][1]]
                tile.start = neighbour[1]
            except:
                tile = None
        
        return neighbour, tile

    
def main():
    global MAINCLOCK, MAINSURF
    
    pygame.init()
    MAINCLOCK = pygame.time.Clock()
    MAINSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    """pygame.init() needs to be called before any of the other Pygame functions.
    pygame.time.Clock() returns a pygame.Clock object. We will use this object's tick() method to ensure that the program runs at no faster than 30 frames per second (or whatever integer value we have in the FPS constant.)
    pygame.display.set_mode() creates the window on the screen and returns a pygame.Surface object. Any drawing done on this Surface object with the pygame.draw.* functions will be displayed on the screen when we call pygame.display.update().
    More information about pygame.display.set_mode() is at http://inventwithpython.com/chapter17.html#ThepygamedisplaysetmodeandpygamedisplaysetcaptionFunctions"""

    mousex = 0
    mousey = 0
    pygame.display.set_caption('Bentanglement')
    mainBoard = Board()
    tile = mainBoard.board[BOARDSIDEWIDTH][2*BOARDSIDEWIDTH]
    beginning = True
    gameended = False
    MAINSURF.fill(BGCOLOR)
    
    # Main game loop:
    while True:
        clicked = False
    
        ## Draw the board.
        MAINSURF.fill(BGCOLOR)
        mainBoard.drawboard()

        #"""This is the main game loop, which constantly loops while the program is playing. In this loop, we display the board on the screen and also handle any input events from the player. clicked will store the whether or not the player has clicked the mouse (the location is stored in mousex and mousey). We reset the value to False each time the game loop loops."""
    
        # Handle any events.
        for event in pygame.event.get():
            """The pygame.event.get() function returns a list of pygame.Event objects of events that have happened since the last call to pygame.event.get(). This loop uses the same code to handle each event in this list."""
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                """The QUIT event is created when the user tries to shut down the program by clicking the X in the top right corner, or by killing the program from the task manager or some other means."""
                sys.stdout.flush()
                pygame.quit()
                sys.exit()
                """In order to terminate the program, we must call both pygame.quit() (to shut down the Pygame engine) and sys.exit() (to shut down the program.)"""
            if event.type == MOUSEMOTION:
                mousex, mousey = event.pos
                #print mousex, mousey
                #sys.stdout.flush()
                """A MOUSEMOTION event is created whenever the user moves the mouse over the window. The Event object created has a pos attribute that is a tuple of the two xy integer coordinates for where the mouse is located. We will save these values off to mousex and mousey."""
            if event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                clicked = True
                """When the MOUSEBUTTONUP is created, we store the location of the mouse click (which is stored as the pos attribute of the Event object) and set clicked to True."""
        
        if (gameended is False):
            if ((clicked == True) or (beginning == True)):
                
                neighbour = mainBoard.getNeighbour(tile, laytile=True, beginning=beginning)
                # Check if the game has ended
                if (hasWon(neighbour[1]) is True):
                    endGame()
                    gameended = True
                    
                # Else update information
                else:
                    neighbour = neighbour[0]
                    current_tiles = [generateTile(*neighbour), generateTile(*neighbour)]
                    current_tiles[0].start = neighbour[1]
                    current_tiles[1].start = neighbour[1]
                    tile = current_tiles[0]
                    print "New tile start: ", neighbour[1]
                    sys.stdout.flush()
                    
                    mainBoard.board[neighbour[0][0]][neighbour[0][1]] = tile
                    
                # Set Parameters back to False
                clicked, beginning = False, False
        
    
        # Redraw the screen and wait a clock tick.
        pygame.display.update()
        MAINCLOCK.tick(FPS)
        """A call to pygame.display.update() causes any drawing functions done to the MAINSURF pygame.Surface object to be drawn to the screen. Unlike other pygame.Surface object, the object stored in MAINSURF was the one returned by the pygame.display.set_mode() call, which is why it is the Surface object that is drawn to the screen when pygame.display.update() is called.
    
        The call to MAINCLOCK.tick(FPS) will introduce a pause to the game so that the program doesn't run faster than 30 frames per second. (30 is the value we stored inside the FPS constant.) This is so that our program doesn't run too fast on very powerful computer."""

def generateCenterTile():
    r = random.randint(0,11)
    lines = [(-1, r, "UNUSED")]
    tile = Tile((BOARDSIDEWIDTH, 2*BOARDSIDEWIDTH), lines=lines, type="START")
    tile.exit = r
    tile.start = -1
    return tile

def generateTile(position, start):
    nums = range(12)
    for i,n in enumerate(nums[:]):
        r = random.randint(0,11)
        nums[i], nums[r] = nums[r], nums[i]
    evens = nums[::2]
    odds = nums[1::2]
    lines = zip(evens, odds)
    lines = map(lambda x: x + ("UNUSED",), lines)
    tile = Tile(position, lines=lines, type="PATH")
    sys.stdout.flush()
    tile.start = start
    tile.current = True
    return tile

def endGame():
    pygame.draw.circle(MAINSURF, GREEN, (5,5), 10)
    
    


def hasWon(tile):
    if ((tile is None) or ((tile.type != "EMPTY") and (tile.type != "PATH"))):
        return True
    return False


def getShapeAndColor(board, boxx, boxy):
    """This function is only one line long, but it can be hard to remember that the shape and color are stored in board[boxx][boxy][0] and board[boxx][boxy][1]. Typing "getShapeAndColor()" with the parameters is much easier, so this function is more of a shortcut than anything."""
    return board[boxx][boxy][0], board[boxx][boxy][1]


def revealBoxesAnimation(board, boxes, speed):
    # Do the "box reveal" animation.
    """The sliding back animation that happens when we reveal a box is simple to explain. First, we'll always draw the background color over the entire area of the box, and then draw the icon on top of that. Then we draw varying amounts of the box color on top of that. Say that BOXSIZE is set to 40. First we'll want to draw the entire 40x40 box to fully cover the icon. Then on the next frame we only draw a 32x40 box, which means 8 columns of pixels of the icon can be seen. Then next we only draw a 24x40, so almost half of the icon can be seen. This keeps going until the box is fully revealed and we aren't drawing any of the covering box."""
    for i in range(BOXSIZE, -speed - 1, -speed):
        for b in boxes:
            """We add this nested for loop because we'll want to reveal multiple boxes at the same time (for example, in the starting animation). Of course, if the boxes list just has one box in it, then only one box is revealed and this for loop is moot. But having this for loop gives us the option for multiple boxes being revealed so we add it in."""
            drawBoxCover(board, b, i)
        pygame.display.update()
        MAINCLOCK.tick(FPS)

def unrevealBoxesAnimation(board, boxes, speed):
    # Do the "box cover" animation.
    """This function is pretty much the same as revealBoxesAnimation(), except the for loop is different."""
    for i in range(0, BOXSIZE, speed):
        for b in boxes:
            drawBoxCover(board, b, i)
        pygame.display.update()
        MAINCLOCK.tick(FPS)

def drawBoxCover(board, b, coverage):
    """Both the revealBoxesAnimation() and unrevealBoxesAnimation() do the exact same thing inside their nested for loops, so instead of copying and pasting that code twice, we just put the code in its own function and call that function twice. Getting rid of duplicated code this way is often a good idea, because if we want to change the code later (say, if we find a bug in it), then we only have to change it in one place instead of multiple places. It also makes our program shorter and easier to read."""
    left, top = leftTopOfBox(b[0], b[1])
    pygame.draw.rect(MAINSURF, BGCOLOR, (left, top, BOXSIZE, BOXSIZE))
    shape, color = getShapeAndColor(board, b[0], b[1])
    drawShape(shape, color, b[0], b[1])
    if coverage > 0:
        pygame.draw.rect(MAINSURF, BOXCOLOR, (left, top, coverage, BOXSIZE))


def isOverBox(x, y):
    """The isOverBox() function takes window coordinates and checks if they are over one of the boxes on the board. This function will be used so we know if the mouse is over a box (in which case, we draw the blue highlight around that box. It returns the box coordinates of the box it is over. If it is not over any boxes, it returns the tuple (None, None) instead."""
    for boxx in range(COLS):
        for boxy in range(ROWS):
            left, top = leftTopOfBox(boxx, boxy)
            boxRect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
            if boxRect.collidepoint(x, y):
                """First we get the window coordinates of the top left corner of the box by calling our leftTopOfBox() function. We use this information to create a pygame.Rect object, because pygame.Rect objects have a collidepoint() method which will tell us if the coordinates we provide are inside of the rectangle the pygame.Rect object represents. If so, then collidepoint() returns True and we know we should return the current box's box coordinates."""
                return (boxx, boxy)
    return (None, None)


def highlightBox(boxx, boxy):
    left, top = leftTopOfBox(boxx, boxy)
    pygame.draw.rect(MAINSURF, BLUE, (left - 5, top - 5, BOXSIZE + 10, BOXSIZE + 10), 4)
    """The 4 argument we pass to pygame.draw.rect() function tells the function that we want the rectangle we are drawing to have an outline width of 4 pixels. To make the rectangle fatter, increase this number. If the number is set to 0 (or not passed at all, like in other calls to pygame.draw.rect(), then a filled rectangle will be drawn."""


def drawShape(shape, color, boxx, boxy):
    quarter = int(BOXSIZE * 0.25)
    half = int(BOXSIZE * 0.5)

    left, top = leftTopOfBox(boxx, boxy)
    """Each of the shapes has its own custom bit of code that draws it. We have this code in one of the if or elif blocks in this function. To find where in the window we should draw the shape, we get the top left corner of the box's position. To keep things proportional, we also get the size of 1/4 and 1/2 of the box stored in quarter and half, respectively."""
    if shape == DONUT:
        pygame.draw.circle(MAINSURF, color, (left + half, top + half), half - 5)
        pygame.draw.circle(MAINSURF, BGCOLOR, (left + half, top + half), quarter - 5)
        """To draw the donut shape, first we draw a large circle (with a radius of half of the box size minus 5 pixels), and then draw the "hole" by drawing a smaller circle of the background color (with a radius of a quarter of the box size minus 5 pixels)."""
    elif shape == SQUARE:
        pygame.draw.rect(MAINSURF, color, (left + 10, top + 10, BOXSIZE - 20, BOXSIZE - 20))
    elif shape == DIAMOND:
        pygame.draw.polygon(MAINSURF, color, ((left + half, top), (left + BOXSIZE, top + half), (left + half, top + BOXSIZE), (left, top + half)))
        """We can draw the diamond shape by drawing a polygon with points in the middle of the top, right, bottom, and then left sides of the box in order."""
    elif shape == LINES:
        for i in range(0, BOXSIZE, 4):
            pygame.draw.line(MAINSURF, color, (left, top + i), (left + i, top))
            pygame.draw.line(MAINSURF, color, (left + i, top + BOXSIZE), (left + BOXSIZE, top + i))
    elif shape == OVAL:
        pygame.draw.ellipse(MAINSURF, color, (left, top + quarter, BOXSIZE, half))


if __name__ == '__main__':
    main()
    """This if statement is actually the first line of code that is run in our program (aside from the import statements and the constant variable assignments. __name__ is a special variable that is created for all Python programs implicitly. The value stored in this variable is the string '__main__', but only when the script is run by itself. If this script is imported by another script's import statement, then the value of __name__ will be the name of the file (if this script still has the name memory.py, then the __name__ variable will contain 'memory').

    This is really handy if we ever want to use the functions that are in this program in another program. By having this if statement here, which then runs the main() function, we could have another program use "import memory" and make use of any of the functions we've already written. Or if you want to test individual functions by calling them from the interactive shell, you could call them without running the game program. This trick is really handy for code reuse."""