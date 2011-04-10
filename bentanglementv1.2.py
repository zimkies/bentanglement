# Just adding an experimental comment
# Memory"
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
WINDOWWIDTH = 1000
WINDOWHEIGHT = 700
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
YELLOW = (255, 255, 180)
ORANGE = (255, 128, 0)
PURPLE = (180, 110, 180)
CYAN = (204, 255, 255)
BLACK = (0,0,0)

BGCOLOR = DARKGRAY
BOXCOLOR = WHITE


DONUT = 1
SQUARE = 2
DIAMOND = 3
LINES = 4
OVAL = 5

MOVEEVENT = USEREVENT
BACKGROUND = "redlight.jpg"
LINECOLOUR = {"USED": RED, "UNUSED": GREEN, "INVISIBLE": PURPLE, "USELESS": YELLOW}#{"USED": RED, "UNUSED": GREEN, "INVISIBLE": PURPLE, "USELESS": BLACK}
MOUSECLICKS= {"LEFTCLICK":1,
              "CENTERCLICK": 2,
              "RIGHTCLICK": 3,
              "WHEELUP":4,
              "WHEELDOWN":5,
              "LEFTEXTRACLICK":6,
              "RIGHTEXTRACLICK":7}

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

class Line:
    
	def __init__(self, start=-1, stop=-1, status="UNUSED", startval=0, stopval=0):
		self.start = start
		self.stop = stop
		self.status = status # UNUSED, USED, USELESS, INVISIBLE
		self.startval = startval
		self.stopval = stopval
	
	def __str__(self):
		return  str(self.start) + str(self.stop) + str( self.status)
	def __repr__(self):
		return  str(self.start) + str(self.stop) + str( self.status)[0] + str(self.startval)+str(self.stopval)
		
class Winbox:
	
	def __init__(self):
		# Render
		txt = "GAME OVER"
		font = pygame.font.Font(None, 22)
		score = font.render(txt, True, (255,255, 255), BGCOLOR)
		
		# Create a rectangle
		scoreRect = score.get_rect()
		
		# Center the rectangle
		scoreRect.centerx, scoreRect.centery =  100, 250
		self.scoreRect = scoreRect
		self.score = score

	def draw(self):
		# Blit the text
		MAINSURF.blit(self.score, self.scoreRect)
	

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
		for l in self.lines:
			if l.start == start:
				return l.stop
			elif l.stop == start:
				return l.start
				
	def placeline(self,start, status):
		# Mark the line as used. 
		for i,l in enumerate(self.lines[:]):
			if ((l.start == start) or (l.stop == start)):
				l.status = status
	
	def drawhexagon(self):
		type = self.type
		if (self.current is True):
			type = "CURRENT"
		color = TILECOLOUR[type]
		drawhexagon(self.coord, color=color)
	
	def rotate(self, times):
		"""rotate the tile times times"""
		for l in self.lines:
			l.start = (l.start+times) %12
			l.stop = (l.stop+times) %12
	
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
			color = LINECOLOUR[line.status]
			start = self.coord + LINEPOSITIONS[line.start]
			end = self.coord +  LINEPOSITIONS[line.stop]
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
	pygame.draw.aalines(MAINSURF, YELLOW, 0, pointlist)
	
class Score:
	
	def __init__(self):
		self.score = 0
		self.segments = 0
		self.longest = 0
		self.font = pygame.font.Font(None, 22)
		
	def update(self, length):
		self.segments +=length
		score = sum(range(length+1))
		self.score += score
		if self.longest < length:
			self.longest = length
			
	def draw(self):
		# Render
		scoreText = "Score: " + str(self.score)
		segmentsText = "Segments: " + str(self.segments)
		longestText = "Longest: " + str(self.longest) 
		
		score = self.font.render(scoreText, True, (255,255, 255), BGCOLOR)
		segments = self.font.render(segmentsText, True, (255,255, 255), BGCOLOR)
		longest = self.font.render(longestText, True, (255,255, 255), BGCOLOR)
		
		# Create a rectangle
		scoreRect = score.get_rect()
		segmentsRect = segments.get_rect()
		longestRect = longest.get_rect()
		
		# Center the rectangle
		scoreRect.centerx, scoreRect.centery =  100, 100
		segmentsRect.centerx, segmentsRect.centery =  100, 150
		longestRect.centerx, longestRect.centery =  100, 200

		# Blit the text
		MAINSURF.blit(score, scoreRect)
		MAINSURF.blit(segments, segmentsRect)
		MAINSURF.blit(longest, longestRect)
		
