# Local
from utils import setup_logger
from settings import run_folder
import initialise

"""
Used to specify which logger is active during training.
"""

path = run_folder + 'Model_' + str(initialise.INITIAL_RUN_NUMBER) + '/'
LOGGER_DISABLED = {'main': True,
                   'memory': True,
                   'tourney': True,
                   'mcts': True,
                   'model': True}

logger_mcts = setup_logger('logger_mcts', path + 'logs/logger_mcts.log')
logger_mcts.disabled = LOGGER_DISABLED['mcts']

logger_main = setup_logger('logger_main', path + 'logs/logger_main.log')
logger_main.disabled = LOGGER_DISABLED['main']

logger_tourney = setup_logger('logger_tourney', path + 'logs/logger_tourney.log')
logger_tourney.disabled = LOGGER_DISABLED['tourney']

logger_memory = setup_logger('logger_memory', path + 'logs/logger_memory.log')
logger_memory.disabled = LOGGER_DISABLED['memory']

logger_model = setup_logger('logger_model', path + 'logs/logger_model.log')
logger_model.disabled = LOGGER_DISABLED['model']