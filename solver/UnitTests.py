from dynamic4 import DynamicGame
from solver.Solver import Solver


def double_menace():

    shape = (4, 5)
    sequence = [18, 13, 17, 12]

    game = DynamicGame(grid_shape=shape)

    for action in sequence:
        game.step(action)

    print('Initial state: \n', game)

    game.step(Solver(game.gameState).get_action())
    print('\n', game)
    game.step(Solver(game.gameState).get_action())
    print('\n', game)
    game.step(Solver(game.gameState).get_action())
    print('\n', game)


if __name__ == '__main__':
    double_menace()
