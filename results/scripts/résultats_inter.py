import os
import re
import funcs
import loggers as lg
import memory as Memory
from model import Residual_CNN, CNN
import config
from game import Game, GameState
from agent import Agent
import matplotlib.pyplot as plt
import pickle
import initialise

def grp(pat, txt):
    r = re.search(pat, txt)
    return r.group(0) if r else '&'

env = Game()

# create an untrained neural network objects from the config file
player1_NN = CNN(config.REG_CONST, config.LEARNING_RATE, (2,) + env.grid_shape,   env.action_size, config.HIDDEN_CNN_LAYERS)
player2_NN = Residual_CNN(config.REG_CONST, config.LEARNING_RATE, (2,) +  env.grid_shape,   env.action_size, config.HIDDEN_CNN_LAYERS)

path1 = './run/models/'
path3 =  './Versions/'
path2 = './results/figures/inter_architecture3/'
EPISODES = 5
version_list_CNN = os.listdir(path1)
version_list_CNN.sort(key=lambda l: grp('(0-9+)', l))

version_list_Res = os.listdir(path3)
version_list_Res.sort(key=lambda l: grp('(0-9+)', l))

keys1 = [i for i in range(len(version_list_CNN))]
#keys2 = [i for i in range(len(version_list_Res))]
values1 = [0]*len(version_list_CNN)
#values2 = [0]*10
points1_dict = dict(zip(keys1, values1))
#points2_dict = dict(zip(keys2, values2))

j=0

# Each versions will play 5 games against each other versions.
for player_idx, _ in enumerate(version_list_CNN):
    for opponent_idx, _ in enumerate(version_list_Res):
        if player_idx != opponent_idx:
            continue
        else:
            m_tmp = player1_NN.read(initialise.INITIAL_RUN_NUMBER, player_idx + 1)
            player1_NN.model.set_weights(m_tmp.get_weights())
            player1 = Agent('player1', env.state_size, env.action_size, config.MCTS_SIMS, config.CPUCT, player1_NN)

            m_tmp = player2_NN.read(initialise.INITIAL_RUN_NUMBER, opponent_idx + 1)
            player2_NN.model.set_weights(m_tmp.get_weights())
            player2 = Agent('player2', env.state_size, env.action_size, config.MCTS_SIMS, config.CPUCT, player2_NN)

            scores, memory, points, sp_scores = funcs.playMatches(player1, player2, EPISODES, lg.logger_main,
            turns_until_tau0 = 0, goes_first=1
            )
            print('\n')
            print('-------')
            print('player1: version {}'.format(player_idx))
            print('player2: version {}'.format(opponent_idx))
            print('\nSCORES')
            print(scores)
            print('\nSTARTING PLAYER / NON-STARTING PLAYER SCORES')
            print(sp_scores)
            print(points)
            points1_dict[player_idx] += sum(points[player1.name])
            #points2_dict[opponent_idx] += sum(points[player2.name])
            plt.figure()
            plt.plot(points1_dict.keys(), points1_dict.values(), 'bo', markersize=10, label='CNN')
            plt.plot(points1_dict.keys(), points1_dict.values(), 'b-', lw=2)
            plt.grid()
            plt.xlabel('Versions')
            plt.ylabel('Points')
            plt.legend()
            plt.title('Compétitions inter-architecture')
            plt.savefig(path2 + 'inter_{}.png'.format(j))
            j+=1

