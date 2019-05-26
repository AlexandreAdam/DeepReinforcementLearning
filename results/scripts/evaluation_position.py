import os
import re
import funcs
import loggers as lg
import memory as Memory
from model import Residual_CNN
import config
from game import Game, GameState
from agent import Agent
import matplotlib.pyplot as plt
import pickle
import numpy as np
import initialise

def grp(pat, txt):
    r = re.search(pat, txt)
    return r.group(0) if r else '&'

color = ['b', 'r', 'c', 'm', 'g']

env = Game()
# create an untrained neural network objects from the config file
player1_NN = Residual_CNN(config.REG_CONST, config.LEARNING_RATE, (2,) + env.grid_shape,   env.action_size, config.HIDDEN_CNN_LAYERS)
# player2_NN = CNN(config.REG_CONST, config.LEARNING_RATE, (2,) +  env.grid_shape,   env.action_size, config.HIDDEN_CNN_LAYERS)

path1 = './run/models/'
path3 =  './Versions/'
path2 = './results/figures/valeur_double_menace/'
EPISODES = 5
try:
    os.mkdir(path2)
except:
    pass

version_list_CNN = os.listdir(path1)
version_list_CNN.sort(key=lambda l: grp('(0-9+)', l))

version_list_Res = os.listdir(path3)
version_list_Res.sort(key=lambda l: grp('(0-9+)', l))
keys = [i for i in range(len(version_list_CNN))]
values = [0]*len(version_list_CNN)
move37 = dict(zip(keys, values))
# value2_dict = dict(zip(keys, values))
move40 = move37.copy()
move41 = move37.copy()
move38 = move37.copy()
move39 = move41.copy()

all_dict = [move38, move39, move41, move37, move40]
moves = ['24', '32', '41', '37', '40']
j=0

state = GameState(np.array([0,0,0,0,0,0,0,
                            0,0,0,0,0,0,0,
                            0,0,0,0,0,0,0,
                            0,0,0,0,0,0,0,
                            0,0,0,-1,-1,0,0,
                            0,0,0,1,1,0,0], dtype=np.int), 1)

# Each versions must predict the best move, we plot the prediction score against the version number
for player_idx, _ in enumerate(version_list_CNN):
        m_tmp = player1_NN.read(initialise.INITIAL_RUN_NUMBER, player_idx + 1)
        player1_NN.model.set_weights(m_tmp.get_weights())
        player1 = Agent('player1', env.state_size, env.action_size, config.MCTS_SIMS, config.CPUCT, player1_NN)

        # m_tmp = player2_NN.read(initialise.INITIAL_RUN_NUMBER, player_idx + 1)
        # player2_NN.model.set_weights(m_tmp.get_weights())
        # player2 = Agent('player2', env.state_size, env.action_size, config.MCTS_SIMS, config.CPUCT, player2_NN)

        move37[player_idx] = player1.get_preds(state)[0]
        # move40[player_idx] = player1.get_preds(state)[1][40]
        # move41[player_idx] = player1.get_preds(state)[1][41]
        # move38[player_idx] = player1.get_preds(state)[1][24]
        # move39[player_idx] = player1.get_preds(state)[1][32]

        plt.figure()
        # for i, stats in enumerate(all_dict):
        #         plt.plot(move37.keys(), all_dict[i].values(), 'o', color=color[i], markersize=10, label=moves[i])
        #         plt.plot(move37.keys(), all_dict[i].values(), '-', color=color[i], lw=2)
        plt.plot(move37.keys(), move37.values(), 'bo', markersize=10)
        plt.plot(move37.keys(), move37.values(), 'b-', lw=2)
        plt.grid()
        plt.xlabel('Versions')
        plt.ylabel(r'$\nu$')
        plt.title("Valeur devant une double menace (coup gagnant)")
        plt.savefig(path2 + 'valeur_double_menace_{}.png'.format(j))
        j+=1

