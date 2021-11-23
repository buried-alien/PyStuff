import itertools
import copy

class Board(object):
	def __init__(self, setupCode):
		self.gameOver = False
		self.whiteTurn = True
		self.boardData = {}
		if setupCode == 1:
			self.boardData.update({(0,0):Rook('White'), (0,1):Knight('White'), (0,2):Bishop('White'), (0,3):Queen('White'), (0,4):King('White'), (0,5):Bishop('White'), (0,6):Knight('White'), (0,7):Rook('White')})
			self.boardData.update({(1,b):Pawn('White') for b in range(8)})
			self.boardData.update({(6,b):Pawn('Black') for b in range(8)})
			self.boardData.update({(7,0):Rook('Black'), (7,1):Knight('Black'), (7,2):Bishop('Black'), (7,3):Queen('Black'), (7,4):King('Black'), (7,5):Bishop('Black'), (7,6):Knight('Black'), (7,7):Rook('Black')})
		self.movelist = []
		self.whiteCastleKingside = True
		self.whiteCastleQueenside = True
		self.blackCastleKingside = True
		self.blackCastleQueenside = True
		self.enPassantPossible = ()

	def drawBoard(self):
		if self.whiteTurn:
			print('  a b c d e f g h ')
			for i in range(8):
				print(str(8-i) + '|', end='')
				for j in range(8):
					if self.boardData.get((7-i,j)) != None:
						print(self.boardData[(7-i,j)].stringify() + '|', end='')
					else:
						print(' |', end='')
				print(i)
			print('  a b c d e f g h ')
		else:
			print('  h g f e d c b a ')
			for i in range(8):
				print(str(1+i) + '|', end='')
				for j in range(8):
					if self.boardData.get((i,7-j)) != None:
						print(self.boardData[(i,7-j)].stringify() + '|', end='')
					else:
						print(' |', end='')
				print(1+i)
			print('  h g f e d c b a ')

	def kingInCheck(self):
		if self.whiteTurn:
			kingColor, attackColor = 'White', 'Black'
		else:
			kingColor, attackColor = 'Black', 'White'

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

	def getMoveInput(self):
		if self.whiteTurn:
			enteredMove = input("Enter White's move: ")
		else:
			enteredMove = input("Enter Black's move")

		while enteredMove not in self.movelist:
			print('That move is not allowed. Try again, using algebraic chess notation. ', end='')
			if self.whiteTurn:
				enteredMove = input("Enter White's move: ")
			else:
				enteredMove = input("Enter Black's move")
		return enteredMove	

	def getMoveList(self):
		self.movelist = []
		for location in self.boardData:
			currentPiece = self.boardData.get(location)
			if (currentPiece.color == 'White' and not self.whiteTurn) or (currentPiece.color == 'Black' and self.whiteTurn):
				continue 
			pieceLocation = [location[0], location[1]]					# Can be removed carefully to optimize later
			pieceDirections = currentPiece.directions
			pieceRange = currentPiece.pieceRange

			if currentPiece.pieceCode == 5:				# Pawn double step and capture
				if (location[0] == 1) or (location[0] == 6):
					pieceRange = 2
				if currentPiece.color == 'White':
					for i in [[1,1],[1,-1]]:
						newLocation = (pieceLocation[0] + i[0], pieceLocation[1] + i[1])
						if newLocation in self.boardData:
							if self.boardData.get(newLocation).color != currentPiece.color:
								self.movelist.append(self.convertToSquare(location)[0] + "x" + board.convertToSquare(newLocation))
						elif newLocation == self.enPassantPossible:
							self.movelist.append(self.convertToSquare(location)[0] + "x" + board.convertToSquare(newLocation) + ' e.p.')
				else:
					for i in [[-1,1],[-1,-1]]:
						newLocation = (pieceLocation[0] + i[0], pieceLocation[1] + i[1])
						if newLocation in self.boardData:
							if self.boardData.get(newLocation).color != currentPiece.color:
								self.movelist.append(self.convertToSquare(location)[0] + "x" + board.convertToSquare(newLocation))
						elif newLocation == self.enPassantPossible:
							self.movelist.append(self.convertToSquare(location)[0] + "x" + board.convertToSquare(newLocation) + ' e.p.')

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
								self.movelist.append(currentPiece.stringify().upper() + self.convertToSquare(pieceLocation) + 'x' + self.convertToSquare(newLocation))			# Capture
							break	
					self.movelist.append(currentPiece.stringify().upper() + self.convertToSquare(pieceLocation) + self.convertToSquare(newLocation))		# Move to an empty square
		
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
							self.movelist.append('O-O-O')
						self.whiteTurn = not self.whiteTurn
						self.boardData = copy.deepcopy(boardDataCopy)
				if self.boardData.get((0,5)) == None and self.boardData.get((0,6)) == None:
					if self.whiteCastleKingside == True:
						self.doMove((0,4),(0,5))
						if not self.kingInCheck():
							self.movelist.append('O-O')
						self.whiteTurn = not self.whiteTurn
						self.boardData = copy.deepcopy(boardDataCopy)
			else:
				if self.boardData.get((7,1)) == None and self.boardData.get((7,2)) == None and self.boardData.get((7,3)) == None:
					if self.blackCastleQueenside == True:
						self.doMove((7,4),(7,3))
						if not self.kingInCheck():
							self.movelist.append('O-O-O')
						self.whiteTurn = not self.whiteTurn
						self.boardData = copy.deepcopy(boardDataCopy)
				if self.boardData.get((7,5)) == None and self.boardData.get((7,6)) == None:
					if self.blackCastleKingside == True:
						self.doMove((7,4),(7,5))
						if not self.kingInCheck():
							self.movelist.append('O-O')
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

		for move1, move2 in itertools.combinations(movelist, 2):
			if move1[0] == move2[0] and move1[-2:] == move2[-2:] and move1[0].isupper():
				pass


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

	def doMove(self, move):
		pass

	@staticmethod
	def convertToSquare(square):		# Takes in a tuple board location and outputs the square. (0, 0) becomes 'a1'
		return first8letters[square[1]] + str(square[0] + 1)

