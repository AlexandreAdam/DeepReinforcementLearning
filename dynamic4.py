import numpy as np

"""
Supports full 2D (6X7 by standard) with different size of connections (4 by standard).

ATTENTION: WHEN YOU CREATE AN INSTANCE OF THIS CLASS, YOU MUST EITHER SPECIFY BOTH BOARD AND SHAPE 
           PARAMETERS OR NONE AT ALL.

"""


class DynamicGameState:

    def __init__(self, board=np.zeros(42, dtype=np.int), playerTurn=1, shape=(6, 7), connect_size=4):

        if np.prod(shape) != board.size:
            raise ValueError("board and shape parameters are incompatible.")

        if connect_size > shape[0] and connect_size > shape[1]:
            raise ValueError("connect_size is bigger than all dimensions. No win possible with these rules.")

        self.shape = shape
        self.connect_size = connect_size
        self.pieces = {'1': 'X', '0': '-', '-1': 'O'}
        self.playerTurn = playerTurn
        self.board = board
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
        #print(index_board)
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

        newState = DynamicGameState(board=newBoard, playerTurn=-self.playerTurn, shape=self.shape, connect_size=self.connect_size)

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


class Game:

    def __init__(self):
        self.currentPlayer = 1
        self.game_shape = (6, 7)
        self.connect_size = 4
        self.gameState = DynamicGameState(board=np.zeros(np.prod(self.game_shape), dtype=np.int), playerTurn=1,
                                          shape=self.game_shape, connect_size=self.connect_size)
        self.actionSpace = np.zeros(42, dtype=np.int)
        self.pieces = {'1': 'X', '0': '-', '-1': 'O'}
        self.grid_shape = self.game_shape
        self.input_shape = (2, self.game_shape[0], self.game_shape[0])
        self.name = 'Dynamic4'
        self.state_size = len(self.gameState.binary)
        self.action_size = len(self.actionSpace)

    def reset(self):
        self.gameState = DynamicGameState(board=np.zeros(np.prod(self.game_shape), dtype=np.int), playerTurn=1,
                                          shape=self.game_shape, connect_size=self.connect_size)
        self.currentPlayer = 1
        return self.gameState

    def step(self, action):
        next_state, value, done = self.gameState.takeAction(action)
        self.gameState = next_state
        self.currentPlayer = -self.currentPlayer
        info = None
        return next_state, value, done, info

    #TODO TO BE REFACTORED TO ACCEPT ANY SHAPE STATE AND ACTIONVALUES
    def identities(self, state, actionValues):
        identities = [(state, actionValues)]

        currentBoard = state.board
        currentAV = actionValues

        '''
        currentBoard = np.array([
              currentBoard[6], currentBoard[5],currentBoard[4], currentBoard[3], currentBoard[2], currentBoard[1], currentBoard[0]
            , currentBoard[13], currentBoard[12],currentBoard[11], currentBoard[10], currentBoard[9], currentBoard[8], currentBoard[7]
            , currentBoard[20], currentBoard[19],currentBoard[18], currentBoard[17], currentBoard[16], currentBoard[15], currentBoard[14]
            , currentBoard[27], currentBoard[26],currentBoard[25], currentBoard[24], currentBoard[23], currentBoard[22], currentBoard[21]
            , currentBoard[34], currentBoard[33],currentBoard[32], currentBoard[31], currentBoard[30], currentBoard[29], currentBoard[28]
            , currentBoard[41], currentBoard[40],currentBoard[39], currentBoard[38], currentBoard[37], currentBoard[36], currentBoard[35]
            ])

        currentAV = np.array([
            currentAV[6], currentAV[5],currentAV[4], currentAV[3], currentAV[2], currentAV[1], currentAV[0]
            , currentAV[13], currentAV[12],currentAV[11], currentAV[10], currentAV[9], currentAV[8], currentAV[7]
            , currentAV[20], currentAV[19],currentAV[18], currentAV[17], currentAV[16], currentAV[15], currentAV[14]
            , currentAV[27], currentAV[26],currentAV[25], currentAV[24], currentAV[23], currentAV[22], currentAV[21]
            , currentAV[34], currentAV[33],currentAV[32], currentAV[31], currentAV[30], currentAV[29], currentAV[28]
            , currentAV[41], currentAV[40],currentAV[39], currentAV[38], currentAV[37], currentAV[36], currentAV[35]
                    ])
        '''

        identities.append((DynamicGameState(board=currentBoard, playerTurn=state.playerTurn, shape=self.game_shape,
                                            connect_size=self.connect_size), currentAV))

        return identities

