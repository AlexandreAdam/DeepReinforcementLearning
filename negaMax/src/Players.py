#!/usr/bin/env python
# -*- coding: utf-8 -*-
from negaMax.src.Negamax import Negamax
from negaMax.src.AlphaBeta import AlphaBeta, Node
import numpy as np

class HumanPlayer:
    def __init__(self, sign):
        self.sign = sign

    def get_move(self, board, opponent):
        while True:
            move = input()
            if self.__is_valid(move, board):
                break
            #print('Please give a valid column number')

        return int(move)

    @staticmethod
    def __is_valid(move, board):
        try:
            move = int(move)
        except ValueError:
            return False

        return 0 < move <= board.width

#Negamax player
class NegaPlayer:
    def __init__(self, sign, depth):
        self.sign = sign
        self.depth = depth

    def get_move(self, board, opponent):
        n = Negamax(board, self.depth)
        move = n.calculate_move(board, self.sign, opponent.sign)
        return move

class AlphaBetaPlayer:
    def __init__(self, sign, depth):
        self.sign = sign
        self.depth = depth

    def get_move(self, board, opponent):
        origin= Node(board, depth=4, current_player=self.sign)
        alpha_beta = AlphaBeta(board, max_depth=self.depth, origin=origin)

        move = alpha_beta.calculate_move()
        return move
