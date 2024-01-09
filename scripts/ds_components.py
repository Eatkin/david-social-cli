import curses
from datetime import datetime
from math import floor
from scripts.colours import ColourConstants
import scripts.api_routes as david_api
import scripts.string_utils as su


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

        if key == curses.KEY_ENTER or key == 10 or key == 13:
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

class Ticker():
    """Ticker class"""
    def __init__(self, stdscr):
        # Initialise the colour constants
        self.colours = ColourConstants()
        self.colours.init_colours()
        _, width = curses.initscr().getmaxyx()
        self.stdscr = stdscr
        self.text = david_api.query_api("get-ticker-text")
        self.ticker_x = 0
        self.ticker_spacing = max(round(width * 0.2), 2)
        self.t = datetime.now()
        self.ticker = self.text
        self.ticker_update_rate = 0.2

    def update_ticker(self):
        """Get new ticker text from the API"""
        self.text = david_api.query_api("get-ticker-text")

    def update(self):
        """Updates the ticker text"""
        _, width = curses.initscr().getmaxyx()
        # Update spacing basedd on Terminal width
        self.ticker_spacing = max(round(width * 0.2), 2)

        # Update the ticker text position
        dt = datetime.now() - self.t
        if dt.total_seconds() > self.ticker_update_rate:
            self.t = datetime.now()
            self.ticker_x += 1

        # Wrap ticker_x
        if self.ticker_x >= len(self.text) + self.ticker_spacing:
            self.ticker_x = 0

        # Update the actual text to display
        self.ticker = list(self.text) + list(" " * self.ticker_spacing) + list(self.text)
        # Add enough repeats of the ticker text to fill the screen
        while len(self.ticker) < width * 2:
            self.ticker = self.ticker + list(" " * self.ticker_spacing) + self.ticker

        # Slice the ticker text to fit the screen
        self.ticker = self.ticker[self.ticker_x:self.ticker_x + width - 1]

        # Join the ticker back into a string
        self.ticker = "".join(self.ticker)


    def draw(self):
        """Prints the ticker text with scrolling"""
        # Print the ticker with a colour pair
        self.stdscr.addstr(self.ticker, curses.A_ITALIC | self.colours.YELLOW_BLACK)

class AsciiImage():
    """Ascii image class"""
    def __init__(self, stdscr, image_path, url, centre=True, dim_adjust=(0, 0)):
        """Initialise the ascii image"""
        self.stdscr = stdscr
        self.image_url = image_path
        self.ascii = su.image_to_ascii(image_path, url=False, dim_adjust=dim_adjust)

        # Centre the ascii image if required
        if centre:
            # Get the width of the ascii image
            ascii_width = len(self.ascii.split("\n")[0])
            # Get the width of the terminal
            _, max_width = curses.initscr().getmaxyx()
            # Centre the ascii image
            centre = floor((max_width - ascii_width)/2)
            self.ascii = "\n".join([" "*centre + line for line in self.ascii.split("\n")])

    def get_dims(self):
        """Return width and height of the ascii image"""
        return len(self.ascii.split("\n")), len(self.ascii.split("\n")[0])

    def draw(self):
        """Draw the ascii image"""
        self.stdscr.addstr(self.ascii)