class Rook(object):
	pieceCode = 0
	pieceRange = 7
	directions = [[1,0], [-1,0], [0,1], [0,-1]]
	def __init__(self, color):
		self.color = color

	def stringify(self):
		if self.color == 'White':
			return 'R'
		else:
			return 'r'

class Knight(object):
	pieceRange = 1
	pieceCode = 1
	directions = [[1,2], [-1,2], [-2,1], [-2,-1], [-1,-2], [1,-2], [2,-1], [2,1]]
	def __init__(self, color):
		self.color = color

	def stringify(self):
		if self.color == 'White':
			return 'N'
		else:
			return 'n'
		
class Bishop(object):
	pieceRange = 7
	pieceCode = 2
	directions = [[1,1], [-1,1], [-1,-1], [1,-1]]
	def __init__(self, color):
		self.color = color

	def stringify(self):
		if self.color == 'White':
			return 'B'
		else:
			return 'b'

class Queen(object):
	pieceRange = 7
	pieceCode = 3
	directions = [[1,1], [-1,1], [-1,-1], [1,-1], [1,0], [-1,0], [0,1], [0,-1]]
	def __init__(self, color):
		self.color = color

	def stringify(self):
		if self.color == 'White':
			return 'Q'
		else:
			return 'q'
		
class King(object):
	pieceRange = 1
	pieceCode = 4
	directions = [[1,1], [-1,1], [-1,-1], [1,-1], [1,0], [-1,0], [0,1], [0,-1]]
	def __init__(self, color):
		self.color = color

	def stringify(self):
		if self.color == 'White':
			return 'K'
		else:
			return 'k'

class Pawn(object):
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
			return 'P'
		else:
			return 'p'

		

board = Board(1)

board.drawBoard()



# while not board.gameOver:	
# 	board.getMoveList()
# 	board.doMove(board.getMoveInput())
# 	board.drawBoard()
# 	if board.kingInCheck(): print('check') 

# print('Game Over!')