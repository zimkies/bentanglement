# Bentanglement
# A version of entanglement http://entanglement.gopherwoodstudios.com/
# which can solve itself with various ai
# A good demonstration of the pygames module.
# Written by Ben Kies "zimkies@gmail.com"


import random
import time
import pygame
import sys
import numpy 
from pygame.locals import *

# SIZE CONSTANTS
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
ROTATIONS = 12
ALTERNATES = 2

# EVENT CONSTANTS
MOVEEVENT = USEREVENT
STARTGAMEEVENT = USEREVENT + 1
MOUSECLICKS= {"LEFTCLICK":1,
              "CENTERCLICK": 2,
              "RIGHTCLICK": 3,
              "WHEELUP":4,
              "WHEELDOWN":5,
              "LEFTEXTRACLICK":6,
              "RIGHTEXTRACLICK":7}


# COLOURS AND PICTURES
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
BACKGROUND = "redlight.jpg"
TILECOLOUR = {"PATH": YELLOW, "EMPTY": WHITE, "START": PURPLE, "CURRENT": CYAN}
LINECOLOUR = {"USED": RED, "UNUSED": GREEN, "INVISIBLE": PURPLE, "USELESS": YELLOW}


####################### CLASSES ####################################

class Winbox:
	'''A box to display whether you have won or not'''
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


class Line:
	'''A class representing a line within each hexagon'''    
	def __init__(self, start=-1, stop=-1, status="UNUSED", startval=0, stopval=0):
		'''Note each line has a status depending on how it should be represented'''
		self.start = start
		self.stop = stop
		self.status = status # UNUSED, USED, USELESS, INVISIBLE
		self.startval = startval
		self.stopval = stopval
	
	def in_line(self, point):
		'''Returns True if the point is the stop or start of the line'''
		if ((point == self.start) or (point == self.stop)):
			return True
	def __str__(self):
		return  str(self.start) + str(self.stop) + str( self.status)
	def __repr__(self):
		return  str(self.start) + str(self.stop) + str( self.status)[0] + str(self.startval)+str(self.stopval)
		
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
		'''Follow the line starting from start to return the opposite point'''
		for l in self.lines:
			if l.start == start:
				return l.stop
			elif l.stop == start:
				return l.start

	def get_line(self, point):
		'''Return the line which contains this point'''
		for l in self.lines:
			if l.start == point:
				return l
			if l.stop == point:
				return l

	def placeline(self,start, status):
		'''Change the line containing the point start to status'''
		# Mark the line as used. 
		for i,l in enumerate(self.lines[:]):
			if (l.in_line(start)):
				l.status = status
	
	def drawhexagon(self):
		'''A method referring to a global function which draws the hexagon'''
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
		''' Converts position (row, column) to coordinates (x,y)'''
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
		'''a method to draw the lines on each hexagon'''
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
		
		pygame.draw.circle(MAINSURF, BLACK, self.coord, 1)
			
	def drawtile(self):
		'''A method to draw everything associated with the tile'''
		self.drawhexagon()
		self.drawlines()


class Board:
	""" A class to represent the board"""
	def __init__(self, ai=lambda x: []):
		self.board = []
		self.score = Score()
		self.gameover = False
		self.winbox = Winbox()
		self.ai = ai
		self.current_tiles = []
		self.alternate = 0
		
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
		''' a method to draw the board'''
		if (self.gameover ==True):
			self.winbox.draw()
			self.score.draw() 
		for row in self.board:
			for tile in row:
				if (tile is not None):
					tile.drawtile()
					
	def getNeighbour(self, tile, placeline="UNUSED", beginning=False):
		'''DEPRECATED DOES NOT WORK If placeline is "UNUSED", simply follows the open pipe till its end. If placeline is "USED", it also 'uses' or lays the tiles. Also takes "INVISIBLE". 
		If the neighbour is not valid (i.e. in the event of a win), return None'''
		
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

			tile, start = getImmediateNeighbour(tile, end)
			try:
				tile = self.board[neighbour[0][0]][neighbour[0][1]]
				tile.start = neighbour[1]
			except:
				tile = None
		
		return neighbour, tile, length

	def run_ai(self):
		'''Runs the AI for the board'''
		moves = self.ai(self)
		for move in moves:
			pygame.event.post(move)

	def place_tile(self, tile):
		self.board[tile.center[0]][ tile.center[1]] = tile

