import curses
from math import floor

class Menu():
    def __init__(self, stdscr, items, states, default_col, highlight_col):
        self.stdscr = stdscr
        self.items = items
        self.states = states
        self.cols = 0
        self.rows = 0
        self.selection = 0
        self.default_col = default_col
        self.highlight_col = highlight_col
        # Used for spacing
        self.longest_item = len(max(self.items, key=len))

    def clear_row(self, row):
        """Blank out the specified row"""
        _, width = curses.initscr().getmaxyx()
        self.stdscr.addstr(row, 0, " " * (width - 1), self.default_col)

    def get_key(self, key, key_check):
        """Check if a key is pressed"""
        return 1 if key == key_check else 0

    def update(self):
        """Navigation with curses"""
        self.stdscr.nodelay(True)
        key = self.stdscr.getch()
        # Jank ass way of getting input lmao
        hinput = self.get_key(key, curses.KEY_RIGHT) - self.get_key(key, curses.KEY_LEFT)
        vinput = self.get_key(key, curses.KEY_DOWN) - self.get_key(key, curses.KEY_UP)
        # Hinput simply increments or decrements
        if hinput != 0:
            self.selection += hinput
            if self.selection < 0:
                self.selection = len(self.items) - 1
            if self.selection >= len(self.items):
                self.selection = 0

        # Vinput is more annoying to handle
        if vinput != 0 and self.rows > 0:
            self.selection += self.cols * vinput
            if self.selection < 0:
                self.selection = self.cols * self.rows + self.selection
            if self.selection >= len(self.items):
                self.selection = len(self.items) - 1

        if self.get_key(key, curses.KEY_ENTER):
            return self.states[self.selection]

        return None

    def draw(self):
        """Draw the menu"""
        # Reset rows and columns
        self.rows = 0
        self.cols = 0
        # Get the height and width of the terminal
        height, width = curses.initscr().getmaxyx()

        # Define the coordinates of the menu items
        coords = []
        current_width = 0
        count_cols = True
        for item in self.items:
            if current_width + self.longest_item + 1 > width:
                current_width = 0
                self.rows += 1
                centre = round((self.longest_item - len(item))/2)
                coords.append((current_width + centre, self.rows))
                count_cols = False
            else:
                # Counts how many columns there are
                if count_cols:
                    self.cols += 1
                # Append this before adjusting the width
                centre = round((self.longest_item - len(item))/2)
                coords.append((current_width + centre, self.rows))

            # Consistent spacing
            current_width += self.longest_item + 1

        # Set initial drawing coordinates
        x = 0
        y = height - self.rows - 1

        # Blank rows
        for row in range(y, height):
            self.clear_row(row)

        # Print menu items
        for item in self.items:
            x_offset, y_offset = coords.pop(0)
            col = self.highlight_col if self.selection == self.items.index(item) else self.default_col
            self.stdscr.addstr(y + y_offset, x + x_offset, item, col)

    def get_rows(self):
        """Return the height of the menu"""
        return self.rows
