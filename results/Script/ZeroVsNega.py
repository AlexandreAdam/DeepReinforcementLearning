from Negamax import NegaPlayer
from Negamax import Board
from game import Game
import config
from model import CNN

zeroModelPath = "Models/Models_1/Versions/"


#Determines both probability of choosing correct move and time to complete.
negaMaxDepth = 6

#Environments
zeroEnv = Game() #Player 1 (or "+")
negaEnv = Board() #Player 2 (or "-")

#Players
zeroPlayer = CNN(config.REG_CONST, config.LEARNING_RATE, (2,) + zeroEnv.grid_shape,   zeroEnv.action_size, config.HIDDEN_CNN_LAYERS)
negaPlayer = NegaPlayer(negaEnv, "-", negaMaxDepth)


