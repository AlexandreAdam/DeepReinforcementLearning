import pandas as pd
import os
import numpy as np
import imp

models_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Models')

models = os.listdir(models_path)

parametres = ['Épisodes', 'MCTS simulations', 'Memory size', 'Turns until tau0',
             'CPUCT', 'Epsilon', 'Alpha', 'Batch size', 'Epochs', 'Reg constant',
             'Momentum', 'Training loops', 'Number of hidden CNN layers', 'Filters',
             'Kernel size', 'Evaluation episodes', 'Scoring thresholds']

table = pd.DataFrame(data=np.zeros((len(parametres), len(models))),
                     index=parametres,
                     columns=models)

for model in models:
    model_path = os.path.join(models_path, model)
    config = imp.load_source(model, os.path.join(model_path, 'config.py'))

    table.loc['Épisode',                     model] = config.EPISODES
    table.loc['MCTS simulations',            model] = config.MCTS_SIMS
    table.loc['Memory size',                 model] = config.MEMORY_SIZE
    table.loc['Turns until tau0',            model] = config.TURNS_UNTIL_TAU0
    table.loc['CPUCT',                       model] = config.CPUCT
    table.loc['Alpha',                       model] = config.ALPHA
    table.loc['Batch size',                  model] = config.BATCH_SIZE
    table.loc['Epochs',                      model] = config.EPOCHS
    table.loc['Momentum',                    model] = config.MOMENTUM
    table.loc['Training loops',              model] = config.TRAINING_LOOPS
    table.loc['Number of hidden CNN layers', model] = len(config.HIDDEN_CNN_LAYERS)
    table.loc['Filters',                     model] = config.HIDDEN_CNN_LAYERS[0]['filters']
    table.loc['Kernel size',                 model] = config.HIDDEN_CNN_LAYERS[0]['kernel_size'][0]
    table.loc['Evaluation episodes',         model] = config.EVAL_EPISODES
    table.loc['Scoring thresholds',          model] = config.SCORING_THRESHOLD

print(table)
