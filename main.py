from curses.textpad import rectangle
import game
import time

def main():
    tetris_game = game.Game()
    while 1:
        try:
            frame_start = time.time()
            try:
                tetris_game.update()
            # Reset if it spawns a piece in an existing tile
            except game.PieceOverlap:
                tetris_game = game.Game()
            
            # Frame limit to 60 FPS
            frame_duration = time.time() - frame_start
            if frame_duration > 1.0/60:
                continue
            elif frame_duration < 0:
                frame_duration = 1.0/60
            time. sleep(1.0/60 - frame_duration)

        except KeyboardInterrupt:
            tetris_game.close()
            exit()

if __name__ == "__main__":
    main()
