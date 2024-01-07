import os
import logging
from datetime import datetime
import atexit
from time import sleep
import curses
from curses import wrapper
import scripts.env_utils as eu
import scripts.api_routes as david_api
import scripts.string_utils as su
from scripts.feed_utils import print_feed

"""
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


def get_david_logo_ascii():
    """Returns ascii art of the David Social logo"""
    # Print out this very cool David Social logo
    david_logo = os.path.join(os.path.dirname(__file__), "assets/david.png")
    david_ascii = su.image_to_ascii(david_logo, url=False)
    return david_ascii

def print_ticker(stdscr, text, ticker_x):
    """Prints the ticker text with scrolling"""
    width = curses.COLS
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
    stdscr.addstr(ticker, curses.A_ITALIC | curses.A_BLINK | YELLOW_BLACK)

    # Wrap ticker_x
    if ticker_x >= len(text) + ticker_spacing:
        ticker_x = 0

    return ticker_x

def update_menu(stdscr, items):
    """Prints menu items and handles inputs"""
    # Just need to print the menu items
    # Get the Terminal size
    HEIGHT, WIDTH = curses.initscr().getmaxyx()
    longest_item = max(items, key=len)
    longest_item = len(longest_item)
    # Set the coordinates of the menu items
    # These will be tuples giving x/y offests
    coords = []
    rows = 0
    current_width = 0
    for item in items:
        if current_width + longest_item + 1 > WIDTH:
            current_width = 0
            rows += 1
            centre = round((longest_item - len(item))/2)
            coords.append((current_width + centre, rows))
        else:
            # Append this before adjusting the width
            centre = round((longest_item - len(item))/2)
            coords.append((current_width + centre, rows))
            # Consistent spacing
            current_width += longest_item + 1

    x = 0
    y = HEIGHT - rows - 1

    # Print the menu items
    for item in items:
        x_offset, y_offset = coords.pop(0)
        col = HIGHLIGHT if sum(MENU_SELECTION) == items.index(item) else WHITE_BLACK
        stdscr.addstr(y + y_offset, x + x_offset, item, col)

    # Now handle some menu navigation
    # We know how many rows and columns we have so we can wrap and stuff



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
    # Menuing
    global MENU_SELECTION
    MENU_SELECTION = (0, 0)

    curses.curs_set(0)
    stdscr.clear()
    stdscr.addstr("Welcome to David Social!\n")
    # Print out the David logo
    david_ascii = get_david_logo_ascii()
    # Set cursor to the next line
    stdscr.addstr(david_ascii)
    stdscr.refresh()

    sleep(1)

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

    # Set up some arbitrary menu items
    menu_items = ["Feed", "Bootlickers", "Bootlicking", "Catpets", "Pet Cat", "Exit", "fdsiOFA", "fds", "FDSfdoihfdsa"]
    # Main loop
    while True:
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
        stdscr.addstr(f"Welcome to David Social version {version}!")

        # Print menu
        update_menu(stdscr, menu_items)

        stdscr.refresh()
        curses.doupdate()


wrapper(main)
