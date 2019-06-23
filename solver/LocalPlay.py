import sys
from dynamic4 import DynamicGame
import pygame as pg
from solver.Solver import Solver


class LocalPlay:

    CELL_SIZE = 100

    def __init__(self, shape=(4, 5), human_first=True):

        # Game environment
        self.shape = shape
        self.env = DynamicGame(grid_shape=shape)

        self.WINDOW_DIMS = (shape[1] * self.CELL_SIZE, shape[0] * self.CELL_SIZE)
        self.main_window = pg.display.set_mode(self.WINDOW_DIMS, 0, 32)
        self.main_window.fill((255, 255, 255))

        self.render(self.main_window)
        pg.display.update()

        while 1:

            # Check if AI plays first
            if not human_first:
                self.update_AI()
                # Check for draw
                if self.env.gameState.isEndGame:
                    break

            # Ask user for valid command
            event = self.choose_move()

            # User wishes to quit
            if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

            # User selects a valid command
            elif event.type == pg.MOUSEBUTTONDOWN:
                try_again = self.update_player(event)
                while try_again:
                    event = self.choose_move()
                    try_again = self.update_player(event)

            if self.env.gameState.isEndGame:
                break

            # Check if AI plays second
            if human_first:
                self.update_AI()

            # Check for draw
            if self.env.gameState.isEndGame:
                break

    @staticmethod
    def choose_move():
        while True:
            event = pg.event.wait()
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                return event

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

        try_again = True
        if action in self.env.gameState.allowedActions:
            _, _, _, _ = self.env.step(action)
            try_again = False

        self.render(self.main_window)
        pg.display.update()

        return try_again

    def update_AI(self):
        solver = Solver(self.env.gameState)
        action = solver.get_action()
        self.env.step(action)

        self.render(self.main_window)
        pg.display.update()


if __name__ == '__main__':
    play = LocalPlay(shape=(3, 5), human_first=True)

'''WEIRD BEHAVIOR: Easy to beat when Ai goes first, always ties when human goes first'''



