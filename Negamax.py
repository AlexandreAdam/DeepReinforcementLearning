#!/usr/bin/env python
# -*- coding: utf-8 -*-

#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from termcolor import colored
    colored_imported = True
except ImportError:
    colored_imported = False

"""This heuristic algorithm is based on negamax, which is a variant of a minimax
algorithm.Negamax can be used due to zero-sum property of Connect-4. Heuristic
algorithm is needed, because Connect Four has around 4*10^12 (4 trillion)
different possible games.
"""

class Negamax:

    '''
    board, 2D Matrix: game layout

    max_depth, Integer: maximum depth visited during Negamax algorithm. Higher values increase probability of selecting
    the correct move. However, the time required by the algorithm evolves exponentially with this parameter.
    '''
    def __init__(self, board, max_depth=4):
        self.__listed_indexes = board.segment_indexes
        self.__weights = [1, 8, 128, 99999]
        self.__max_depth = max_depth
        self.__evaluated = {}

    '''
    Method returns the best move to play (column number from 1-7) and the best score (Integer).
    The board parameter MUST be a Board object. Board objects have a board attribute that represent the gamestate.
    The gamestate is represented as a list in the AlphaGo Zero architecture, while it is represented as a 6x7 matrix 
    in the Negamax architecture. 
    '''
    def __negamax(self, board, curr_sign, opponent_sign, depth=0):

        #The Negamax algorithm operates on a Board type object. If the board passed as parameter is in list ,
        #it must first be converted.
        if isinstance(board, list):
            board = self.convertListToMatrix(board)

        hashed_board = hash(board)

        if hashed_board in self.__evaluated:
            return None, self.__evaluated[hashed_board]

        #Reached maximum allowed depth.
        if depth == self.__max_depth:
            score = self.__evaluate(board.board, curr_sign, opponent_sign)
            self.__evaluated[hashed_board] = score
            return None, score

        best_score = float('-inf')
        best_move = None

        for x in range(1, 8):
            move = x
            move_allowed, row = board.try_place_piece(move, curr_sign)

            if not move_allowed:
                continue

            game_over, winner = board.is_game_over(board.board, curr_sign, opponent_sign, (move-1, row))
            if game_over:
                if winner == curr_sign:
                    best_subscore = 9999999999
                elif winner == opponent_sign:
                    best_subscore = -9999999999
                else:
                    best_subscore = 0
            else:
                best_submove, best_subscore = self.__negamax(board, opponent_sign, curr_sign, depth + 1)
                best_subscore *= -1
            board.undo()

            if best_subscore > best_score:
                best_score = best_subscore
                best_move = move

        # Happens when max_depth exceeds number of possible moves
        if best_move is None:
            best_score = self.__evaluate(board.board, curr_sign, opponent_sign)

        self.__evaluated[hashed_board] = best_score

        return best_move, best_score

    def __evaluate(self, board, curr_sign, opponent_sign):
        """Counts and weighs longest connected checker chains
        which can lead to win"""

        curr_score = 0
        opp_score = 0

        for indexes in self.__listed_indexes:
            # indexes contains four board indexes as tuples

            curr_count = 0
            opp_count = 0

            for index in indexes:
                v = board[index[0]][index[1]]
                if v == curr_sign:
                    curr_count += 1
                elif v == opponent_sign:
                    opp_count += 1

            if curr_count > 0 and opp_count > 0:
                continue
            elif curr_count > 0:
                curr_score += curr_count * self.__weights[curr_count - 1]
            elif opp_count > 0:
                opp_score += opp_count * self.__weights[opp_count - 1]

        difference = curr_score - opp_score

        return difference

    def calculate_move(self, board, curr_sign, opponent_sign):
        move, score = self.__negamax(board, curr_sign, opponent_sign)
        #print(score)
        return move

    '''
    Interface that binds AlphaGo Zero architecture with NegaMax architecture.
    Takes as input a 42 entry list containing 1,0 and -1 and converts it to a 6x7 matrix containing X and Os.
    '''
    def convertListToMatrix(self, board, width = 7, height = 6):

        newBoard = [[' ' for x in range(width)] for y in range(height)]


        if(len(board) == width*height):
            counter = 0
            for x in range(width):
                for y in range(height):
                    if board[counter] is 1:
                        newBoard[y][x] = "X"
                    elif board[counter] is -1:
                        newBoard[y][x] = "O"
                    counter+=1

            return [[' ' for x in range(width)] for y in range(height)]

        else:
            raise ValueError("Length of list cannot be converted to matrix specified width and height (7 and 6 by default).")


