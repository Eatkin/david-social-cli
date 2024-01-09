import os
import logging
import atexit
import curses
from curses import wrapper
from datetime import datetime
from math import floor
from time import sleep
import scripts.env_utils as eu
import scripts.api_routes as david_api
import scripts.string_utils as su
from scripts.feed_utils import print_feed
from scripts.ds_components import Menu, Ticker, AsciiImage
from scripts.colours import ColourConstants

"""
TODO: Kill myself
TODO: Pass menu object to states so they can use it and update as necessary
TODO: Right now it's being updated in main which is kinda dumb cause the states need to update them as necessary
TODO: Move states to their own files and import them here, update them to incldue the logger
TODO: Why does pressing escape pause everything?
TODO: Stuff
TODO: More stuff
TODO: Even more stuff
TODO: Kill myself again
TODO: Ascend to a higher plane of existence
TODO: Become a god
TODO: Become one with the universe
TODO: Become the universe
TODO: Become everything
TODO: Become nothing
TODO: Become the void
TODO: Become the void in the void
TODO: Become the void in the void in the void
TODO: Become the void in the void in the void in the void
TODO: Become the void in the void in the void in the void in the void
TODO: Resurrect myself
TODO: Work on David Social CLI
"""

# Initialise curses
stdscr = curses.initscr()
curses.start_color()
# Initialise the colours
colours = ColourConstants()
colours.init_colours()

# Set up logging
def logging_init():
    """Createss a logfile with the current date and time"""
    # Make a logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.mkdir("logs")
    # Create a logfile with the current date and time
    filename = f"logs/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    logging.basicConfig(filename=filename, level=logging.DEBUG, encoding="utf-8")
    print(f"Logging to {filename}")
    logger = logging.getLogger()
    return filename, logger

LOGFILE, LOGGER = logging_init()

def cleanup():
    """Cleanup curses and remove logfile if there are no logs"""
    curses.endwin()

    # Check if the logfile is empty
    if os.stat(LOGFILE).st_size == 0:
        # If it is, delete it
        os.remove(LOGFILE)

atexit.register(cleanup)

def login():
    username, password = eu.parse_secrets()
    session = david_api.query_api("login", [username, password])
    return session

def clear_row(stdscr, row):
    """Blank out the specified row"""
    _, width = curses.initscr().getmaxyx()
    stdscr.addstr(row, 0, " " * (width - 1), colours.WHITE_BLACK)


"""States"""
# Parent class
class State():
    pass

class StateMain(State):
    def __init__(self, args_dict):
        """Initialise the state"""
        stdscr = args_dict['stdscr']
        session = args_dict['session']
        self.stdscr = stdscr
        # Set up the david ascii art
        self.david_logo = os.path.join(os.path.dirname(__file__), "assets/david.png")

        # Get the version
        self.version = david_api.query_api("version")
        self.version = self.version['version']

        # Session
        self.session = session

        # Ticker
        self.ticker = Ticker(self.stdscr)

        self.menu_rows = 1

        self.david_ascii = None

    def generate_david_ascii(self):
        """Generate the ascii art"""
        # Get the ascii art
        self.david_ascii = AsciiImage(self.stdscr, self.david_logo, url=False, centre=True, dim_adjust=(0, self.menu_rows + 1))

    def update(self, args_dict):
        """Update the state"""
        curses.update_lines_cols()
        self.menu_rows = args_dict['menu_rows']
        # Update the ticker
        self.ticker.update()

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
        logging.info('cleaning up StateMain stuff')
        # Delete the ticker object
        del self.ticker
        # Delete the ascii object
        del self.david_ascii

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

class StateExit(State):
    def __init__(self, args_dict):
        """Initialise the state"""
        logging.info('initialising StateExit')
        self.stdscr = args_dict['stdscr']
        self.countdown = 3
        self.t = datetime.now()

    def update(self, args_dict):
        """Update the state, countdown to exit"""
        dt = datetime.now() - self.t
        self.countdown -= dt.total_seconds()
        self.t = datetime.now()
        if self.countdown <= 0:
            exit(0)

    def draw(self):
        """Draw the state"""
        self.stdscr.addstr("Goodbye!\n")

    def cleanup(self):
        """Clean up the state"""
        logging.info('cleaning up StateExit stuff')

def change_state(state, new_state, args_dict):
    """Changes the state"""
    state.cleanup()
    del state
    return new_state(args_dict)

def main(stdscr):
    """Main function"""
    # Instantiate the menu object
    # Set up some arbitrary menu items
    menu_items = ["Feed", "Bootlickers", "Bootlicking", "Catpets", "Pet Cat", "Exit", ]
    menu_states = [StateExit, StateExit, StateExit, StateExit, StateExit, StateExit]

    menu = Menu(stdscr, menu_items, menu_states, colours.WHITE_BLACK, colours.HIGHLIGHT)

    curses.curs_set(0)
    stdscr.clear()
    stdscr.addstr("Welcome to David Social!\n")
    stdscr.addstr("Logging you in...\n")
    stdscr.refresh()

    # Ping DS
    ping = david_api.query_api("ping")
    stdscr.clear()
    curses.curs_set(0)

    # If DS is down we won't get a version
    if ping is None:
        stdscr.addstr("Oh no, David Social is down!! :(")
        stdscr.refresh()
        sleep(3)
        exit(1)

    # Should probably actually login
    session = login()

    # Initial state is main
    instantiate_args = {
        'stdscr': stdscr,
        'session': session,
    }

    # Instantiate the state
    state = StateMain(instantiate_args)

    """Main loop"""
    while True:
        # Set up arguments
        instantiate_args = {}
        update_args = {}
        if isinstance(state, StateMain):
            update_args = {
                'menu_rows': menu.get_rows(),
            }

        # Update the state
        try:
            state.update(update_args)
        except Exception as e:
            logging.exception(e)
            exit(1)

        # Draw the state
        # Curses always fails when drawing, so we need to catch the exception
        stdscr.clear()
        curses.curs_set(0)
        try:
            state.draw()
        except:
            pass

        # Menuing
        try:
            function = menu.update()
            menu.draw()
            # I am in hell
            # I try to be a good programmer
            # And everything is just hell
            if function is not None:
                if issubclass(function, State):
                    logging.info(f"Changing state to {function}")
                    state = change_state(state, function, {'stdscr': stdscr})
                else:
                    function()
        except:
            pass

        stdscr.refresh()
        curses.doupdate()


wrapper(main)
