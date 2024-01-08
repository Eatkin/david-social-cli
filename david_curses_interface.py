import os
import logging
import atexit
import curses
from curses import wrapper
from datetime import datetime
from math import floor
import scripts.env_utils as eu
import scripts.api_routes as david_api
import scripts.string_utils as su
from scripts.feed_utils import print_feed
from scripts.menu import Menu

"""
TODO: Kill myself
TODO: Menu functionality, the menu is passed a list of states and returns the selected state
TODO: Set up state machine
TODO: The state machine is shit, should make class objects for each state
TODO: Then we can have init and update
TODO: That's going to be really fucking annoying
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
    return filename

LOGFILE = logging_init()

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
    stdscr.addstr(row, 0, " " * (width - 1), WHITE_BLACK)

def get_david_logo_ascii(dim_adjust=(0, 0)):
    """Returns ascii art of the David Social logo"""
    # Print out this very cool David Social logo
    david_logo = os.path.join(os.path.dirname(__file__), "assets/david.png")
    david_ascii = su.image_to_ascii(david_logo, url=False, dim_adjust=dim_adjust)
    return david_ascii

def print_ticker(stdscr, text, ticker_x):
    """Prints the ticker text with scrolling"""
    _, width = curses.initscr().getmaxyx()
    ticker_spacing = round(width * 0.2)
    # Print the ticker with ticker_x being the offset by exploding it into a list
    # We need to AT least double the ticker text so it can scroll seamlessly for example if text is very long
    ticker = list(text) + list(" " * ticker_spacing) + list(text)
    # Add enough repeats of the ticker text to fill the screen
    while len(ticker) < width * 2:
        ticker = ticker + list(" " * ticker_spacing) + ticker

    # Slice the ticker text to fit the screen
    ticker = ticker[ticker_x:ticker_x + width - 1]

    # Join the ticker back into a string
    ticker = "".join(ticker)
    # Print the ticker with a colour pair
    stdscr.addstr(ticker, curses.A_ITALIC | YELLOW_BLACK)

    # Wrap ticker_x
    if ticker_x >= len(text) + ticker_spacing:
        ticker_x = 0

    return ticker_x


"""States"""
class StateMain():
    def __init__(self, args_dict):
        stdscr = args_dict['stdscr']
        session = args_dict['session']
        self.stdscr = stdscr
        # Set up the david ascii art
        self.david_ascii = get_david_logo_ascii()
        self.ascii_width = len(self.david_ascii.split("\n")[0])
        centre = floor((curses.COLS - self.ascii_width)/2)
        # Centre the ascii art
        self.print_ascii = "\n".join([" "*centre + line for line in self.david_ascii.split("\n")])

        # Ascii dims
        self.ascii_max_height, self.ascii_max_width = self.stdscr.getmaxyx()

        # Get the version
        self.version = david_api.query_api("version")
        self.version = self.version['version']

        # Session
        self.session = session

        # Ticker
        self.ticker_text = david_api.query_api("get-ticker-text")
        if self.ticker_text is None:
            self.ticker_text = "Ticker unavailable"

        self.ticker_x = 0
        self.ticker_update_rate = 0.2
        self.t = datetime.now()
        self.menu_rows = 1


    def update(self, args_dict):
        curses.update_lines_cols()
        self.menu_rows = args_dict['menu_rows']

    def update_ascii(self):
        # Get any new ascii dims
        new_max_height, new_max_width = curses.initscr().getmaxyx()
        new_max_height -= self.menu_rows + 1

        if new_max_height != self.ascii_max_height or new_max_width != self.ascii_max_width:
            self.ascii_max_height, self.ascii_max_width = new_max_height, new_max_width
            # Regenerate ascii at new size
            # First check if this is necessary
            ascii_width = len(self.print_ascii.split("\n")[0])
            ascii_height = len(self.david_ascii.split("\n"))
            if self.ascii_max_height != ascii_height or self.ascii_max_width != ascii_width:
                # Re-generate the ascii
                self.david_ascii = get_david_logo_ascii(dim_adjust=(0, self.menu_rows + 1))

            # Redefine the ascii width (we want the width without padding)
            ascii_width = len(self.david_ascii.split("\n")[0])

            # Re-centre the ascii by padding
            centre = floor((self.ascii_max_width  - ascii_width)/2)
            self.print_ascii = "\n".join([" "*centre + line for line in self.david_ascii.split("\n")])

        new_max_height -= self.menu_rows + 1

    def cleanup(self):
        logging.info('cleaning up StateMain stuff')

    def draw(self):
        self.ticker_x = print_ticker(self.stdscr, self.ticker_text, self.ticker_x)
        dt = datetime.now() - self.t
        if dt.total_seconds() > self.ticker_update_rate:
            self.t = datetime.now()
            self.ticker_x += 1

        self.stdscr.addstr("\n")
        welcome_message = f"Welcome to David Social version {self.version}!"
        # Centre the welcome message
        _, max_width = curses.initscr().getmaxyx()
        max_width -= 1
        centre = round((max_width - len(welcome_message))/2)
        self.stdscr.addstr(" "*centre + welcome_message + "\n")

        self.update_ascii()
        # Print the ascii
        self.stdscr.addstr(self.print_ascii)

class StateExit():
    def __init__(self, args_dict):
        logging.info('initialising StateExit')
        self.stdscr = args_dict['stdscr']
        self.countdown = 3
        self.t = datetime.now()

    def update(self, args_dict):
        dt = datetime.now() - self.t
        self.countdown -= dt.total_seconds()
        self.t = datetime.now()
        if self.countdown <= 0:
            exit(0)

    def draw(self):
        self.stdscr.addstr("Goodbye!\n")

    def cleanup(self):
        logging.info('cleaning up StateExit stuff')

def change_state(state, new_state, args_dict):
    """Changes the state"""
    state.cleanup()
    del state
    return new_state(args_dict)

def main(stdscr):
    """Main function"""
    # Initialise curses
    stdscr = curses.initscr()

    # Constants
    # Colours - these MUST be globals because of some curses shit idk
    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    global YELLOW_BLACK
    YELLOW_BLACK = curses.color_pair(1)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    global HIGHLIGHT
    HIGHLIGHT = curses.color_pair(2)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
    global WHITE_BLACK
    WHITE_BLACK = curses.color_pair(3)

    # Instantiate the menu object
    # Set up some arbitrary menu items
    menu_items = ["Feed", "Bootlickers", "Bootlicking", "Catpets", "Pet Cat", "Exit", ]
    menu_states = [StateExit, StateExit, StateExit, StateExit, StateExit, StateExit]

    menu = Menu(stdscr, menu_items, menu_states, WHITE_BLACK, HIGHLIGHT)

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
        stdscr.addstr("Oh no, David Social is down!! How will we ever survive? :(")
        stdscr.refresh()
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
            new_state = menu.update()
            menu.draw()
            if new_state is not None:
                logging.info(f"Changing state to {new_state}")
                state = change_state(state, new_state, {'stdscr': stdscr})
        except:
            pass

        stdscr.refresh()
        curses.doupdate()


wrapper(main)
