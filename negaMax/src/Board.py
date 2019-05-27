#!/usr/bin/env python
# -*- coding: utf-8 -*-
from negaMax.src.Zobrist_hashing import ZobristHash
import random

try:
    from termcolor import colored
    colored_imported = True
except ImportError:
    colored_imported = False

class Board:
    """Game board for Connect 4"""
    def __init__(self, width=7, height=6):
        self.width = width
        self.height = height
        self.board = self.__build_board()
        self.undo_stack = []
        self.segment_indexes = self.__segment_indexes()
        self.__segment_indexes_by_index = self.__segment_indexes_by_index()
        self.zod_table = self.instantiate_random_64_bit_integer()
        self.previous_move = {
            "player" : "X",
            "row" : 0,
            "column" : 0
        }
        self.current_player = self.__current_player()
        self.current_hash = 0
        self.action_list = []

    #Calls must be made as Board[y][x]
    def __build_board(self):
        return [[' ' for x in range(self.width)] for y in range(self.height)]

    def __update_previous_move(self, curr_sign, row, column):
        self.previous_move = {
            "player" : curr_sign,
            "row" : row,
            "column" : column
        }
        return self.previous_move

    def try_place_piece(self, move):
        """Tries to put piece to board. Returns True if move is possible and row the piece was put"""
        self.__update_current_player()
        for i in range(len(self.board)):
            row = self.height - i - 1   # Pieces are added from bottom to up
            if self.board[row][move-1] == ' ':
                self.board[row][move-1] = self.current_player
                self.undo_stack.append(self.__update_previous_move(curr_sign=self.current_player,
                                                                   row=row,
                                                                   column=move - 1))

                return True, row

        return False, None
    
    def act(self, move, current_sign):
        self.__update_current_player()
        for i in range(self.height):
            row = self.height - i - 1   # Pieces are added from bottom to up
            if self.board[row][move] == ' ':
                self.board[row][move] = current_sign
                break
        self.action_list.append({"player": current_sign, "row":row, "column":move})
        
    def undo_action(self):
        last_action = self.action_list.pop()
        if self.board[last_action["row"]][last_action["column"]] != ' ':
            self.board[last_action["row"]][last_action["column"]] = ' '
        self.current_player = self.__current_player()
        self.previous_move = self.action_list[-1] # TODO change this implementation, high risk of failing
        
    def undo(self):
        while True:
            try:
                value = self.undo_stack.pop()
            except IndexError:
                break
            if self.board[value["row"]][value["column"]] != ' ':
                self.board[value["row"]][value["column"]] = ' '
        self.current_player = self.__current_player()
    
    
    def reset_board(self):
        self.board = self.__build_board()

    def is_game_over(self):
        # Check if game is over (general case)
        for indexes in self.segment_indexes:
            # indexes contains four board indexes as tuples
            segment = ''.join([self.board[index[0]][index[1]] for index in indexes])

            if segment == 4 * self.current_player:
                return True, self.current_player
            elif segment == 4 * self.opponent_player():
                return True, self.opponent_player()

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

    def number_of_moves_played(self):
        nb_moves = 0
        for row in range(self.height):
            for column in range(self.width):
                if self.board[row][column] != ' ':
                    nb_moves += 1
        return nb_moves

    def __current_player(self):
        if self.number_of_moves_played() % 2 == 1:
            return "O"
        else:
            return "X"

    def opponent_player(self):
        if self.current_player == "X":
            return "O"
        else:
            return "X"

    def __update_current_player(self):
        if self.current_player == "X":
            self.current_player = "O"
        else:
            self.current_player = "X"


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

    def instantiate_random_64_bit_integer(self):
        # Return a random integer of 64 bits max for each cells in the board
        random.seed(31415926)
        return [[[random.randint(1, 2 ** 64 - 1)
                  for column in range(self.width)]
                    for row in range(self.height)]
                     for player in range(2)] # For the two players


    def __hash__(self):
        z_hash = ZobristHash(board=self.board,
                           zod_table=self.zod_table,
                           previous_hash=self.current_hash,
                           move_index=self.previous_move
                           )
        self.current_hash = z_hash.compute_hash()
        return self.current_hash

