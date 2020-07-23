import board
import piece
import random
import curses

LETTERS = ["L", "J", "S", "Z", "I", "T", "O"]


class PieceOverlap(Exception):
    pass


class Game():
    def __init__(self):
        self.board = board.Board()
        self.bag = random.sample(LETTERS, k=7)
        self.next_bag = random.sample(LETTERS, k=7)
        self.board.active_piece = piece.Piece(self.retrieve_piece())
        self.frame_count = 0
    
    def retrieve_piece(self):
        """
        Take a piece from the bag, if the bag is empty, use the next_bag and create a new next_bag
        """
        if not self.bag:
            self.bag = [*self.next_bag]
            self.next_bag = random.sample(LETTERS, k=7)
        return self.bag.pop()
   
    def update(self):
        """
        Do gravity, check for input, check if it has to reset, display pieces and tiles
        """
        self.frame_count += 1
        if self.frame_count % 30 == 0:
            # board.gravity() returns 1 if it solidified a piece
            if self.board.gravity():
                self.board.active_piece = piece.Piece(self.retrieve_piece())

        if not self.board.check_valid_piece(self.board.active_piece):
            raise PieceOverlap()
        
        self.board.delete_full_rows()
        self.check_keys()
        self.board.screen.erase()
        self.board.display()

    def close(self):
        """
        Will have more functionality later, right now just returns the terminal
         setting backs to normal
         """
        self.board.deinit_scr()

    def check_keys(self):
        keys_pressed = []
        while 1:
            try:
                keys_pressed.append(self.board.screen.getkey())
            except:
                break

        for c in keys_pressed:
            if c == "KEY_LEFT":
                self.board.move_x(-1)

            if c == "KEY_RIGHT":
                self.board.move_x(1)

            if c == "KEY_DOWN":
                self.board.gravity()
                # Reset frame count so gravity does not work unpredictably with soft drop
                self.frame_count = 1

            if c == "KEY_UP":
                lowest_y = self.board.get_lowest_valid_y()
                self.board.active_piece.y = lowest_y
                self.board.solidify()
                self.frame_count = 1
                self.board.active_piece = piece.Piece(self.retrieve_piece())
            
            if c == "a":
                self.board.rotate_piece(board.rotate_left, -1)

            if c == "s":
                self.board.rotate_piece(board.rotate_right, 1)

