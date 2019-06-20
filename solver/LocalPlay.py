import sys

from dynamic4 import DynamicGame, DynamicGameState
import pygame as pg
import numpy as np
from solver.Solver import Solver
from solver.Node import Node


class LocalPlay:

    CELL_SIZE = 100

    def __init__(self, shape=(6, 7)):

        # Game environment
        self.shape = shape
        self.env = DynamicGame(grid_shape=shape)

        self.WINDOW_DIMS = (shape[1] * self.CELL_SIZE, shape[0] * self.CELL_SIZE)
        self.main_window = pg.display.set_mode(self.WINDOW_DIMS, 0, 32)
        self.main_window.fill((255, 255, 255))

        game_over = 0
        while not game_over:

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

                elif event.type == pg.MOUSEBUTTONDOWN:
                    game_over = self.update_player(event)
                    if game_over:
                        break
                    # self.update_AI()

            self.render(self.main_window)
            pg.display.update()

    def render(self, main_window):

        for x in range(self.shape[1]):
            for y in range(self.shape[0]):
                pg.draw.rect(main_window, (255, 255, 255), (x*self.CELL_SIZE, y*self.CELL_SIZE, self.CELL_SIZE, self.CELL_SIZE))

        for x in range(self.shape[1]):
            pg.draw.line(main_window, (0, 0, 0), (x*self.CELL_SIZE, 0), (x*self.CELL_SIZE, self.shape[0]*self.CELL_SIZE))
            pg.draw.line(main_window, (0, 0, 0), (0, x*self.CELL_SIZE), (self.shape[1]*self.CELL_SIZE, x*self.CELL_SIZE))

        matrix = self.env.gameState.board.reshape(self.shape)

        for x in range(self.shape[1]):
            for y in range(self.shape[0]):
                if matrix[y, x] == 1:
                    pg.draw.circle(main_window, (255, 0, 0), (int((x + 0.5) * self.CELL_SIZE), int((y + 0.5) * self.CELL_SIZE)), self.CELL_SIZE//2, 0)
                elif matrix[y, x] == -1:
                    pg.draw.circle(main_window, (0, 255, 0), (int((x + 0.5) * self.CELL_SIZE), int((y + 0.5) * self.CELL_SIZE)), self.CELL_SIZE//2, 0)

    def update_player(self, event):
        x = event.pos[0] // self.CELL_SIZE
        y = event.pos[1] // self.CELL_SIZE
        action = y * self.shape[1] + x

        done = 0
        if action in self.env.gameState.allowedActions:
            next_state, value, done, info = self.env.step(action)

        return done

    def update_AI(self):
        solver = Solver(self.env.gameState)
        scores = np.empty(self.shape[1], dtype=int)

        for col in range(self.shape[1]):
            if solver.root_node.can_play(col):
                scores[col] = solver.solve(solver.root_node.play(col))

        print(scores)
        best_col = np.argmax(scores)[-1]



play = LocalPlay(shape=(4, 5))