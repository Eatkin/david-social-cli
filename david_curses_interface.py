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
from scripts.menu import Menu

"""
TODO: Kill myself
TODO: Pass menu object to states so they can use it and update as necessary
TODO: Make ascii image class object
TODO: Make a colours enum?? idk
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

"""Classes"""
class Ticker():
    """Ticker class"""
    def __init__(self, stdscr):
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
        self.stdscr.addstr(self.ticker, curses.A_ITALIC | YELLOW_BLACK)

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

        self.generate_david_ascii()

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
        # Get any new ascii dims
        new_max_height, new_max_width = curses.initscr().getmaxyx()
        new_max_height -= self.menu_rows + 1

        ascii_width, ascii_height = self.david_ascii.get_dims()

        # Make sure the ascii is not too big for the available space
        if ascii_width > new_max_width or ascii_height > new_max_height:
            # Resize the ascii
            del self.david_ascii
            self.generate_david_ascii()

    def cleanup(self):
        """Clean up the state"""
        logging.info('cleaning up StateMain stuff')
        # Delete the ticker object
        del self.ticker

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
