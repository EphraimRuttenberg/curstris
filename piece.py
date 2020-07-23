import json
import board

with open("shapes.json", "r") as s:
    SHAPES = json.loads(s.read())

class Piece():
    def __init__(self, name):
        self.name = name
        self.shape = SHAPES[name]
        self.rot = 0
        self.x = 3
        self.y = 18

    def show(self, screen, cha):
        for _y, row in enumerate(self.shape):
            for _x, tile in enumerate(row):
                if _y + self.y > 19 or tile != "#":
                    continue
                # Fill in a rectangle on the board corresponding to the given tile
                offset_x = ((self.x + _x) * board.tile_width) + board.BOARD_X + 1
                offset_y = ((20 - (self.y - _y)) * board.tile_height) + board.BOARD_Y - 1
                for i in range(offset_y, offset_y + board.tile_height):
                    for j in range(offset_x, offset_x + board.tile_width):
                        screen.addch(i, j, cha)

