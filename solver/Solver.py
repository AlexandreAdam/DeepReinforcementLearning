from solver.Node import Node
import numpy as np



class Solver:

    def __init__(self, gamestate):

        # Initial properties and state
        self.shape = gamestate.shape
        self.board = gamestate.board
        self.player_turn = gamestate.playerTurn
        self.total_moves = gamestate.total_moves
        self.nodes_explored = 0


        # Get binary representation of the position and mask from the board
        self.position, self.mask = self.get_binary_rep(self.board, self.player_turn)

        # Define exploration order of columns to increase pruning
        self.exploration_order = [None for x in range(self.shape[1])]
        for column in range(len(self.exploration_order)):
            self.exploration_order[column] = self.shape[1]//2 + (1-2*(column % 2)) * (column+1)//2

        self.root_node = Node(self.position, self.mask, self.total_moves, self.shape)

    def get_binary_rep(self, board, player_turn):

        # Initialize
        mask, position = np.zeros(board.size, dtype=int), np.zeros(board.size, dtype=int)

        # Fill the mask and position
        mask[np.where(board != 0)[0]] = 1
        position[np.where(board == player_turn)[0]] = 1

        mask = mask.reshape(self.shape)
        position = position.reshape(self.shape)

        # Add the ghost row
        mask = np.insert(mask, 0, np.zeros(self.shape[1]), axis=0)
        position = np.insert(position, 0, np.zeros(self.shape[1]), axis=0)

        # Transpose the mask and position (Dynamic4 representation is the flipped transpose of the Node representation)
        mask = np.flip(mask, axis=1).transpose().reshape((self.shape[0]+1)*self.shape[1])
        position = np.flip(position, axis=1).transpose().reshape((self.shape[0]+1)*self.shape[1])

        # Return the binary representation of the position and mask
        return int(''.join(map(str, position)), 2), int(''.join(map(str, mask)), 2)

    def solve(self, node, weak=False):
        if weak:
            return self.negamax(node, -1, 1)
        else:
            return self.negamax(node, -float('inf'), float('inf'))

    def negamax(self, node, alpha, beta):

        self.nodes_explored += 1

        # Check for draw game
        if node.total_moves == node.WIDTH * node.HEIGHT:
            return 0

        # Check if the current node is a leaf
        for column_nb in range(node.WIDTH):
            column_nb = self.exploration_order[column_nb]
            if node.can_play(column_nb) and node.is_winning_move(column_nb):
                return (node.WIDTH * node.HEIGHT + 1 - node.total_moves) // 2

        # Compute maximum and minimum possible scores for pruning
        # min_potential = (node.WIDTH * node.HEIGHT - 2 - node.total_moves) // 2
        max_potential = (node.WIDTH * node.HEIGHT - 1 - node.total_moves) // 2

        # # Min pruning
        # if alpha < min_potential:
        #     alpha = min_potential
        #     if alpha >= beta:
        #         return alpha

        # Max pruning
        if beta > max_potential:
            beta = max_potential
            if alpha >= beta:
                return beta

        for column_nb in range(node.WIDTH):
            column_nb = self.exploration_order[column_nb]

            if node.can_play(column_nb):
                # Create a new Node (copy of current), play the column and get the score
                next_node = Node(position=node.position, mask=node.mask, total_moves=node.total_moves, shape=node.shape)
                next_node.play(column_nb)
                score = -self.negamax(next_node, -beta, -alpha)
                #print(score)

                if score >= beta:
                    return score
                if score > alpha:
                    alpha = score

        return alpha