class Smartboard(Board):
	
	def getNeighbour(self, tile, placeline="UNUSED", beginning=False, collapse=False, maxlength=float("infinity")):
		'''Follows the open pipe starting from tile, all the way to its end. 
		Changes the line to whatever form of placeline is listed.
		If the neighbour is not valid (i.e. in the event of a win), return None. '''
		
		# Keep track of the starting point so we don't have an infinite loop
		startingposition = (tile, tile.start)
		start = tile.start
		
		#Cycle through the pipes till you get to the next available one
		length = 0
		while ((tile and (tile.type == "PATH")) or (beginning==True)):
			length += 1
			beginning = False
			end = tile.get_end(start)
			
			# Collapse if necessary
			if (collapse is True):
				self.collapseTile(tile)
			
			# Change line Status
			if (placeline!="UNUSED"):
				tile.placeline(start, placeline)
				tile.current = False
			
			tile, start = self.getImmediateNeighbour(tile, end)
			
			# Make sure we haven't returned to our original position. If so, return tile as None 
			if (tile == startingposition[0]):
				if (start == startingposition[1]):
					tile = None
	
		# Position of tile, the tile object, and the distance to it
		return tile, start, length
	
	def getImmediateNeighbour(self, tile, endpoint):
		'''Gets the immediate neighbour of a tile, starting from an endpoint. Returns the tile and the starting poisition'''
	
		# A POINTMAP MAPPING BORDERS OF HEXAGONS TO THEIR NEIGHBOURS
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

		neighbour = POINTMAP[endpoint][:] 
		# adjust for center and update tile to its neighbour
		neighbour[0] = tuple(map(sum,zip(tile.center,neighbour[0])))
		
		try:
			tile = self.board[neighbour[0][0]][neighbour[0][1]]
		except:
			tile = None

		start = neighbour[1]
		return tile, start


	def debugger(self):
		# Get Start tile:
		center = self.board[3][6]
		start = -1
		end = center.get_end(start)
		firsttile, start = self.getImmediateNeighbour(center, end)
		
		line = firsttile.get_line(start)
		if (line is not None):
			if (line.status != "USED"):
				import pdb
				pdb.set_trace()
				raise Exception("The line has been compromised")


	def collapseTile(self, tile):
		start = tile.start
		for line in tile.lines:
			startends, stopends = 0,0
			#  Make sure this is not the actual path
			if ((not line.in_line(start)) and (line.status != "USED")):
				tile.start = line.start
				ntile, nstart, nlen  = self.getNeighbour(tile)
				if (isEndTile(ntile) is True):
					startends = 1
					# Make that path invisible, and attach length to this point
					line.stopval = nlen-1
				
				tile.start = line.stop
				ntile, nstart,  nlen = self.getNeighbour(tile)
				if (isEndTile(ntile) is True):
					# Make that path invisible, and attach length to this point
					stopends = 1
					line.stopval = nlen-1
					
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


######################### GAME LOOP ###############################
				
def main(gametype, ai):
	'''Our main function which sets up and runs the game'''
	global MAINCLOCK, MAINSURF
	
	#'''Set up pgyame variables'''
	pygame.init()
	MAINCLOCK = pygame.time.Clock()
	MAINSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
	
	# Our Session mainloop. Everytime we restart the game, it comes back to here. 
	while True:
		mousex = 0
		mousey = 0
		pygame.display.set_caption('Bentanglement')
		mainBoard = gametype(ai)
		tile = mainBoard.board[BOARDSIDEWIDTH][2*BOARDSIDEWIDTH]
		beginning = True
		gameended = False
		restart = False
		mainBoard.alternate = 0
		# Make sure the event loop runs before the ai
		pygame.event.post(pygame.event.Event(STARTGAMEEVENT))
		
		mainBoard.current_tiles = [tile, tile]
		background = pygame.image.load(BACKGROUND).convert()
		MAINSURF.blit(background, (0,0))
		
		# For each game we play loop through here:
		while True:
		
			## Draw the board.
			MAINSURF.blit(background, (0,0))
			mainBoard.drawboard()
	
			"""This is the main game loop, which constantly loops while the program is playing. In this loop, we display the board on the screen and also handle any input events from the player. clicked will store the whether or not the player has clicked the mouse (the location is stored in mousex and mousey). We reset the value to False each time the game loop loops."""
			# Handle any events.
			events = pygame.event.get()
			for event in events:
				clicked = False
				mousebutton = -1
				"""The pygame.event.get() function returns a list of pygame.Event objects of events that have happened since the last call to pygame.event.get(). This loop uses the same code to handle each event in this list."""
				if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
					pygame.quit()
					sys.exit()
					"""In order to terminate the program, we must call both pygame.quit() (to shut down the Pygame engine) and sys.exit() (to shut down the program.)"""
				if (event.type == KEYUP and event.key == K_r):
					"""Restart the game"""
					restart = True
				if event.type == MOUSEBUTTONUP:
					# If the mouse is clicked, then store relevant data
					mousex, mousey = event.pos
					mousebutton = event.button
					clicked = True

				# Process the events
				if ((gameended is False) and (clicked == True) or (beginning==True)):
					
					# If Right-Clicked Mouse button to alternate tile
					if ((clicked == True) and (mousebutton == MOUSECLICKS["RIGHTCLICK"])):
						mainBoard.alternate += 1
						mainBoard.alternate %= 2
						tile = mainBoard.current_tiles[mainBoard.alternate]
						mainBoard.place_tile(tile)
					
					# Left click means set the current tile as it is displayed		
					elif ((mousebutton == MOUSECLICKS["LEFTCLICK"]) or (beginning == True)):
						
						# Mark the path as used, and collapse all useless lines
						mainBoard.getNeighbour(tile, placeline="USED", beginning=beginning, collapse=False)
						ntile, nstart, nlength = mainBoard.getNeighbour(tile, beginning=beginning, collapse=True)
						mainBoard.score.update(nlength)
						
						# Check if the game has ended
						if (hasWon(ntile) is True):
							endGame(mainBoard)
							print mainBoard.score.score
							gameended = True
							mainBoard.debugger()
							
						# Else update information and generate new tiles
						else:
							tile = ntile
							mainBoard.current_tiles = [generateTile(tile.center, nstart), generateTile(tile.center, nstart)]
							mainBoard.current_tiles[0].start = nstart
							mainBoard.current_tiles[1].start = nstart
							tile = mainBoard.current_tiles[mainBoard.alternate]
							mainBoard.place_tile(tile)
					
					# If rotating tile:
					elif ((clicked == True) and (mousebutton == MOUSECLICKS["WHEELUP"])):
						tile.rotate(1)
						mainBoard.place_tile(tile)
					elif ((clicked == True) and (mousebutton == MOUSECLICKS["WHEELDOWN"])):
						tile.rotate(-1)
						mainBoard.place_tile(tile)						
					# Set Parameters back to False
					clicked, beginning  = False, False, 
										
			# Redraw the screen and wait a clock tick.
			pygame.display.update()
			MAINCLOCK.tick(FPS)
					
			#Restart if the board has been marked to restart
			if (restart is True):
				del mainBoard
				break

			# Let the AI make a move			
			mainBoard.run_ai()

