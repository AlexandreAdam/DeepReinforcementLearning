from dynamic4 import DynamicGame
from solver.Solver import Solver
import numpy as np
from time import time


'''
    These unit tests assume that both players play perfectly. The optimal move is known in each test case.
    
    Connect 4 grid
    This grid defines the cell number (or action)
    Dynamic4 uses a flattened version of this grid as a board representation.
    This is the represenation used by the AlphaGo Zero model.
    +---------------------+
    | 0  1  2  3  4  5  6 |
    | 7  8  9 10 11 12 13 |
    |14 15 16 17 18 19 20 |
    |21 22 23 24 25 26 27 |
    |28 29 30 31 32 33 34 |
    |35 36 37 38 39 40 41 |
    +---------------------+
    
    Binary grid
    The numbers represent the position of each cell in the binary representation
    For example, cell #0 occupies the fifth less significant bit.
    This is the representation used by the Connect4 Solver.
    +---------------------+
    | 5 12 19 26 33 40 47 |
    | 4 11 18 25 32 39 46 |
    | 3 10 17 24 31 38 45 |
    | 2  9 16 23 30 37 44 |
    | 1  8 15 22 29 36 43 |
    | 0  7 14 21 28 35 42 |
    +---------------------+
'''


# Validates binary representations by filling the board horizontally and vertically.
# Validates can_play() on empty and full board.
# Validates play() method implicitly.
def fill_position_mask(shape=(6, 7)):

    print('|----------------------------------------------------------------------------|')
    print(' TEST OBJECTIVE: test binary representation of grid of', shape, 'shape')

    # Start with an empty board and node
    game = DynamicGame(grid_shape=shape)
    solver = Solver(game.gameState)
    node = solver.root_node

    # Node should be empty
    assert (node.position == 0 and node.mask == 0)

    # Every column should be playable
    for col in range(node.WIDTH):
        assert (node.can_play(col))

    # Move sequence (row, col)
    move_order_h = []
    move_order_v = []

    # Fill the board left to right, bottom to top
    for row in range(node.HEIGHT):
        for col in range(node.WIDTH):
            move_order_h.append((row, col))

    # Fill the board bottom to top, lef to right
    for col in range(node.WIDTH):
        for row in range(node.HEIGHT):
            move_order_v.append((row, col))

    for i in range(0, 2):

        solver = Solver(game.gameState)
        node = solver.root_node
        played_cells = []

        if i == 0:
            moves = move_order_h
        else:
            moves = move_order_v

        for row, col in moves:

            # Current player plays a move
            played_cells.append(col * (node.HEIGHT + 1) + row)
            node.play(col)

            # Compute what should be position of the current player
            expected_position = 0
            for idx, cell in enumerate(played_cells):

                # It is the starting players turn
                if node.total_moves % 2 == 0:
                    if idx % 2 == 0:
                        expected_position += 2 ** cell

                # It is the second players turn
                else:
                    if idx % 2 == 1:
                        expected_position += 2 ** cell

            # The value of the position is the sum of 2**cell for all cell played by the current player.
            assert (node.position == expected_position)

            # The value of the mask is the sum of 2**cell for all cell played.
            assert (node.mask == sum(map(lambda x: 2 ** x, played_cells)))

        # Node should be full at this point and have no legal moves left
        for col in range(node.WIDTH):
            assert (not node.can_play(col))

    print('\n TEST SUCCESSFUL')
    print('|----------------------------------------------------------------------------|')


