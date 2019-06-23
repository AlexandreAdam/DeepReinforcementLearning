from solver.Node import Node
import numpy as np


class Solver:

    """
    Dynamic4 solver. Can be perfect or not depending on depth parameter.
    """

    def __init__(self, gamestate):

        # Initial properties and state
        self.shape = gamestate.shape
        self.board = gamestate.board
        self.player_turn = gamestate.playerTurn
        self.total_moves = gamestate.total_moves
        self.nodes_explored = 0

        # Get binary representation of the position and mask from the board
        self.position, self.mask = self.get_binary_rep(self.board, self.player_turn)

        # Root node
        self.root_node = Node(self.position, self.mask, self.total_moves, self.shape)

        # Define exploration order of columns to increase pruning
        self.exploration_order = [None for x in range(self.shape[1])]
        for column in range(len(self.exploration_order)):
            self.exploration_order[column] = self.shape[1]//2 + (1-2*(column % 2)) * (column+1)//2

    # Convert board attribute (numpy.ndarray) to single integer (binary representation)
    def get_binary_rep(self, board, player_turn):

        # Initialize
        mask, position = np.zeros(board.size, dtype=np.int64), np.zeros(board.size, dtype=np.int64)

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

    # Returns best column to play. Only works for root node given to constructor.
    def get_col(self):
        scores = np.array([self.player_turn*-99999999] * self.root_node.WIDTH, dtype=int)

        for column_nb in range(self.root_node.WIDTH):
            if self.root_node.can_play(column_nb):

                # Create and update child Node
                next_node = Node(position=self.root_node.position, mask=self.root_node.mask,
                                 total_moves=self.root_node.total_moves, shape=self.root_node.shape)
                next_node.play(column_nb)
                scores[column_nb] = self.negamax(node=next_node, color=-self.player_turn)

        if self.player_turn == -1:
            best_scores = np.where(scores == np.amin(scores))[0]
        else:
            best_scores = np.where(scores == np.amax(scores))[0]

        # If more than one column have the same score, pick one at random
        best_col = int(np.random.choice(best_scores, 1)[0])

        return best_col

    # Returns best action to play. Only works for root node given to constructor.
    def get_action(self):
        best_column = self.get_col()

        # Convert column to action
        for y in range(self.shape[0]-1, -1, -1):
            if self.board[y*self.shape[1] + best_column] == 0:
                return y*self.shape[1] + best_column

    def negamax(self, node, alpha=-float('inf'), beta=float('inf'), color=1, depth=float('inf')):

        self.nodes_explored += 1

        # Base case 1 (Depth)
        if depth <= 0:
            return 0  # TO ADD HEURISTIC FUNCTION HERE

        # Base case 2 (Leaf node, draw)
        if node.total_moves == node.WIDTH * node.HEIGHT:
            return 0

        # Base case 3 (Leaf node, victory)
        for column_nb in range(node.WIDTH):
            column_nb = self.exploration_order[column_nb]
            if node.can_play(column_nb) and node.is_winning_move(column_nb):
                return color * ((node.WIDTH * node.HEIGHT - 1 - node.total_moves) // 2)

        value = -float('inf')

        # Recursion on each child
        for column_nb in range(node.WIDTH):
            column_nb = self.exploration_order[column_nb]

            if node.can_play(column_nb):
                # Create and update child Node
                next_node = Node(position=node.position, mask=node.mask, total_moves=node.total_moves, shape=node.shape)
                next_node.play(column_nb)

                # Get the value of the child Node
                value = max(value, -self.negamax(next_node, -beta, -alpha, color=-color, depth=depth-1))

                # Update boundaries
                alpha = max(alpha, value)

                # Pruning
                if alpha >= beta:
                    break

        return value
