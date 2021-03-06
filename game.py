import board
import piece
import random
import curses



class PieceOverlap(Exception):
    pass


class Game():
    def __init__(self):
        self.frame_count = 0
        self.board = board.Board()
        self.board.spawn_new_piece()

    def update(self):
        """
        Do gravity, check for input, check if it has to reset, display pieces and tiles
        """
        self.frame_count += 1
        if self.frame_count % 30 == 0:
            # board.gravity() returns 1 if it solidified a piece
            if self.board.gravity():
                self.board.spawn_new_piece()

        if not self.board.check_valid_piece(self.board.active_piece) and \
                self.board.active_piece.y == 18:
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
                self.board.spawn_new_piece()
            
            if c == "a":
                self.board.rotate_piece(board.rotate_left, -1)

            if c == "s":
                self.board.rotate_piece(board.rotate_right, 1)

            if c == " ":
                self.board.hold_piece()
                if self.board.active_piece is None:
                    self.board.spawn_new_piece()

            if c == "KEY_BACKSPACE":
                self.close()
                exit()

