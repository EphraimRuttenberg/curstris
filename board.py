import curses
from curses.textpad import rectangle
from random import randint, sample
import piece
from copy import deepcopy
import json

LETTERS = list("SZLJTOI")

BOARD_X = 30
BOARD_Y = 5
BOARD_WIDTH = 41
BOARD_HEIGHT = 41
ROWS = 24  

# Size of an ingame tile in characters
tile_width = BOARD_WIDTH//10
tile_height = BOARD_HEIGHT//20

hold_rect_width = tile_width * 6
hold_rect_height = tile_height * 4 
hold_rect_x = BOARD_X - hold_rect_width - tile_width

queue_rect_width = tile_width * 6
queue_rect_height = tile_height * 17
queue_rect_x = BOARD_X + queue_rect_width + (5 * tile_width)


with open("rotations.json", "r") as r:
    ROTATIONS = json.loads(r.read())


def rotate_right(matrix):
    return list(zip(*matrix[::-1]))

def rotate_left(matrix):
    return list(zip(*[i[::-1] for i in matrix]))


class Board():
    def __init__(self):
        self.screen = self.initscr()
        self.board = [[0] * 10 for i in range(ROWS)]
        self.held_piece = None
        self.bag = sample(LETTERS, k = len(LETTERS))
        self.next_bag = sample(LETTERS, k = len(LETTERS))

    def initscr(self): 
        stdscr =  curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        stdscr.keypad(True)
        stdscr.nodelay(True)
        curses.resizeterm(400, 400)
        return stdscr

    def deinit_scr(self):
        self.screen.erase()
        self.screen.refresh()
        curses.nocbreak()
        self.screen.keypad(False)
        curses.echo()
        curses.curs_set(1)
        curses.endwin()
    
    def retrieve_piece(self):
        """
        Take a piece from the bag, if the bag is empty, use the next_bag and create a new next_bag
        """
        if not self.bag:
            self.bag = [*self.next_bag]
            self.next_bag = sample(LETTERS, k=7)
        return self.bag.pop(0)


    def hold_piece(self):
        """
        Switch the active piece and the held piece, returning both to default 
        coordinates and rotation
        """
        self.held_piece, self.active_piece = self.active_piece, self.held_piece
        if self.active_piece:
            self.active_piece = piece.Piece(self.active_piece.name)
        self.held_piece = piece.Piece(self.held_piece.name)
        self.held_piece.x = -6
        self.held_piece.y = 18

    def display(self):
        """
        Displays tiles and border of the board, the active piece, and a preview piece of where it will land
        """
        # Display the border of the board, not filled in
        rectangle(self.screen, 
                  BOARD_Y,                BOARD_X - 1, 
                  BOARD_Y + BOARD_HEIGHT, BOARD_X + BOARD_WIDTH + 1)

        # Displays solidifed tiles
        for y in range(ROWS):
            for x in range(10):
                if (self.board[y][x] == 0 or y > 19):
                    continue
                else:
                    # Find the bottom left corner of the rectangle on the visual board representing each x, y coordinate
                    offset_x = (x * tile_width) + BOARD_X + 1
                    offset_y = ((20 - y) * tile_height) + BOARD_Y - 1
                    # Draw a rectangle for each tile
                    for _y in range(offset_y, offset_y + tile_height):
                        for _x in range(offset_x, offset_x + tile_width):
                            self.screen.addch(_y, _x, "█")
        
        # Create a piece representing the preview and display it
        lowest_y = self.get_lowest_valid_y()
        _piece = deepcopy(self.active_piece)
        _piece.y = lowest_y
        _piece.show(self.screen, "*")
        
        self.active_piece.show(self.screen, "#")
         
        # Display the hold box and held piece
        rectangle(self.screen, 
                BOARD_Y,                    hold_rect_x,
                BOARD_Y + hold_rect_height, hold_rect_x + hold_rect_width)
        if self.held_piece:
            self.held_piece.show(self.screen, "#")

        #Display the next 5 pieces
        rectangle(self.screen,
                BOARD_Y,                     queue_rect_x,
                BOARD_Y + queue_rect_height, queue_rect_x + queue_rect_width)
        for i, name in enumerate([*self.bag, *self.next_bag][:5]):
            _piece = piece.Piece(name)
            _piece.x = 12
            _piece.y = 18 - (3 * i)
            _piece.show(self.screen, "#")

        self.screen.refresh()

    def check_valid_piece(self, piece):
        """
        Check if the given shape and position is in bounds and does not overlap with anything
        """
        for y, row in enumerate(piece.shape):
            for x, tile in enumerate(row):
                if tile == "#":
                    offset_y = piece.y - y
                    offset_x = piece.x + x
                    if  offset_y < 0 or \
                        offset_x < 0 or \
                        offset_x > 9 or \
                        self.board[offset_y][offset_x]:
                        return False
        return True
    
    def move_x(self, x_direction):
        # Check if it can move in the given direction and move if so
        _piece = deepcopy(self.active_piece)
        _piece.x += x_direction
        if self.check_valid_piece(_piece):
            self.active_piece.x += x_direction


    def gravity(self):
        # Try to move down, if it cannot then add the piece to the board tiles
        if self.get_lowest_valid_y() == self.active_piece.y:
            self.solidify()
            return 1
        else:
            self.active_piece.y -= 1
    
    def solidify(self): 
        # Adds each tile of the active piece to the board as solid tiles
        for y, row in enumerate(self.active_piece.shape):
            for x, tile in enumerate(row):
                if tile == "#":
                    offset_y = self.active_piece.y - y
                    offset_x = self.active_piece.x + x
                    self.board[offset_y][offset_x] = 1

    def get_lowest_valid_y(self):
        """
        Finds where the ghost piece and hard drop will be
        Iterates backwards through the rows so it doesn't choose a y coord 
         that is below a solid tile
        """
        _piece = deepcopy(self.active_piece)
        _piece.y = self.active_piece.y
        valid_y = [self.active_piece.y]
        while 1:
            if self.check_valid_piece(_piece):
                valid_y.append(_piece.y)
                _piece.y -= 1
            else:
                break
        return min(valid_y)

    def rotate_piece(self, rot_direction, rot_increment):
        """
        Use the offset table for each rotation to do wall kicks if necessary, not rotating if none are valid
        Offsets are defined in the Super Rotation System guidelines
        """
        if self.active_piece.name == "I":
            rot_table = ROTATIONS["i"]
        else:
            rot_table = ROTATIONS["all"]
        
        # Alter the rotation state and wrap around if it is out of range
        new_rot = self.active_piece.rot + rot_increment
        if new_rot == 4:
            new_rot = 0
        elif new_rot == -1:
            new_rot = 3
        
        _piece = deepcopy(self.active_piece)
        _piece.shape = rot_direction(self.active_piece.shape)
        _piece.rot = new_rot
        
        # Try offsets from the table until one works
        for delta_x, delta_y in rot_table[str([self.active_piece.rot, new_rot])]:
            _piece.x = self.active_piece.x + delta_x
            _piece.y = self.active_piece.y + delta_y
            if self.check_valid_piece(_piece):
                self.active_piece = _piece
                return

    def delete_full_rows(self):
        """
        Clears full rows and moves all other rows down, returning the number of rows cleared
        """
        row_count = 0
        for i in range(24):
            if self.board[i] == [1]*10:
                del self.board[i]
                self.board.append([0]*10)
                row_count += 1
        return row_count
    
    def spawn_new_piece(self):
        self.active_piece = piece.Piece(self.retrieve_piece())
