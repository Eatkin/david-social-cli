import curses
import os
from datetime import datetime
from scripts.ds_components import Menu, Ticker, AsciiImage
import scripts.api_routes as david_api

class State():
    def update(self):
        """Update the state"""
        # Update the menu
        update = self.menu.update()
        # If the menu returns a state, return it
        if update is None or issubclass(update, State):
            return update
        # Otherwise the menu has returned a function so call it
        update()
        return None

    def draw(self):
        """Draw the state"""
        # Draw the menu
        self.menu.draw()

    def cleanup(self):
        """Clean up the state"""
        # Delete menu
        del self.menu

class StateMain(State):
    def __init__(self, stdscr, session, logger):
        """Initialise the state"""
        self.stdscr = stdscr
        self.session = session
        self.logger = logger
        # Set up the david ascii art
        # Get the path to the david ascii art - first go up a directory, then go into assets
        self.david_logo = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets/david.png")

        # Get the version
        self.version = david_api.query_api("version")
        self.version = self.version['version']

        # Session
        self.session = session

        # Ticker
        self.ticker = Ticker(self.stdscr)

        self.menu_rows = 1

        self.david_ascii = None

        # Initialise the menu
        menu_items = ["Feed", "Bootlickers", "Bootlicking", "Catpets", "Pet Cat", "Exit", ]
        menu_states = [StateExit, StateExit, StateExit, StateExit, StateExit, StateExit]
        self.menu = Menu(self.stdscr, menu_items, menu_states)

    def generate_david_ascii(self):
        """Generate the ascii art"""
        # Get the ascii art
        self.david_ascii = AsciiImage(self.stdscr, self.david_logo, url=False, centre=True, dim_adjust=(0, self.menu_rows + 1))

    def update(self):
        """Update the state"""
        curses.update_lines_cols()
        self.menu_rows = self.menu.get_rows()
        # Update the ticker
        self.ticker.update()

        # Call the parent update function
        return super().update()

    def update_ascii(self):
        """Update ascii to fit the terminal"""
        # We need to generate the ascii if it doesn't exist
        # This makes sure it is generated with the correct dimensions (accounting for menu)
        # If we generate it initially it will be generated with the wrong dimensions
        if self.david_ascii is None:
            self.generate_david_ascii()
            return

        # Pass the new dimensions to the ascii object
        self.david_ascii.set_dim_adjust((0, self.menu_rows + 1))

        # Use the ascii image's update function
        self.david_ascii.update()


    def cleanup(self):
        """Clean up the state"""
        self.logger.info('cleaning up StateMain stuff')
        # Delete the ticker object
        del self.ticker
        # Delete the ascii object
        del self.david_ascii
        super().cleanup()

    def draw(self):
        """Draw the state"""
        # Print the ticker
        self.ticker.draw()

        self.stdscr.addstr("\n")
        welcome_message = f"Welcome to David Social version {self.version}!"
        # Centre the welcome message
        _, max_width = curses.initscr().getmaxyx()
        max_width -= 1
        centre = round((max_width - len(welcome_message))/2)
        self.stdscr.addstr(" "*centre + welcome_message + "\n")

        # Call update ascii here because we know the available space
        self.update_ascii()

        # Print the ascii
        self.david_ascii.draw()

        # Call the parent draw function
        super().draw()

class StateExit(State):
    def __init__(self, stdscr, session, logger):
        """Initialise the state"""
        self.logger = logger
        self.logger.info('initialising StateExit')
        self.stdscr = stdscr
        self.countdown = 3
        self.t = datetime.now()
        # Create blank menu
        self.menu = Menu(self.stdscr, [], [])

    def update(self):
        """Update the state, countdown to exit"""
        dt = datetime.now() - self.t
        self.countdown -= dt.total_seconds()
        self.t = datetime.now()
        if self.countdown <= 0:
            exit(0)

        super().update()

    def draw(self):
        """Draw the state"""
        self.stdscr.addstr("Goodbye!\n")

        super().draw()

    def cleanup(self):
        """Clean up the state"""
        self.logger.info('cleaning up StateExit stuff')
        del self.menu
