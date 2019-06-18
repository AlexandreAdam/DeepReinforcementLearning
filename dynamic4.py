import numpy as np

"""
Supports full 2D (6X7 by standard) with different size of connections (4 by standard).

ATTENTION: WHEN YOU CREATE AN INSTANCE OF THIS CLASS, YOU MUST EITHER SPECIFY BOTH BOARD AND SHAPE 
           PARAMETERS OR NONE AT ALL.

"""



class DynamicGameState:

    def __init__(self, board=None, player_turn=1, shape=(6, 7), connect_size=4):

        if connect_size > shape[0] and connect_size > shape[1]:
            raise ValueError("connect_size is bigger than all dimensions. No win possible with these rules.")

        if board is None:
            self.board = np.zeros(shape[0] * shape[1], dtype=np.int8)
        else:
            self.board = board

        self.position = []
        self.shape = shape
        self.connect_size = connect_size
        self.pieces = {'1': 'X', '0': '-', '-1': 'O'}
        self.playerTurn = player_turn
        self.total_moves = 0
        self.winners = self._winners()
        self.binary = self._binary()
        self.id = self._convertStateToId()
        self.allowedActions = self._allowedActions()
        self.isEndGame = self._checkForEndGame()
        self.value = self._getValue()
        self.score = self._getScore()

    def _checkForEndGame(self):
        if np.count_nonzero(self.board) == np.prod(self.shape):
            return 1

        for winner in self.winners:
            concurrent = 0

            for cell in winner:
                concurrent += self.board[cell]

            if concurrent == self.connect_size * -self.playerTurn:
                return 1

        return 0

    def _getValue(self):
        # This is the value of the state for the current player
        # i.e. if the previous player played a winning move, you lose
        for winner in self.winners:
            concurrent = 0

            for cell in winner:
                concurrent += self.board[cell]

            if concurrent == self.connect_size * -self.playerTurn:
                return -1, -1, 1

        return 0, 0, 0

    def _getScore(self):
        tmp = self.value
        return tmp[1], tmp[2]

    def _allowedActions(self):
        allowed = []
        for i in range(len(self.board)):
            if i >= len(self.board) - self.shape[1]:
                if self.board[i] == 0:
                    allowed.append(i)
            else:
                if self.board[i] == 0 and self.board[i + self.shape[1]] != 0:
                    allowed.append(i)

        return allowed

    def _convertStateToId(self):
        player1_position = np.zeros(len(self.board), dtype=np.int)
        player1_position[self.board == 1] = 1

        other_position = np.zeros(len(self.board), dtype=np.int)
        other_position[self.board == -1] = 1

        position = np.append(player1_position, other_position)

        id = ''.join(map(str, position))

        return id

    def _binary(self):
        currentplayer_position = np.zeros(len(self.board), dtype=np.int)
        currentplayer_position[self.board == self.playerTurn] = 1

        other_position = np.zeros(len(self.board), dtype=np.int)
        other_position[self.board == -self.playerTurn] = 1

        position = np.append(currentplayer_position, other_position)

        return position

    def _winners(self):
        index_board = np.arange(0, self.shape[0] * self.shape[1], 1).astype(np.int).reshape(self.shape)
        winners = []

        # Horizontals
        for row in index_board:
            for index in range(0, row.size-self.connect_size+1):
                winners.append(row[index:index+self.connect_size].tolist())

        # Verticals
        for idx in range(self.shape[1]):
            for idy in range(0, self.shape[0]-self.connect_size+1):
                winners.append(index_board[idy:idy+self.connect_size, idx].tolist())

        # Diagonals
        for idx in range(self.shape[1]-self.connect_size+1):
            for idy in range(0, self.shape[0]-self.connect_size+1):
                diagonal = []
                # Build the diagonal
                for idc in range(self.connect_size):
                    diagonal.append(index_board[idy+idc, idx+idc])

                winners.append(diagonal)

        # Anti diagonals
        for idx in range(self.shape[1]-1, self.connect_size-2, -1):
            for idy in range(self.shape[0]-1, self.connect_size-2, -1):
                anti_diagonal = []
                # Build the anti-diagonal
                for idc in range(self.connect_size):
                    anti_diagonal.append(index_board[idy-idc, idx-idc])

                winners.append(anti_diagonal)

        return winners

    def takeAction(self, action):
        newBoard = np.array(self.board)
        newBoard[action] = self.playerTurn

        newState = DynamicGameState(board=newBoard, player_turn=-self.playerTurn, shape=self.shape, connect_size=self.connect_size)
        newState.position = self.position
        newState.position.append(action - (action//self.shape[1])*self.shape[1])
        newState.total_moves = self.total_moves + 1

        value = 0
        done = 0

        if newState.isEndGame:
            value = newState.value[0]
            done = 1

        return newState, value, done

    def render(self, logger):
        for r in range(self.shape[0]):
            logger.info([self.pieces[str(x)] for x in self.board[self.shape[1]*r: (self.shape[1]*r + self.shape[1])]])
        logger.info('--------------')


class DynamicGame:

    def __init__(self, grid_shape=(6, 7)):
        self.name = 'Dynamic4'
        self.currentPlayer = 1
        self.grid_shape = grid_shape
        self.input_shape = (2, self.grid_shape[0], self.grid_shape[0])
        self.connect_size = 4
        self.gameState = DynamicGameState(board=np.zeros(np.prod(self.grid_shape), dtype=np.int), player_turn=1,
                                          shape=self.grid_shape, connect_size=self.connect_size)
        self.actionSpace = np.zeros(42, dtype=np.int)
        self.pieces = {'1': 'X', '0': '-', '-1': 'O'}
        self.state_size = len(self.gameState.binary)
        self.action_size = len(self.actionSpace)

    def reset(self):
        self.gameState = DynamicGameState(board=np.zeros(np.prod(self.grid_shape), dtype=np.int), player_turn=1,
                                          shape=self.grid_shape, connect_size=self.connect_size)
        self.currentPlayer = 1
        return self.gameState

    def step(self, action):
        next_state, value, done = self.gameState.takeAction(action)
        self.gameState = next_state
        self.currentPlayer = -self.currentPlayer
        info = None
        return next_state, value, done, info

    # REFACTORED, TO BE DEBUGGED
    def identities(self, state, actionValues):
        identities = [(state, actionValues)]

        currentBoard = state.board
        currentAV = actionValues

        tempBoard = np.copy(currentBoard).reshape(self.grid_shape)
        tempAV = np.copy(currentAV).reshape(self.grid_shape)

        for y in range(self.grid_shape[0]):
            for x in range(self.grid_shape[1]):
                tempBoard[y, x] = currentBoard[y, self.grid_shape[1] - x - 1]
                tempAV[y, x] = currentAV[y, self.grid_shape[1] - x - 1]

        currentBoard = tempBoard.flatten()
        currentAV = tempAV.flatten()

        identities.append((DynamicGameState(board=currentBoard, player_turn=state.playerTurn, shape=self.grid_shape,
                                            connect_size=self.connect_size), currentAV))

        return identities

    def __str__(self):
        return str(self.gameState.board.reshape(self.grid_shape))


if __name__ == '__main__':

    game = DynamicGame()
    game.step(38)
    game.step(31)
    game.step(39)
    print(game.gameState.position)
    print(game)