# TODO:
#    - Prefer games that win faster or lose later
#


class Board:
    """Game board for Connect 4"""
    def __init__(self, width=7, height=6):
        self.width = width
        self.height = height
        self.board = self.__build_board(width, height)
        self.undo_stack = []
        self.segment_indexes = self.__segment_indexes()
        self.__segment_indexes_by_index = self.__segment_indexes_by_index()

    #Calls must be made as Board[y][x]
    def __build_board(self, width, height):
        return [[' ' for x in range(width)] for y in range(height)]

    def try_place_piece(self, move, curr_sign):
        """Tries to put piece to board. Returns True if move is possible and row the piece was put"""
        for i in range(len(self.board)):
            row = self.height - i - 1   # Pieces are added from bottom to up
            if self.board[row][move-1] == ' ':
                self.board[row][move-1] = curr_sign
                self.undo_stack.append(move - 1)
                return True, row

        return False, None

    def undo(self):
        try:
            value = self.undo_stack.pop()
        except IndexError:
            #print('Nothing to undo')
            return False
        for row in self.board:
            if not row[value] == ' ':
                row[value] = ' '
                return value

    def is_game_over(self, board, curr_sign, opponent_sign, move=None):
        if move:
            # Check if specific move causes game over (specific case)
            col, row = move
            for indexes in self.__segment_indexes_by_index[row * 7 + col]:
                # indexes contains four board indexes as tuples
                segment = ''.join([board[index[0]][index[1]] for index in indexes])

                if segment == 4 * curr_sign:
                    return True, curr_sign
                elif segment == 4 * opponent_sign:
                    return True, opponent_sign
        else:
            # Check if game is over (general case)
            for indexes in self.segment_indexes:
                # indexes contains four board indexes as tuples
                segment = ''.join([self.board[index[0]][index[1]] for index in indexes])

                if segment == 4 * curr_sign:
                    return True, curr_sign
                elif segment == 4 * opponent_sign:
                    return True, opponent_sign

        if not self.__is_legal_moves_left():
            # If tie game, no winner is returned
            return True, None

        # If game is not over, no winner is returned
        return False, None

    def __segment_indexes(self):

        # Get indexes from rows, columns and diagonal lines and combine them to segments
        rows = [[(y, x) for x in range(self.width)] for y in range(self.height)]
        columns = [[(x, y) for x in range(self.height)] for y in range(self.width)]

        up = [[(x, y) for x in range(self.height) for y in range(self.width)
               if x + y == z] for z in range(3, 9)]
        down = [[(x, y) for x in range(self.height) for y in range(self.width)
                 if x - y == z] for z in range(-3, 3)]

        segments = rows + columns + up + down

        # Split segments to smaller, 4 length pieces
        # These are every possible chain of four in the game
        # Each element in returned list is a list of indexes (which are tuples)

        return [segments[x][i:i+4] for x in range(len(segments)) for i in range(len(segments[x])-3)]

    def __segment_indexes_by_index(self):
        segment_indexes_by_index = [[] for x in range(self.width * self.height)]
        for col in range(self.width):
            for row in range(self.height):
                for index in self.segment_indexes:
                    if (col, row) in index:
                        segment_indexes_by_index[col*7 + row].append(index)

        return segment_indexes_by_index

    def __is_legal_moves_left(self, board=None):
        if board is None:
            board = self.board
        return ' ' in [board[0][x] for x in range(self.width)]

    def __str__(self):
        numbers = [str(x) for x in range(1, self.width + 1)]
        if colored_imported:
            print(colored(' ' + ' '.join(numbers), 'cyan'))
        else:
            print(' ' + ' '.join(numbers))

        s = ''
        for row in self.board:
            if colored_imported:
                s += colored('|', 'red') + colored('|', 'red').join(row) + colored('|\n', 'red')
            else:
                s += '|' + '|'.join(row) + '|\n'

        return s

    def __hash__(self):
        tmp = str(self.board)
        return hash(tmp)



#Create empty board
board = Board()

#Create solver object
nega = Negamax(board)

#Ask solver for next move.
print(nega.calculate_move(board, "+", "+"))
