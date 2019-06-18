from solver.Node import Node
import numpy as np


class Solver:

    def __init__(self, gamestate):

        # Initial properties and state
        self.shape = gamestate.shape
        self.board = gamestate.board
        self.player_turn = gamestate.playerTurn
        self.total_moves = gamestate.total_moves

        # Get binary representation of the position and mask from the board
        self.position, self.mask = self.get_binary_rep(self.board, self.player_turn)

        # Define exploration order of columns to increase pruning
        self.exploration_order = [None for x in range(self.shape[1])]
        for column in range(len(self.exploration_order)):
            self.exploration_order[column] = self.shape[1]//2 + (1-2*(column % 2)) * (column+1)//2

        self.root_node = Node(self.position, self.mask, self.total_moves)

    @staticmethod
    def get_binary_rep(board, player_turn):
        # Initialize
        mask, position = np.zeros(board.size, dtype=int), np.zeros(board.size, dtype=int)

        # Fill the mask and position
        mask[np.where(board != 0)[0]], position[np.where(board == player_turn)[0]] = 1, 1

        mask = bin(int(''.join(map(str, mask)), 2))
        position = bin(int(''.join(map(str, position)), 2))

        return int(position, 2), int(mask, 2)

    # TO DEBUG
    def negamax(self, node, alpha, beta):

        # Check for draw game
        if node.total_moves == node.WIDTH * node.HEIGHT:
            return 0

        for column_nb in range(node.WIDTH):
            column_nb = self.exploration_order[column_nb]
            if node.can_play(column_nb) and node.is_winning_move:
                return node.WIDTH*node.HEIGHT+1 - node.total_moves/2

        max_potential = node.WIDTH*node.HEIGHT-1 - node.total_moves/2

        if beta > max_potential:
            beta = max_potential
            if alpha >= beta:
                return beta

        for column_nb in range(node.WIDTH):
            column_nb = self.exploration_order[column_nb]
            if node.can_play(column_nb):

                # THE MASK MUST BE INVERTED EVERY TIME THE PLAYER TURN CHANGES? NOT DONE YET ?????
                next_node = Node(position=node.position, mask=node.mask, shape=node.shape, connect_size=node.connect_size)
                next_node.play(column_nb)
                score = -self.negamax(next_node, -beta, -alpha)
                if score >= beta:
                    return score
                if score > alpha:
                    alpha = -score

        return alpha
