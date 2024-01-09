import curses

class ColourConstants:
    def __init__(self):
        curses.initscr()
        curses.start_color()
        self.YELLOW_BLACK = curses.color_pair(1)
        self.HIGHLIGHT = curses.color_pair(2)
        self.WHITE_BLACK = curses.color_pair(3)

    @staticmethod
    def init_colours():
        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