class Board:
	""" A class to represent the board"""
	def __init__(self, ai=lambda x: []):
		self.board = []
		self.score = Score()
		self.gameover = False
		self.winbox = Winbox()
		self.ai = ai
		
		# set up tiles:
		size = BOARDSIDEWIDTH
		maxwidth = 2*size + 1
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
		if (self.gameover ==True):
			print self.score.score
			self.winbox.draw()
		self.score.draw()
		for row in self.board:
			for tile in row:
				if (tile is not None):
					tile.drawtile()
					
	def getNeighbour(self, tile, placeline="UNUSED", beginning=False):
		# If placeline is "UNUSED", simply follows the open pipe till its end. If placeline is "USED", it also 'uses' or lays the tiles.
		# Also takes "INVISIBLE"
		# If the neighbour is not valid (i.e. in the event of a win), return None
		
		#Cycle through the pipes till you get to the next available one
		length = 0
		while (((tile is not None) and (tile.type == "PATH")) or (beginning==True)):
			length += 1
			beginning = False
			start = tile.start
			end = tile.get_end(start)
			
			if (placeline!="UNUSED"):
				tile.placeline(start, placeline)
				tile.current = False
				
			neighbour = POINTMAP[end][:]
	
			# adjust for center and update tile to its neighbour
			neighbour[0] = tuple(map(sum,zip(tile.center,neighbour[0])))
			try:
				tile = self.board[neighbour[0][0]][neighbour[0][1]]
				tile.start = neighbour[1]
			except:
				tile = None
		
		return neighbour, tile, length

		def ai(self):
			'''Runs the AI for the board'''
			if (self.gameover is True):
				pygame.event.post(pygame.event.Event(KEYUP, {'key': K_r}))
			else:
				moves = self.ai()
				for move in moves:
					pygame.event.post(move)
				pygame.event.post(pygame.event.Event(MOUSEBUTTONUP, {'button': MOUSECLICKS["LEFTCLICK"], 'pos': (0,0)}))
	
class Smartboard(Board):
	
	def getNeighbour(self, tile, placeline="UNUSED", beginning=False, collapse=False):
		# If placeline is "UNUSED", simply follows the open pipe till its end. If placeline is 1, it also 'uses' or lays the tiles.
		# If the neighbour is not valid (i.e. in the event of a win), return None
		
		#Cycle through the pipes till you get to the next available one
		length = 0
		# Keep track of the starting point so we don't have an infinite loop
		startingposition = (tile, tile.start)

		while (((tile is not None) and (tile.type == "PATH")) or (beginning==True)):
			sys.stdout.flush()
			if (collapse is True):
				self.collapseTile(tile)
			length += 1
			beginning = False
			start = tile.start
			end = tile.get_end(start)
			
			if (placeline!="UNUSED"):
				tile.placeline(start, placeline)
				tile.current = False
			
			neighbour = POINTMAP[end][:]
	
			# adjust for center and update tile to its neighbour
			neighbour[0] = tuple(map(sum,zip(tile.center,neighbour[0])))
			try:
				tile = self.board[neighbour[0][0]][neighbour[0][1]]
				tile.start = neighbour[1]
				# Make sure we haven't returned to our original position. If we have, then act as if we have reached deadend. 
				if (tile == startingposition[0]):
					if (tile.start == startingposition[1]):
						raise Exception
			except:
				tile = None
		
		return neighbour, tile, length
	
	def collapseTile(self, tile):
		start = tile.start
		for line in tile.lines:
			startends, stopends = 0,0
			#  Make sure this is not the actual path
			if ((line.start != start) and (line.stop != start) and (line.status != "USED")):
				tile.start = line.start
				npos, ntile, nlen = self.getNeighbour(tile)
				if (isEndTile(ntile) is True):
					startends = 1
					# Make that path invisible, and attach length to this point
					line.stopval = nlen-1
					self.getNeighbour(tile, placeline="INVISIBLE")
				
				tile.start = line.stop
				npos, ntile, nlen = self.getNeighbour(tile)
				if (isEndTile(ntile) is True):
					# Make that path invisible, and attach length to this point
					stopends = 1
					line.stopval = nlen-1
					self.getNeighbour(tile, placeline="INVISIBLE")
					
				# If both ends terminate then make the entire line useless
				if ((startends == 1) and (stopends == 1)):
					tile.start = line.start
					self.getNeighbour(tile, placeline="USELESS")
					tile.start = line.stop
					self.getNeighbour(tile, placeline="USELESS")
					
				elif (startends == 1):
					tile.start = line.stop
					self.getNeighbour(tile, placeline="INVISIBLE")
				
				elif (stopends == 1):
					tile.start = line.start
					self.getNeighbour(tile, placeline="INVISIBLE")
					
				# Otherwise make the line unused again
				else:
					line.status = "UNUSED"
				
			tile.start = start
		# Replace the original start value again:
		tile.start = start
				
