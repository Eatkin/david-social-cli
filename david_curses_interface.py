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
TODO: Create a Menu class instead of what I'm doing now
TODO: Create a git branch so I don't fuck everything up lol
TODO: Kill myself
TODO: Menu navigation
TODO: Menu lambda functions
TODO: Set up state machine
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
    logging.basicConfig(filename=filename, level=logging.WARNING, encoding="utf-8")
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
    menu_items = ["Feed", "Bootlickers", "Bootlicking", "Catpets", "Pet Cat", "Exit", "fdsiOFA", "fds", "FDSfdoihfdsa"]
    menu = Menu(stdscr, menu_items, [], WHITE_BLACK, HIGHLIGHT)

    curses.curs_set(0)
    stdscr.clear()
    stdscr.addstr("Welcome to David Social!\n")
    stdscr.addstr("Logging you in...\n")
    stdscr.refresh()

    # Set up the david ascii art
    david_ascii = get_david_logo_ascii()
    ascii_width = len(david_ascii.split("\n")[0])
    centre = floor((curses.COLS - ascii_width)/2)
    # Centre the ascii art
    print_ascii = "\n".join([" "*centre + line for line in david_ascii.split("\n")])

    # Get available space for the ascii
    ascii_max_height, ascii_max_width = curses.initscr().getmaxyx()

    # Ping DS
    version = david_api.query_api("version")
    version = version['version']
    stdscr.clear()
    curses.curs_set(0)

    # If DS is down we won't get a version
    if version is None:
        stdscr.addstr("Oh no, David Social is down!! How will we ever survive? :(")
        stdscr.refresh()
        exit(1)

    # Should probably actually login
    session = login()

    # Get the ticker text
    ticker_text = david_api.query_api("get-ticker-text")
    # Log the ticker text
    logging.info(f"Ticker text: {ticker_text}")
    if ticker_text is None:
        ticker_text = "Ticker unavailable"
    ticker_x = 0
    # Scrolling ticker text causes some glitching which is annoying
    ticker_update_rate = 0.2
    t = datetime.now()

    # Main loop
    while True:
        # Update the terminal size
        curses.update_lines_cols()
        # Print welcome message
        stdscr.clear()
        curses.curs_set(0)
        # Print the ticker text and handle scrolling
        ticker_x = print_ticker(stdscr, ticker_text, ticker_x)
        dt = datetime.now() - t
        if dt.total_seconds() > ticker_update_rate:
            t = datetime.now()
            ticker_x += 1

        stdscr.addstr("\n")
        welcome_message = f"Welcome to David Social version {version}!"
        # Centre the welcome message
        _, max_width = curses.initscr().getmaxyx()
        max_width -= 1
        centre = round((max_width - len(welcome_message))/2)
        stdscr.addstr(" " * centre + welcome_message, curses.A_BLINK)
        stdscr.addstr("\n")

        # Detect Terminal resize
        new_max_height, new_max_width = curses.initscr().getmaxyx()

        new_max_height -= menu.get_rows() + 1

        try:
            if new_max_height != ascii_max_height or new_max_width != ascii_max_width:
                # Update the height and width
                ascii_max_height = new_max_height
                ascii_max_width = new_max_width
                # Ascii will need to be re-generated if width < ascii_width
                # This will probably be a bit slow
                # This is based on the print ascii which is dynamically resized by padding
                ascii_width = len(print_ascii.split("\n")[0])
                ascii_height = len(david_ascii.split("\n"))
                if ascii_max_height != ascii_height or ascii_max_width != ascii_width:
                    # Re-generate the ascii
                    david_ascii = get_david_logo_ascii(dim_adjust=(0, menu.get_rows() + 1))

                # Redefine the ascii width (we want the width without padding)
                ascii_width = len(david_ascii.split("\n")[0])

                # Re-centre the ascii by padding
                centre = floor((ascii_max_width  - ascii_width)/2)
                print_ascii = "\n".join([" "*centre + line for line in david_ascii.split("\n")])

            # Print the ascii
            stdscr.addstr(print_ascii)
        except:
            pass

        # Print menu
        try:
            menu.draw()
        except:
            pass

        stdscr.refresh()
        curses.doupdate()


wrapper(main)
