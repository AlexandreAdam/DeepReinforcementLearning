"""
Implementation of competitions between AlphaGo Zero and alphaMax.
"""

# Third-Party
import numpy as np

# Local
import config
import initialise
from negaMax.src.AlphaBeta import AlphaBeta
from negaMax.src.Board import Board
from model import Residual_CNN
from agent import Agent
from dynamic4 import DynamicGameState, Game


class ZvNMatch:

    '''
    Upon instantiating the object, a series of matches takes place between a certain model of AlphaGo Zero and the
    alphaMax variant of the heuristic min max solution to Connect4.
    '''

    def __init__(self, model_number, nbMatches, alphaMaxDepth=4):

        # Determines both probability of choosing correct move and time to complete.
        self.alphaMaxDepth = alphaMaxDepth

        # Environments
        self.zeroEnv, self.alphaEnv = None, None
        self.reset_envs()
        
        # Players
        self.zeroPlayer = Residual_CNN(config.REG_CONST, config.LEARNING_RATE, (2,) + self.zeroEnv.grid_shape,   self.zeroEnv.action_size, config.HIDDEN_CNN_LAYERS)
        self.alphaPlayer = AlphaBeta(board=self.alphaEnv, max_depth=alphaMaxDepth)

        # Setting weights and initiating agent.
        m_tmp = self.zeroPlayer.read(initialise.INITIAL_RUN_NUMBER, model_number)
        self.zeroPlayer.model.set_weights(m_tmp.get_weights())
        self.zeroPlayer = Agent('player1', self.zeroEnv.state_size, self.zeroEnv.action_size, config.MCTS_SIMS, config.CPUCT, self.zeroPlayer)

        self.results = 0

        # Playing matches
        for x in range(nbMatches):
            self.results += self.playMatch()
            self.reset_envs()

    def reset_envs(self):
        self.zeroEnv = Game() #Player 1 (or "X")
        self.alphaEnv = Board() #Player 2 (or "O")

    # Plays a match and returns the results.
    def playMatch(self):

        matchEnded = False

        while not matchEnded:

            # Player 1 (X) chooses
            (action, pi, value, NN_value) = self.zeroPlayer.act(self.zeroEnv.gameState, 0)
            #print("Zero (1, +) plays cell number: ", action)

            # Player 1 acts on both grids
            self.zeroEnv.step(action)
            move = action % self.alphaEnv.width
            self.alphaEnv.act(move, current_sign="X")
            print("AlphaZero turn")
            print(self.alphaEnv)

            # Check if Zero player wins
            if self.zeroEnv.gameState._checkForEndGame():
                if np.count_nonzero(self.zeroEnv.gameState.board) == 42:
                    return 0
                else:
                    return 1

            # Player 2 (O) chooses
            self.alphaPlayer = AlphaBeta(board=self.alphaEnv,  max_depth=self.alphaMaxDepth)
            move = self.alphaPlayer.calculate_move()


            # Player 2 acts on both grids
            self.alphaEnv.act(move, "O")
            print("alphamax turn")
            print(self.alphaEnv)

            # Must convert row to action
            #print("alpha (-1, -) plays column: ", move)
            for y in range(6, 0, -1):
                if self.zeroEnv.gameState.board[7*(y-1)+move-1] == 0:
                    self.zeroEnv.step(7*(y-1)+move-1)
                    break

            # Check if alphamaz player wins
            if self.zeroEnv.gameState._checkForEndGame():
                if np.count_nonzero(self.zeroEnv.gameState.board) == 42:
                    return 0
                else:
                    return -1

            #print(self.zeroEnv.gameState.board)
            #for x in self.alphaEnv.board:
            #    print(x)


for x in range(1, 50):
    print('match:', x)
    matches = ZvNMatch(model_number=str(x), nbMatches=1)
    print(matches.results)