def main(gametype):
	global MAINCLOCK, MAINSURF
	
	pygame.init()
	MAINCLOCK = pygame.time.Clock()
	MAINSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
	"""pygame.init() needs to be called before any of the other Pygame functions.
	pygame.time.Clock() returns a pygame.Clock object. We will use this object's tick() method to ensure that the program runs at no faster than 30 frames per second (or whatever integer value we have in the FPS constant.)
	pygame.display.set_mode() creates the window on the screen and returns a pygame.Surface object. Any drawing done on this Surface object with the pygame.draw.* functions will be displayed on the screen when we call pygame.display.update().
	More information about pygame.display.set_mode() is at http://inventwithpython.com/chapter17.html#ThepygamedisplaysetmodeandpygamedisplaysetcaptionFunctions"""
	
	while True:
		mousex = 0
		mousey = 0
		pygame.display.set_caption('Bentanglement')
		mainBoard = gametype()
		tile = mainBoard.board[BOARDSIDEWIDTH][2*BOARDSIDEWIDTH]
		beginning = True
		gameended = False
		restart = False
		alternate = 0
		
		current_tiles = [tile, tile]
		background = pygame.image.load(BACKGROUND).convert()
		MAINSURF.blit(background, (0,0))
		
		# Main game loop:
		while True:
			clicked = False
			mousebutton = -1
		
			## Draw the board.
			MAINSURF.blit(background, (0,0))
			mainBoard.drawboard()
	
			"""This is the main game loop, which constantly loops while the program is playing. In this loop, we display the board on the screen and also handle any input events from the player. clicked will store the whether or not the player has clicked the mouse (the location is stored in mousex and mousey). We reset the value to False each time the game loop loops."""
			# Handle any events.
			for event in pygame.event.get():
				sys.stdout.flush()
				"""The pygame.event.get() function returns a list of pygame.Event objects of events that have happened since the last call to pygame.event.get(). This loop uses the same code to handle each event in this list."""
				if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
					"""The QUIT event is created when the user tries to shut down the program by clicking the X in the top right corner, or by killing the program from the task manager or some other means."""
					pygame.quit()
					sys.exit()
					"""In order to terminate the program, we must call both pygame.quit() (to shut down the Pygame engine) and sys.exit() (to shut down the program.)"""
				if (event.type == KEYUP and event.key == K_r):
					"""Restart the game"""
					restart = True
				if event.type == MOUSEMOTION:
					mousex, mousey = event.pos
					"""A MOUSEMOTION event is created whenever the user moves the mouse over the window. The Event object created has a pos attribute that is a tuple of the two xy integer coordinates for where the mouse is located. We will save these values off to mousex and mousey."""
				if event.type == MOUSEBUTTONUP:
					mousex, mousey = event.pos
					mousebutton = event.button
					clicked = True
					"""When the MOUSEBUTTONUP is created, we store the location of the mouse click (which is stored as the pos attribute of the Event object) and set clicked to True."""
			if ((gameended is False)):
				# If Right-Clicked Mouse button to alternate tile
				if ((clicked == True) and (mousebutton == MOUSECLICKS["RIGHTCLICK"])):
					alternate += 1
					alternate %= 2
					tile = current_tiles[alternate]
					mainBoard.board[neighbour[0][0]][neighbour[0][1]] = tile
					
				elif (((clicked == True) and (mousebutton == MOUSECLICKS["LEFTCLICK"])) or (beginning == True)):
					
					# Mark the path as used
					mainBoard.getNeighbour(tile, placeline="USED", beginning=beginning, collapse=False)
					# Collapse all useless lines
					neighbour = mainBoard.getNeighbour(tile, beginning=beginning, collapse=True)
					mainBoard.score.update(neighbour[2])
					# Check if the game has ended
					if (hasWon(neighbour[1]) is True):
						endGame(mainBoard)
						gameended = True
						
					# Else update information
					else:
						neighbour = neighbour[0]
						current_tiles = [generateTile(*neighbour), generateTile(*neighbour)]
						current_tiles[0].start = neighbour[1]
						current_tiles[1].start = neighbour[1]
						tile = current_tiles[alternate]
						mainBoard.board[neighbour[0][0]][neighbour[0][1]] = tile
				elif ((clicked == True) and (mousebutton == MOUSECLICKS["WHEELUP"])):
					tile.rotate(1)
					mainBoard.board[neighbour[0][0]][neighbour[0][1]] = tile
				elif ((clicked == True) and (mousebutton == MOUSECLICKS["WHEELDOWN"])):
					tile.rotate(-1)
					mainBoard.board[neighbour[0][0]][neighbour[0][1]] = tile
					
				# Set Parameters back to False
				clicked, beginning  = False, False, 

		
			# Redraw the screen and wait a clock tick.
			pygame.display.update()
			MAINCLOCK.tick(FPS)
			"""A call to pygame.display.update() causes any drawing functions done to the MAINSURF pygame.Surface object to be drawn to the screen. Unlike other pygame.Surface object, the object stored in MAINSURF was the one returned by the pygame.display.set_mode() call, which is why it is the Surface object that is drawn to the screen when pygame.display.update() is called.
			The call to MAINCLOCK.tick(FPS) will introduce a pause to the game so that the program doesn't run faster than 30 frames per second. (30 is the value we stored inside the FPS constant.) This is so that our program doesn't run too fast on very powerful computer."""
			
			# Let the AI make a move
			ai(mainBoard)

			#Restart if the board has been marked to restart
			if (restart is True):
				del mainBoard
				break