# Validates all possible positive alignment cases.
def positive_alignments(shape=(6, 7)):

    print('|----------------------------------------------------------------------------|')
    print(' TEST OBJECTIVE: test all possible alignments in grid of', shape, 'shape')

    # Start with an empty board and node
    game = DynamicGame(shape)
    solver = Solver(game.gameState)
    node = solver.root_node

    # Binary values leading to the victory of the first player or second
    winners = []

    index = np.flip(np.arange(0, node.WIDTH * (node.HEIGHT + 1), dtype=np.int64)
                    .reshape((node.WIDTH, (node.HEIGHT + 1))), axis=1).transpose()

    # Vertical alignments are possible
    if shape[0] >= 4:
        for col in range(node.WIDTH):
            for row in range(1, node.HEIGHT - 3):
                winners.append(sum(map(lambda x: 2 ** x, index[row:row + 4, col])))

    # Horizontal alignments are possible
    if shape[1] >= 4:
        for row in range(node.HEIGHT):
            for col in range(node.WIDTH - 4):
                winners.append(sum(map(lambda x: 2 ** x, index[row, col:col + 4])))

    # Diagonal alignments are possible
    if shape[0] >= 4 and shape[1] >= 4:
        for col in range(node.WIDTH - 3):
            for row in range(1, node.HEIGHT - 2):
                indexes = []
                for c in range(4):
                    indexes.append(index[row + c, col + c])
                winners.append(sum(map(lambda x: 2 ** x, indexes)))

        for col in range(node.WIDTH - 4, -1, -1):
            for row in range(node.HEIGHT - 3, 0, -1):
                indexes = []
                for c in range(4):
                    indexes.append(index[row + c, col + c])
                winners.append(sum(map(lambda x: 2 ** x, indexes)))

    for winner in winners:
        assert (node.alignment(winner))

    print('\n TEST SUCCESSFUL')
    print('|----------------------------------------------------------------------------|')


# Validates negative alignments (lack thereof).
# Validates is_winning_move method.
def negative_alignments():
    pass


# The first player has successfully set up a double menace and is guaranteed to win in two moves.
# Takes a few seconds to compute.
def double_menace():

    print('|----------------------------------------------------------------------------|')
    print(' TEST OBJECTIVE: complete the double menace\n')

    start_time = time()

    shape = (4, 5)
    sequence = [18, 13, 17, 12]

    game = DynamicGame(grid_shape=shape)

    for action in sequence:
        game.step(action)

    print('Initial state: \n', game)

    total_nodes = 0

    for x in range(3):
        solver = Solver(game.gameState)
        game.step(solver.get_action())
        total_nodes += solver.nodes_explored
        print('\n', game)

    end_time = time()

    assert (game.gameState.board[16] == 1 and game.gameState.board[15] == 1)

    print('\n TEST SUCCESSFUL:', total_nodes, ' nodes explored in ', round(end_time-start_time, 2), 'seconds.')
    print('|----------------------------------------------------------------------------|')


# The first player is trying to set up a double menace.
# The second player must counter it at this turn or he is guaranteed to lose.
# Takes a few seconds to compute.
def counter_double_menace():

    print('|----------------------------------------------------------------------------|')
    print(' TEST OBJECTIVE: counter the double menace\n')

    start_time = time()

    shape = (4, 5)
    sequence = [18, 13, 17]

    game = DynamicGame(grid_shape=shape)

    for action in sequence:
        game.step(action)

    print('Initial state: \n', game)

    solver = Solver(game.gameState)
    game.step(solver.get_action())
    print('\n', game)

    end_time = time()

    assert (game.gameState.board[16] == -1)

    print('\n TEST SUCCESSFUL:', solver.nodes_explored, 'nodes explored in ', round(end_time-start_time, 2), 'seconds.')
    print('|----------------------------------------------------------------------------|')


# The first player has to choose his first move.
# Takes about 3 minutes to compute.
def first_move():

    print('|----------------------------------------------------------------------------|')
    print(' TEST OBJECTIVE: choose the optimal first move\n')

    start_time = time()

    shape = (4, 5)
    game = DynamicGame(grid_shape=shape)

    print('\n', game)
    solver = Solver(game.gameState)
    game.step(solver.get_action())

    end_time = time()

    assert (game.gameState.board[17] == 1)

    print('\n TEST SUCCESSFUL:', solver.nodes_explored, 'nodes explored in ', round(end_time-start_time, 2), 'seconds.')
    print('|----------------------------------------------------------------------------|')


if __name__ == '__main__':
    test_shapes = [(2, 6), (4, 6), (6, 6), (2, 7), (4, 7), (6, 7)]

    for test_shape in test_shapes:
        fill_position_mask(test_shape)
        positive_alignments(test_shape)

    double_menace()
    counter_double_menace()
    first_move()
