import random

class ZobristHash:

    def __init__(self, board, zod_table, previous_hash, move_index):
        self.board = board
        self.zob_table = zod_table
        self.previous_hash = previous_hash
        self.current_player = move_index["player"]
        self.current_move_row = move_index["row"]
        self.current_move_column = move_index["column"]

    @staticmethod
    def indexing_pieces(piece):
        """
        Mapping each piece to the correct index in zob_table
        """
        if piece == 'X':
            return 0
        if piece == 'O':
            return 1

    def compute_hash(self):
        piece = self.indexing_pieces(self.current_player)
        current_hash = self.zob_table[piece][self.current_move_row][self.current_move_column]
        return self.previous_hash ^ current_hash
