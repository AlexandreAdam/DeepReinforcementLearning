from Negamax import Negamax
from Negamax import Board
from game import Game
import config
import initialise
from model import Residual_CNN
from agent import Agent

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

        #Playing matches
        for x in range(nbMatches):
            results = self.playMatch()
            self.resetEnvs()

    def resetEnvs(self):
        self.zeroEnv = Game() #Player 1 (or "+")
        self.negaEnv = Board() #Player 2 (or "-")

    #Plays a match and returns the results.
    def playMatch(self):

        matchEnded = False
        #while not matchEnded:
        for x in range(3):

            #Is the action the cell number or the index or that cell in the list of cells in zeroEnv?
            print(self.zeroEnv.gameState.board)
            print(self.negaEnv.board)
            #Player 1 (+) acts
            (action, pi, value, NN_value) = self.zeroPlayer.act(self.zeroEnv.gameState, config.TURNS_UNTIL_TAU0 ) #is this the correct tau parameter?
            print("Zero (1/+) plays cell number: ", action) # BUG : ALWAYS CHOOSES 38 (DOES NOT SEE MAP UPDATES FROM PREVIOUS ITER?)
            self.zeroEnv.gameState.board[action] = 1
            self.negaEnv.board[action // self.negaEnv.width][action%self.negaEnv.width] = '+'

            #Player 2 (-) acts
            self.negaPlayer = Negamax(self.negaEnv, self.negaMaxDepth)
            move = self.negaPlayer.calculate_move(self.negaEnv, "-", "+")
            print("Nega (-1, -) plays column: ", move)

            self.negaEnv.try_place_piece(move, "-")

            for y in range(6,0, -1):
                if self.zeroEnv.gameState.board[7*(y-1)+move-1] == 0:
                    self.zeroEnv.gameState.board[7*(y-1)+move-1] = -1
                    break

matches = ZvNMatch( "Models/Model_1/Versions/version0037.h5",1)