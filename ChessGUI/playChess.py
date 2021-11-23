# The approach here is to make the board hold piece location data. 
# Each piece is an object held in the boardData dictionary. The key is a tuple (a,b) where (0,0) = a1, (0,7) = a8, etc.

import pygame
import copy

# Classes 
class Board(object):
	def __init__(self, boardMode):	# boardMode: 0 - Blank board;	1 - Default starting position;		2+ - Debugging help
		self.gameMode = 2		# 0 - Anlysis mode from only white's perspective;	1 - Only Black view;	2 - Game mode, flips every turn
		if self.gameMode == 1:
			self.whiteView = False 
		else:
			self.whiteView = True
		
		self.boardData = {}
		if boardMode == 1:
			self.boardData.update({(0,0):Rook('White'), (0,1):Knight('White'), (0,2):Bishop('White'), (0,3):Queen('White'), (0,4):King('White'), (0,5):Bishop('White'), (0,6):Knight('White'), (0,7):Rook('White')})
			self.boardData.update({(1,b):Pawn('White') for b in range(8)})
			self.boardData.update({(6,b):Pawn('Black') for b in range(8)})
			self.boardData.update({(7,0):Rook('Black'), (7,1):Knight('Black'), (7,2):Bishop('Black'), (7,3):Queen('Black'), (7,4):King('Black'), (7,5):Bishop('Black'), (7,6):Knight('Black'), (7,7):Rook('Black')})
		if boardMode == 2:
			self.boardData.update({(1,1):Pawn('White'), (1,0):Pawn('White'), (2,1):Rook('Black'), (2,2):Pawn('Black'), (7,7):King('Black'), (5,7):King('White')})
		if boardMode == 3:
			self.boardData.update({(0,0):Rook('White'), (0,1):Knight('White'), (0,2):Bishop('White'), (0,3):Queen('White'), (0,4):King('White'), (0,5):Bishop('White'), (0,6):Knight('White'), (0,7):Rook('White')})
			self.boardData.update({(7,0):Rook('Black'), (7,1):Knight('Black'), (7,2):Bishop('Black'), (7,3):Queen('Black'), (7,4):King('Black'), (7,5):Bishop('Black'), (7,6):Knight('Black'), (7,7):Rook('Black')})
			self.boardData.update({(6,1):Pawn('White'), (1,1):Pawn('Black')})

		self.movelist = []
		self.moveHistory = []		# Format: [[]]
		self.whiteTurn = True
		self.moveCount = 0		# Is incremented after each move, so this is actually a half-move count
		self.drawMoveCount = 0	# Is reset to 0 after a capture or a pawn move, and incremented by 1 after each half-move. When this reaches 100, the game is drawn 
		self.whiteCastleKingside = True
		self.whiteCastleQueenside = True
		self.blackCastleKingside = True
		self.blackCastleQueenside = True
		self.enPassantPossible = ()		# Stores the square to which en passant is possible. Reset to null tuple after move
		self.gameOver = False

	def drawBoard(self):
		if self.gameMode == 2:
			self.whiteView = self.whiteTurn
		if self.checkPendingPromotion():
			self.whiteView = not self.whiteView

		if self.whiteView:
			win.fill((128, 128, 128))
			pygame.draw.rect(win, (255,255,0), (30, 30, 540, 540))
			for x in range(8):
				for y in range(8):
					if (x + y) % 2 == 0:
						color = (175, 93, 35)		# Dark square
					else:
						color = (247, 201, 160) 	# Light square
					pygame.draw.rect(win, color, (60 * (y + 1), 60 * (8 - x), 60, 60))
					if (hasattr(self.boardData.get((x,y)), 'color')):
						if self.boardData.get((x,y)).color == 'White':
							win.blit(whiteSprites[self.boardData[(x,y)].pieceCode], (60 * (y + 1), 60 * (8 - x)))
						else:
							win.blit(blackSprites[self.boardData[(x,y)].pieceCode], (60 * (y + 1), 60 * (8 - x)))

			for i in range(8):
				win.blit(LETTERS[i], (30 + 60 * (i + 1) - LETTERS[i].get_width()/2, 58 - LETTERS[i].get_height()))
				win.blit(LETTERS[i], (30 + 60 * (i + 1) - LETTERS[i].get_width()/2, 538))
				win.blit(NUMBERS[i], (545, 30 + 60 * (8 - i) - NUMBERS[i].get_height()/2))
				win.blit(NUMBERS[i], (40, 30 + 60 * (8 - i) - NUMBERS[i].get_height()/2))
		else:
			win.fill((128, 128, 128))
			pygame.draw.rect(win, (255,255,0), (30, 30, 540, 540))
			for x in range(8):
				for y in range(8):
					if (x + y) % 2 == 0:
						color = (175, 93, 35)		# Dark square
					else:
						color = (247, 201, 160) 	# Light square
					pygame.draw.rect(win, color, (60 * (y + 1), 60 * (8 - x), 60, 60))
					if (hasattr(self.boardData.get((7-x,7-y)), 'color')):
						if self.boardData.get((7-x,7-y)).color == 'White':
							win.blit(whiteSprites[self.boardData[(7-x,7-y)].pieceCode], (60 * (y + 1), 60 * (8 - x)))
						else:
							win.blit(blackSprites[self.boardData[(7-x,7-y)].pieceCode], (60 * (y + 1), 60 * (8 - x)))

			for i in range(8):
				win.blit(LETTERS[7-i], (30 + 60 * (i + 1) - LETTERS[i].get_width()/2, 58 - LETTERS[i].get_height()))
				win.blit(LETTERS[7-i], (30 + 60 * (i + 1) - LETTERS[i].get_width()/2, 538))
				win.blit(NUMBERS[7-i], (545, 30 + 60 * (8 - i) - NUMBERS[i].get_height()/2))
				win.blit(NUMBERS[7-i], (40, 30 + 60 * (8 - i) - NUMBERS[i].get_height()/2))

	def getMoves(self):
		self.movelist = []
		for location in self.boardData:
			currentPiece = self.boardData.get(location)
			if (currentPiece.color == 'White' and not self.whiteTurn) or (currentPiece.color == 'Black' and self.whiteTurn):
				continue 
			pieceLocation = [location[0], location[1]]					# Can be removed carefully to optimize later
			pieceDirections = currentPiece.directions
			pieceRange = currentPiece.pieceRange

			if currentPiece.pieceCode == 5:				# Pawn double step and capture
				if (currentPiece.color == 'White' and location[0] == 1) or (currentPiece.color == 'Black' and location[0] == 6):
					pieceRange = 2
				if currentPiece.color == 'White':
					for i in [[1,1],[1,-1]]:
						newLocation = (pieceLocation[0] + i[0], pieceLocation[1] + i[1])
						if newLocation in self.boardData:
							if self.boardData.get(newLocation).color != currentPiece.color:
								self.movelist.append([location, newLocation])
						elif newLocation == self.enPassantPossible:
							self.movelist.append([location, self.enPassantPossible])
				else:
					for i in [[-1,1],[-1,-1]]:
						newLocation = (pieceLocation[0] + i[0], pieceLocation[1] + i[1])
						if newLocation in self.boardData:
							if self.boardData.get(newLocation).color != currentPiece.color:
								self.movelist.append([location, newLocation])
						elif newLocation == self.enPassantPossible:
							self.movelist.append([location, self.enPassantPossible])

			for i in range(len(pieceDirections)):
				for j in range(pieceRange):
					newLocation = [pieceLocation[0] + (j+1)*pieceDirections[i][0], pieceLocation[1] + (j+1)*pieceDirections[i][1]]
					if newLocation[0] < 0 or newLocation[0] > 7 or newLocation[1] < 0 or newLocation[1]	> 7:	# Check if outside board
						break	
					newLocation = tuple(newLocation)
					if newLocation in self.boardData:		# Landing square already has a piece
						if self.boardData.get(newLocation).color == currentPiece.color:	# Check if landing square has piece of same color
							break
						else:
							if currentPiece.pieceCode != 5:			# Ensures that pawns can't capture straight
								self.movelist.append([location, newLocation])			# Capture
							break	
					self.movelist.append([location, newLocation])		# Move to an empty square
		
		boardDataCopy = copy.deepcopy(self.boardData) 

		########################### Castling stuff ################################
		self.whiteTurn = not self.whiteTurn
		if not self.kingInCheck():
			self.whiteTurn = not self.whiteTurn
			if self.whiteTurn:
				if self.boardData.get((0,1)) == None and self.boardData.get((0,2)) == None and self.boardData.get((0,3)) == None:
					if self.whiteCastleQueenside == True:
						self.doMove((0,4),(0,3))
						if not self.kingInCheck():
							self.movelist.append([(0,4), (0,2)])
						self.whiteTurn = not self.whiteTurn
						self.boardData = copy.deepcopy(boardDataCopy)
				if self.boardData.get((0,5)) == None and self.boardData.get((0,6)) == None:
					if self.whiteCastleKingside == True:
						self.doMove((0,4),(0,5))
						if not self.kingInCheck():
							self.movelist.append([(0,4), (0,6)])
						self.whiteTurn = not self.whiteTurn
						self.boardData = copy.deepcopy(boardDataCopy)
			else:
				if self.boardData.get((7,1)) == None and self.boardData.get((7,2)) == None and self.boardData.get((7,3)) == None:
					if self.blackCastleQueenside == True:
						self.doMove((7,4),(7,3))
						if not self.kingInCheck():
							self.movelist.append([(7,4), (7,2)])
						self.whiteTurn = not self.whiteTurn
						self.boardData = copy.deepcopy(boardDataCopy)
				if self.boardData.get((7,5)) == None and self.boardData.get((7,6)) == None:
					if self.blackCastleKingside == True:
						self.doMove((7,4),(7,5))
						if not self.kingInCheck():
							self.movelist.append([(7,4), (7,6)])
						self.whiteTurn = not self.whiteTurn
						self.boardData = copy.deepcopy(boardDataCopy)
		else:
			self.whiteTurn = not self.whiteTurn

		########################### End Castling stuff ################################

		illegalMoves = []
		for move in self.movelist:
			self.doMove(move[0], move[1])
			if self.kingInCheck():
				illegalMoves.append(move)			# This removes moves that leave the player (who just moved) in check
			self.boardData = copy.deepcopy(boardDataCopy)
			self.whiteTurn = not self.whiteTurn
		for i in illegalMoves:
			self.movelist.remove(i)

		if self.movelist == []:
			self.whiteTurn = not self.whiteTurn		# Needed because that's how kingInCheck() works (it implicitly handles turn swapping after a move)
			if self.kingInCheck():
				if self.whiteTurn:
					print('Checkmate! White wins!')
				else:
					print('Checkmate! Black wins!')
			else:
				print('Stalemate!')
			self.gameOver = True

	def doMove(self, start, end, realMove = False):				# Updates boardData and whiteTurn after each move 
		
		if realMove == True:
			# print(self.convertToChessNotation(start, end))
			if start[0] == 1 and self.boardData[start].pieceCode == 5 and end[0] == 3:
				self.enPassantPossible = (2, start[1])
			elif start[0] == 6 and self.boardData[start].pieceCode == 5 and end[0] == 4:
				self.enPassantPossible = (5, start[1])
			else:
				self.enPassantPossible = ()


		# Moves the rook when castling
		if start == (0,4) and end == (0,2) and self.boardData[start].pieceCode == 4 and self.boardData[start].color == 'White':
			self.boardData.pop((0,0))
			self.boardData[(0,3)] = Rook('White')
		elif start == (0,4) and end == (0,6) and self.boardData[start].pieceCode == 4 and self.boardData[start].color == 'White':
			self.boardData.pop((0,7))
			self.boardData[(0,5)] = Rook('White')
		elif start == (7,4) and end == (7,2) and self.boardData[start].pieceCode == 4 and self.boardData[start].color == 'Black':
			self.boardData.pop((7,0))
			self.boardData[(7,3)] = Rook('Black')
		elif start == (7,4) and end == (7,6) and self.boardData[start].pieceCode == 4 and self.boardData[start].color == 'Black':
			self.boardData.pop((7,7))
			self.boardData[(7,5)] = Rook('Black')

		if self.boardData[start].pieceCode == 5 and self.boardData.get(end) == None and (start[1] - end[1]) != 0:	# En passant conditions
			if start[0] == 4:	# White pawn doing en passant
				self.boardData.pop((4, end[1]))
			else:		# Black pawn doing en passant
				self.boardData.pop((3, end[1]))


		if end in self.boardData.keys():
			self.boardData.pop(end)
		self.boardData[end] = self.boardData[start]
		self.boardData.pop(start) 

		self.whiteTurn = not self.whiteTurn

	def kingInCheck(self):					# Checks the board to see if the player whose turn it is can capture the other king
		if self.whiteTurn:
			kingColor = 'Black'
			attackColor = 'White'
		else:
			kingColor = 'White'
			attackColor = 'Black'

		for location, piece in self.boardData.items():
			if piece.color == kingColor and piece.pieceCode == 4:
				kingLocation = location

		for direction in [[0,1], [0,-1], [1,0], [-1,0]]:		# Rook, queen and king
			for attackRange in range(1,8):
				attackLocation = (kingLocation[0] + (attackRange * direction[0]), kingLocation[1] + (attackRange * direction[1]))
				if self.boardData.get(attackLocation) != None:
					if self.boardData.get(attackLocation).color == attackColor and (self.boardData.get(attackLocation).pieceCode == 0 or self.boardData.get(attackLocation).pieceCode == 3):
						return True
					elif self.boardData.get(attackLocation).pieceCode == 4 and attackRange == 1:
						return True
					else:
						break

		for direction in [[1,1],[-1,1],[-1,-1],[1,-1]]:			# Bishop, queen and king
			for attackRange in range(1,8):
				attackLocation = (kingLocation[0] + (attackRange * direction[0]), kingLocation[1] + (attackRange * direction[1]))
				if self.boardData.get(attackLocation) != None:
					if self.boardData.get(attackLocation).color == attackColor and (self.boardData.get(attackLocation).pieceCode == 2 or self.boardData.get(attackLocation).pieceCode == 3):
						return True
					elif self.boardData.get(attackLocation).pieceCode == 4 and attackRange == 1:
						return True
					else:
						break
		
		for direction in [[2,1], [2,-1], [-2,1], [-2,-1], [1,2], [-1,2], [1,-2], [-1,-2]]:		# Knight
			attackLocation = (kingLocation[0] + direction[0], kingLocation[1] + direction[1])
			if self.boardData.get(attackLocation) != None:
					if self.boardData.get(attackLocation).color == attackColor and self.boardData.get(attackLocation).pieceCode == 1:
						return True

		if attackColor == 'White':		# Pawn
			attackDirections = [[1,1], [1,-1]]
		else:
			attackDirections = [[-1,1], [-1,-1]]
		for direction in attackDirections:
			attackLocation = (kingLocation[0] - direction[0], kingLocation[1] - direction[1])
			if self.boardData.get(attackLocation) != None:
					if self.boardData.get(attackLocation).color == attackColor and self.boardData.get(attackLocation).pieceCode == 5:
						return True

		return False

	def castleFlagUpdates(self, start, end):
		if start == (0,0):
			self.whiteCastleQueenside = False
		elif start == (0,7):
			self.whiteCastleKingside = False
		elif start == (7,0):
			self.blackCastleQueenside = False
		elif start == (7,7):
			self.blackCastleKingside = False
		
		if self.boardData.get(end) != None:
			if self.boardData[end].pieceCode == 4:
				if self.whiteTurn:
					self.blackCastleKingside = False
					self.blackCastleQueenside = False
				else:
					self.whiteCastleKingside = False
					self.whiteCastleQueenside = False

	def checkPendingPromotion(self):
		for i in range(8):
			if self.boardData.get((7,i)) != None:
				if self.boardData.get((7,i)).pieceCode == 5:
					return True
			if self.boardData.get((0,i)) != None:
				if self.boardData.get((0,i)).pieceCode == 5:
					return True
		return False

	def doPromotion(self):
		self.drawBoard()
		win.blit(unfocusBoard, (60,60))
		promoteClickLocation = ((mx//60)-3, ((my+30)//60)-5)
		for i in range(8):
			if self.boardData.get((7,i)) != None:
				if self.boardData.get((7,i)).pieceCode == 5 and self.boardData.get((7,i)).color == 'White':
					for j in range(4):
						promotionMenu.blit(whiteSprites[j], (60*j, 0))
					win.blit(promotionMenu, (180,270))
					if promoteClickLocation == (0,0):
						self.boardData[7,i] = Rook('White')
					elif promoteClickLocation == (1,0):
						self.boardData[7,i] = Knight('White')
					elif promoteClickLocation == (2,0):
						self.boardData[7,i] = Bishop('White')
					elif promoteClickLocation == (3,0):
						self.boardData[7,i] = Queen('White')
			if self.boardData.get((0,i)) != None:
				if self.boardData.get((0,i)).pieceCode == 5 and self.boardData.get((0,i)).color == 'Black':
					for j in range(4):
						promotionMenu.blit(blackSprites[j], (60*j, 0))
					win.blit(promotionMenu, (180,270))
					if promoteClickLocation == (0,0):
						self.boardData[0,i] = Rook('Black')
					elif promoteClickLocation == (1,0):
						self.boardData[0,i] = Knight('Black')
					elif promoteClickLocation == (2,0):
						self.boardData[0,i] = Bishop('Black')
					elif promoteClickLocation == (3,0):
						self.boardData[0,i] = Queen('Black')								
		if not self.checkPendingPromotion():
			self.drawBoard()

	# def convertToChessNotation(self, start, end):
	# 	workingString = ''
	# 	if self.boardData[start].pieceCode == 5:	# Pawn moves
	# 		if start[1] == end[1]:
	# 			workingString += Board.convertToSquare(end)
	# 			if end[0] == 0 or end[0] == 7:
	# 				return workingString + '='
	# 			return workingString
	# 		return 'Pawn move'
	# 	return '.'

	@staticmethod
	def convertToSquare(square):		# Takes in a tuple board location and outputs the square. (0, 0) becomes 'a1'
		return first8letters[square[1]] + str(square[0] + 1)

class Piece(object):
	"""docstring for Piece"""
	pass

class Rook(Piece):
	pieceCode = 0
	pieceRange = 7
	directions = [[1,0], [-1,0], [0,1], [0,-1]]
	def __init__(self, color):
		self.color = color

	def stringify(self):
		if self.color == 'White':
			return 'WR'
		else:
			return 'BR'

class Knight(Piece):
	pieceRange = 1
	pieceCode = 1
	directions = [[1,2], [-1,2], [-2,1], [-2,-1], [-1,-2], [1,-2], [2,-1], [2,1]]
	def __init__(self, color):
		self.color = color

	def stringify(self):
		if self.color == 'White':
			return 'WN'
		else:
			return 'BN'
		
class Bishop(Piece):
	pieceRange = 7
	pieceCode = 2
	directions = [[1,1], [-1,1], [-1,-1], [1,-1]]
	def __init__(self, color):
		self.color = color

	def stringify(self):
		if self.color == 'White':
			return 'WB'
		else:
			return 'BB'

class Queen(Piece):
	pieceRange = 7
	pieceCode = 3
	directions = [[1,1], [-1,1], [-1,-1], [1,-1], [1,0], [-1,0], [0,1], [0,-1]]
	def __init__(self, color):
		self.color = color

	def stringify(self):
		if self.color == 'White':
			return 'WQ'
		else:
			return 'BQ'
		
class King(Piece):
	pieceRange = 1
	pieceCode = 4
	directions = [[1,1], [-1,1], [-1,-1], [1,-1], [1,0], [-1,0], [0,1], [0,-1]]
	def __init__(self, color):
		self.color = color

	def stringify(self):
		if self.color == 'White':
			return 'WK'
		else:
			return 'BK'

class Pawn(Piece):
	pieceCode = 5
	pieceRange = 1
	def __init__(self, color):
		self.color = color
		if self.color == 'White':
			self.directions = [[1,0]]
		else:
			self.directions = [[-1,0]]

	def stringify(self):
		if self.color == 'White':
			return 'WP'
		else:
			return 'BP'

# Pygame stuff
SCREENWIDTH = 800
SCREENHEIGHT = 600
pygame.init()
win = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
pygame.display.set_caption("Chess")
clock = pygame.time.Clock()
moveFlag = False

font = pygame.font.SysFont('Verdana', 24)
LETTERS = [font.render('{}'.format(letter), False, (0, 0, 0)) for letter in 'abcdefgh']
NUMBERS = [font.render('{}'.format(number), False, (0, 0, 0)) for number in '12345678']
first8letters = 'abcdefgh'

COLOR_TO_PLAY = [font.render('White to play', False, (0,0,0)), font.render('Black to play', False, (0,0,0)), font.render('GAME OVER', False, (0,0,0))]

redTile = pygame.Surface((60, 60))
redTile.set_alpha(128)
redTile.fill((255, 0, 0))

promotionMenu = pygame.Surface((240,60))
promotionMenu.fill((0,0,255))

unfocusBoard = pygame.Surface((480, 480))
unfocusBoard.set_alpha(128)
unfocusBoard.fill((0, 0, 0))

whiteSprites = [pygame.image.load('images/WR.png'), pygame.image.load('images/WN.png'), pygame.image.load('images/WB.png'), pygame.image.load('images/WQ.png'), pygame.image.load('images/WK.png'), pygame.image.load('images/WP.png')]
blackSprites = [pygame.image.load('images/BR.png'), pygame.image.load('images/BN.png'), pygame.image.load('images/BB.png'), pygame.image.load('images/BQ.png'), pygame.image.load('images/BK.png'), pygame.image.load('images/BP.png')]

board = Board(1)

################################################################################################################################

# Game loop
board.drawBoard()	
pygame.display.update()
while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			quit()
		if event.type == pygame.MOUSEBUTTONDOWN:
			board.drawBoard()	
			pygame.display.update()
			mx, my = pygame.mouse.get_pos()
			clickCoordinates = (8 - (my // 60), (mx - 60) // 60)
			if not board.whiteView:
				clickCoordinates = (7 - clickCoordinates[0], 7 - clickCoordinates[1])

			if not board.gameOver:
				if not board.checkPendingPromotion():
					if moveFlag == False:
						if clickCoordinates in board.boardData.keys():
							board.getMoves()
							for i in range(len(board.movelist)):
								if clickCoordinates == board.movelist[i][0]:
									if board.whiteView:
										win.blit(redTile, (60 * (board.movelist[i][1][1] + 1), 60 * (8 - board.movelist[i][1][0])))
										pygame.draw.rect(win, (0, 255, 0), (60 * (clickCoordinates[1] + 1), 60 * (8 - clickCoordinates[0]), 60, 60), 3)
									else:
										win.blit(redTile, (60 * (8 - board.movelist[i][1][1]), 60 * (1 + board.movelist[i][1][0])))
										pygame.draw.rect(win, (0, 255, 0), (60 * (8 - clickCoordinates[1]), 60 * (1 + clickCoordinates[0]), 60, 60), 3)
									moveFlag = True
									startCoordinates = clickCoordinates 
									pygame.display.update()
					else:
						if [startCoordinates, clickCoordinates] in board.movelist:
							board.doMove(startCoordinates, clickCoordinates, True)

							board.castleFlagUpdates(startCoordinates, clickCoordinates)
							board.drawBoard()
							pygame.display.update()

							board.whiteTurn = not board.whiteTurn
							if board.kingInCheck():
								print('Check!')
							board.whiteTurn = not board.whiteTurn
							board.getMoves()
							moveFlag = False
						else:
							for i in range(len(board.movelist)):
								if clickCoordinates == board.movelist[i][0]:
									if board.whiteView:
										win.blit(redTile, (60 * (board.movelist[i][1][1] + 1), 60 * (8 - board.movelist[i][1][0])))
										pygame.draw.rect(win, (0, 255, 0), (60 * (clickCoordinates[1] + 1), 60 * (8 - clickCoordinates[0]), 60, 60), 3)
									else:
										win.blit(redTile, (60 * (8 - board.movelist[i][1][1]), 60 * (1 + board.movelist[i][1][0])))
										pygame.draw.rect(win, (0, 255, 0), (60 * (8 - clickCoordinates[1]), 60 * (1 + clickCoordinates[0]), 60, 60), 3)
									moveFlag = True
									startCoordinates = clickCoordinates 
									pygame.display.update()
				if board.checkPendingPromotion():
					board.doPromotion()
					board.whiteTurn = not board.whiteTurn
					if board.kingInCheck():
						print('Check!')
					board.whiteTurn = not board.whiteTurn

			else:
				print('The game is over! You can stop clicking')
				# TODO: Stuff like congrats message, move rewind, etc. 

		if not board.gameOver:
			if board.whiteTurn:
				win.blit(COLOR_TO_PLAY[0], (600, 60))
			else:
				win.blit(COLOR_TO_PLAY[1], (600, 60))
		else:
			win.blit(COLOR_TO_PLAY[2], (600, 60))

	pygame.display.update()
	clock.tick(30)