############################# GLOBAL FUNCTIONS ##################################

def drawhexagon(center,sidesize=TILESIDEWIDTH, color=CYAN):
	"""Draw a hexagon with center and size"""
	v = TILESIDEWIDTH/2
	h = v * 3**.5
	pointlist = [(0,2*v), (-h, v), (-h,-v), (0, -2*v), (h, -v), (h,v)]
	pointlist = map(lambda a: tuple(map(sum,zip(a,center))), pointlist)
	pygame.draw.polygon(MAINSURF, color, pointlist, 0)
	pygame.draw.aalines(MAINSURF, YELLOW, 0, pointlist)
	
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

def hasWon(tile): return isEndTile(tile)

####################################### AI FUNCTIONS #################################

def moronic_ai(board):
	if (board.gameover is True):
		#time.sleep(1)	
		return [pygame.event.Event(KEYUP, {'key': K_r})]
	else:
		return [pygame.event.Event(MOUSEBUTTONUP, {'button': MOUSECLICKS["LEFTCLICK"], 'pos': (0,0)})]

def stupid_ai(board):
	if (board.gameover is True):
		#time.sleep()
		return [pygame.event.Event(KEYUP, {'key': K_r})]
	else:
		positions = []
		for alt in range(ALTERNATES):
			pass
			board.alternate += 1
			board.alternate %= 2		
			
			tile = board.current_tiles[board.alternate]
			board.board[tile.center[0]][tile.center[1]] = tile
			for rot in range(ROTATIONS):
				tile.rotate(1)
				ntile, nstart, nlength = board.getNeighbour(tile)
				
				# Reduce incentive for terminal lines
				if (isEndTile(ntile)):
					 nlength = -1./nlength
				positions.append([nlength, alt, rot ])
		
		positions.sort(reverse=True)
		length, alt, rot = positions[0]
		commands = []
		if (alt == 0):
			commands.append(pygame.event.Event(MOUSEBUTTONUP, {'button': MOUSECLICKS["RIGHTCLICK"], 'pos': (0,0)})) 
		commands.extend([pygame.event.Event(MOUSEBUTTONUP, {'button': MOUSECLICKS["WHEELUP"], 'pos': (0,0)})]*((rot+1)%ROTATIONS))
		commands.append(pygame.event.Event(MOUSEBUTTONUP, {'button': MOUSECLICKS["LEFTCLICK"], 'pos': (0,0)}))
		return commands	

def human_ai(board):
	return []
	
	

if __name__ == '__main__':
	gametype, ai = 1,0
	if (len(sys.argv) >= 2):
		ai = int(sys.argv[1])
	GAMETYPE = {0: Board, 1: Smartboard}
	AI = {0: human_ai, 1: moronic_ai, 2: stupid_ai}
	main(GAMETYPE[gametype], ai=AI[ai]) 

