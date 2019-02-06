from Negamax import Negamax
from Negamax import Board
from game import Game
import config
import initialise
from model import Residual_CNN
from agent import Agent
import numpy as np

class ZvNMatch:

    '''
    Upon instantiating the object, a series of matches takes place between a certain model of AlphaGo Zero and the
    negaMax variant of the heuristic min max solution to Connect4.

    '''
    def __init__(self, pathToZeroModel, nbMatches, negaMaxDepth = 6):

        self.pathToZeroModel = pathToZeroModel

        #Determines both probability of choosing correct move and time to complete.
        self.negaMaxDepth = negaMaxDepth

        # environments
        self.resetEnvs()

        #Players
        self.zeroPlayer = Residual_CNN(config.REG_CONST, config.LEARNING_RATE, (2,) + self.zeroEnv.grid_shape,   self.zeroEnv.action_size, config.HIDDEN_CNN_LAYERS)
        self.negaPlayer = Negamax(self.negaEnv)

        #Setting weights and initiating agent.
        m_tmp = self.zeroPlayer.read(initialise.INITIAL_RUN_NUMBER, 37)
        self.zeroPlayer.model.set_weights(m_tmp.get_weights())
        self.zeroPlayer = Agent('player1', self.zeroEnv.state_size, self.zeroEnv.action_size, config.MCTS_SIMS, config.CPUCT, self.zeroPlayer)


        self.results = 0

        #Playing matches
        for x in range(nbMatches):
            self.results += self.playMatch()
            self.resetEnvs()

    def resetEnvs(self):
        self.zeroEnv = Game() #Player 1 (or "+")
        self.negaEnv = Board() #Player 2 (or "-")

    #Plays a match and returns the results.
    def playMatch(self):

        matchEnded = False
        while not matchEnded:
        #for x in range(10):

            #Player 1 (+) chooses
            (action, pi, value, NN_value) = self.zeroPlayer.act(self.zeroEnv.gameState, 0)
            print("Zero (1/+) plays cell number: ", action)

            #Player 1 acts on both grids
            self.zeroEnv.step(action)
            self.negaEnv.board[action // self.negaEnv.width][action%self.negaEnv.width] = '+'

            #Check if Zero player wins
            if self.zeroEnv.gameState._checkForEndGame():
                if np.count_nonzero(self.zeroEnv.gameState.board) == 42:
                    return 0
                else:
                    return 1

            #Player 2 (-) chooses
            self.negaPlayer = Negamax(self.negaEnv, self.negaMaxDepth)
            move = self.negaPlayer.calculate_move(self.negaEnv, "-", "+")

            #Player 2 acts on both grids
            self.negaEnv.try_place_piece(move, "-")

            #Must convert row to action
            print("Nega (-1, -) plays column: ", move)
            for y in range(6, 0, -1):
                if self.zeroEnv.gameState.board[7*(y-1)+move-1] == 0:
                    self.zeroEnv.step(7*(y-1)+move-1)
                    break

            #Check if Negamaz player wins
            if self.zeroEnv.gameState._checkForEndGame():
                if np.count_nonzero(self.zeroEnv.gameState.board) == 42:
                    return 0
                else:
                    return -1

            #Is the action the cell number or the index or that cell in the list of cells in zeroEnv?
            print(self.zeroEnv.gameState.board)
            for x in self.negaEnv.board:
                print(x)

matches = ZvNMatch( "Models/Model_1/Versions/version0037.h5", 1,6)
print(matches.results)