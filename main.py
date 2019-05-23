"""
Used to train models.
"""

# Standard
from shutil import copyfile
from importlib import reload
import pickle
import random

# Third-party
import numpy as np
# from keras.utils import plot_model  # Must manually add graphviz distro to ENV PATH to fix plot_model method

# Local
import loggers as lg
import initialise
import config
from game import Game, GameState
from agent import Agent
from memory import Memory
from model import Residual_CNN
from funcs import playMatches, playMatchesBetweenVersions
from settings import run_folder, run_archive_folder
from dynamic4 import DynamicGameState

np.set_printoptions(suppress=True)

# Logger heading
lg.logger_main.info('=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*')
lg.logger_main.info('=*=*=*=*=*=.      NEW LOG      =*=*=*=*=*')
lg.logger_main.info('=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*')

# Game interface
#env = Game()
env = DynamicGameState(shape=config.GRID_SHAPE)

# If loading an existing neural network, copy the config file to root
if initialise.INITIAL_RUN_NUMBER is not None:
    copyfile(run_archive_folder + 'Model_{}'.format(initialise.INITIAL_RUN_NUMBER) + '/config.py', './config.py')

# Load memory if necessary
if initialise.INITIAL_MEMORY_VERSION is None:
    memory = Memory(config.MEMORY_SIZE)
else:
    print('LOADING MEMORY VERSION ' + str(initialise.INITIAL_MEMORY_VERSION) + '...')
    memory = pickle.load(open(run_archive_folder + 'Model_' + str(initialise.INITIAL_RUN_NUMBER)
                              + "/memory/memory" + str(initialise.INITIAL_MEMORY_VERSION).zfill(4) + ".p",   "rb"))

# Create an untrained neural network objects from the config file
current_NN = Residual_CNN(config.REG_CONST, config.LEARNING_RATE, (2,) + env.grid_shape,
                          env.action_size, config.HIDDEN_CNN_LAYERS)
best_NN = Residual_CNN(config.REG_CONST, config.LEARNING_RATE, (2,) + env.grid_shape,
                       env.action_size, config.HIDDEN_CNN_LAYERS)

# Load existing neural network if needed
if initialise.INITIAL_MODEL_VERSION is not None:
    best_player_version = initialise.INITIAL_MODEL_VERSION
    print('LOADING MODEL VERSION ' + str(initialise.INITIAL_MODEL_VERSION) + '...')
    m_tmp = best_NN.read(initialise.INITIAL_RUN_NUMBER, best_player_version)
    current_NN.model.set_weights(m_tmp.get_weights())
    best_NN.model.set_weights(m_tmp.get_weights())

# Otherwise ensure the initial weights are the same for both players
else:
    best_player_version = 0
    best_NN.model.set_weights(current_NN.model.get_weights())


print('\n')
print(current_NN.model.summary())

# Create players
current_player = Agent('current_player', env.state_size, env.action_size, config.MCTS_SIMS, config.CPUCT, current_NN)
best_player = Agent('best_player', env.state_size, env.action_size, config.MCTS_SIMS, config.CPUCT, best_NN)
iteration = 0

print(config.MEMORY_SIZE)

# Training loop
while 1:

    iteration += 1
    reload(lg)
    reload(config)

    print('ITERATION NUMBER ' + str(iteration))

    lg.logger_main.info('BEST PLAYER VERSION: %d', best_player_version)
    print('BEST PLAYER VERSION ' + str(best_player_version))

    # SELF PLAY
    print('SELF PLAYING ' + str(config.EPISODES) + ' EPISODES...')
    _, memory, _, _ = playMatches(best_player, best_player, config.EPISODES, lg.logger_main,
                                  turns_until_tau0=config.TURNS_UNTIL_TAU0, memory=memory)
    print('\n')

    memory.clear_stmemory()

    if len(memory.ltmemory) >= config.MEMORY_SIZE:

        # RETRAINING
        print('RETRAINING...')
        current_player.replay(memory.ltmemory)
        print('')

        if iteration % 5 == 0:
            pickle.dump(memory, open(run_folder + 'Model_' + str(initialise.INITIAL_RUN_NUMBER) +
                                     "/memory/memory" + str(iteration).zfill(4) + ".p", "wb"))

        lg.logger_memory.info('====================')
        lg.logger_memory.info('NEW MEMORIES')
        lg.logger_memory.info('====================')

        memory_samp = random.sample(memory.ltmemory, min(1000, len(memory.ltmemory)))

        for s in memory_samp:
            current_value, current_probs, _ = current_player.get_preds(s['state'])
            best_value, best_probs, _ = best_player.get_preds(s['state'])

            lg.logger_memory.info('MCTS VALUE FOR %s: %f', s['playerTurn'], s['value'])
            lg.logger_memory.info('CUR PRED VALUE FOR %s: %f', s['playerTurn'], current_value)
            lg.logger_memory.info('BES PRED VALUE FOR %s: %f', s['playerTurn'], best_value)
            lg.logger_memory.info('THE MCTS ACTION VALUES: %s', ['%.2f' % elem for elem in s['AV']]  )
            lg.logger_memory.info('CUR PRED ACTION VALUES: %s', ['%.2f' % elem for elem in  current_probs])
            lg.logger_memory.info('BES PRED ACTION VALUES: %s', ['%.2f' % elem for elem in  best_probs])
            lg.logger_memory.info('ID: %s', s['state'].id)
            lg.logger_memory.info('INPUT TO MODEL: %s', current_player.model.convertToModelInput(s['state']))

            s['state'].render(lg.logger_memory)

        # TOURNAMENT
        print('TOURNAMENT...')
        scores, _, points, sp_scores = playMatches(best_player, current_player, config.EVAL_EPISODES,
                                                   lg.logger_tourney, turns_until_tau0=0, memory=None)
        print('\nSCORES')
        print(scores)
        print('\nSTARTING PLAYER / NON-STARTING PLAYER SCORES')
        print(sp_scores)
        # print(points)
        print('\n\n')

        if scores['current_player'] > scores['best_player'] * config.SCORING_THRESHOLD:
            best_player_version = best_player_version + 1
            best_NN.model.set_weights(current_NN.model.get_weights())
            best_NN.write(initialise.INITIAL_RUN_NUMBER, best_player_version)

    else:
        print('MEMORY SIZE: ' + str(len(memory.ltmemory)))
