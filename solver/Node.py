

"""
ATTENTION:
    -Column indexes are defined between 1 to width and not 0 to width-1
"""


class Node:

    def __init__(self, position, mask, total_moves, shape=(6, 7)):
        self.shape = shape
        self.WIDTH, self.HEIGHT = shape[1], shape[0]
        self.position, self.mask = position, mask
        self.total_moves = total_moves

    # Returns the binary representation of an empty board except for a single cell in the ghost layer.
    def top_mask(self, column_nb):
        return (1 << (self.HEIGHT-1)) << column_nb*(self.HEIGHT+1)

    # Returns the binary representation of an empty board except for a single cell in the bottom.
    def bottom_mask(self, column_nb):
        return 1 << column_nb * (self.HEIGHT+1)

    # Returns binary representation of an empty board except single full column.
    def column_mask(self, column_nb):
        return ((1 << self.HEIGHT)-1) << column_nb*(self.HEIGHT+1)

    def can_play(self, column_nb):
        return (self.mask & self.top_mask(column_nb)) == 0

    def play(self, column_nb):

        self.position = self.position ^ self.mask  # Invert the position
        self.mask = self.mask | self.bottom_mask(column_nb)  # Update the mask
        self.total_moves += 1  # Update the move counter

    def is_winning_move(self, column_nb):
        pos = self.position
        pos = pos | ((self.mask + self.bottom_mask(column_nb)) & self.column_mask(column_nb))
        return self.alignment(pos)

    # Returns the truth value of a connect 4 alignment
    def alignment(self, position):

        # Horizontal
        m = position & (position >> (self.HEIGHT+1))
        if m & (m >> (2 * (self.HEIGHT+1))):
            return True

        # Vertical;
        m = position & (position >> 1)
        if m & (m >> 2):
            return True

        # Diagonal 1
        m = position & (position >> self.HEIGHT)
        if m & (m >> (2*self.HEIGHT)):
            return True

        # Diagonal 2
        m = position & (position >> (self.HEIGHT+2))
        if m & (m >> (2*(self.HEIGHT+2))):
            return True

        return False

    def key(self):
        return self.position + self.mask # + self.bottom ????????????