def generateCenterTile():
	r = random.randint(0,11)
	lines = [Line(-1, r)]
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
	lines = map(lambda x: Line(x[0], x[1]), lines)
	tile = Tile(position, lines=lines, type="PATH")
	sys.stdout.flush()
	tile.start = start
	tile.current = True
	return tile

def endGame(board):
	board.gameover = True

def isEndTile(tile):
	if ((tile is None) or ((tile.type != "EMPTY") and (tile.type != "PATH"))):
		return True
	return False

def hasWon(tile):
	return isEndTile(tile)
	
	

if __name__ == '__main__':
	GAMETYPE = {0: Board, 1: Smartboard}
	type = 1
	main(GAMETYPE[type])
	"""This if statement is actually the first line of code that is run in our program (aside from the import statements and the constant variable assignments. __name__ is a special variable that is created for all Python programs implicitly. The value stored in this variable is the string '__main__', but only when the script is run by itself. If this script is imported by another script's import statement, then the value of __name__ will be the name of the file (if this script still has the name memory.py, then the __name__ variable will contain 'memory').
	This is really handy if we ever want to use the functions that are in this program in another program. By having this if statement here, which then runs the main() function, we could have another program use "import memory" and make use of any of the functions we've already written. Or if you want to test individual functions by calling them from the interactive shell, you could call them without running the game program. This trick is really handy for code reuse."""
