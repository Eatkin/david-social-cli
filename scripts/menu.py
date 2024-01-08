import curses

class Menu():
    def __init__(self, stdscr, items, functions, default_col, highlight_col):
        self.stdscr = stdscr
        self.items = items
        self.functions = functions
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

    def update(self):
        """Navigation with curses"""
        pass

    def draw(self):
        """Draw the menu"""
        # Reset rows
        self.rows = 0
        # Get the height and width of the terminal
        height, width = curses.initscr().getmaxyx()

        # Define the coordinates of the menu items
        coords = []
        current_width = 0
        for item in self.items:
            if current_width + self.longest_item + 1 > width:
                current_width = 0
                self.rows += 1
                centre = round((self.longest_item - len(item))/2)
                coords.append((current_width + centre, self.rows))
            else:
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
