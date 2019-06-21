from dynamic4 import DynamicGame
from solver.Solver import Solver
from time import time

'''
These unit tests assume that both players play perfectly. The optimal move is known in each test case.
'''


# The first player has successfully set up a double menace and is guaranteed to win in two moves.
# Takes a few seconds to compute.
def double_menace():

    print('|-------------------------------------------------------------|')
    print('TEST OBJECTIVE: complete the double menace\n')

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
    print('|-------------------------------------------------------------|\n')


# The first player is trying to set up a double menace.
# The second player must counter it at this turn or he is guaranteed to lose.
# Takes a few seconds to compute.
def counter_double_menace():

    print('|-------------------------------------------------------------|')
    print('TEST OBJECTIVE: counter the double menace\n')

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

    print('\n TEST SUCCESSFUL:', solver.nodes_explored, ' nodes explored in ', round(end_time-start_time, 2), 'seconds.')
    print('|-------------------------------------------------------------|\n')


# The first player has to choose his first move.
# Takes about 3 minutes to compute.
def first_move():

    print('|-------------------------------------------------------------|')
    print('TEST OBJECTIVE: choose the optimal first move\n')

    start_time = time()

    shape = (4, 5)
    game = DynamicGame(grid_shape=shape)

    print('\n', game)
    solver = Solver(game.gameState)
    game.step(solver.get_action())

    end_time = time()

    assert (game.gameState.board[17] == 1)

    print('\n TEST SUCCESSFUL:', solver.nodes_explored, ' nodes explored in ', round(end_time-start_time, 2), 'seconds.')
    print('|-------------------------------------------------------------|\n')


if __name__ == '__main__':
    # double_menace()
    # counter_double_menace()
    first_move()
