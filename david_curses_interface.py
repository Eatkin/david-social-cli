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
from scripts.states import State, StateMain, StateTextEntry

"""
TODO: Why does ASCII art flicker in full screen? Maybe something to do with curses failing to draw?
TODO: Why does pressing escape pause everything?
"""

# Initialise curses
stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
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

def main(stdscr):
    """Main function"""
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
    # Instantiate the state
    state = StateMain(stdscr, session, LOGGER)

    """Main loop"""
    while True:
        # Update the state
        # If it returns a state then we need to change state
        # Otherwise it will return None and we continue normal execution
        try:
            new_state = state.update()
            if new_state is not None:
                state = new_state
                logging.info(f"Changed state to {state}")
        except Exception as e:
            logging.exception(e)

        # Draw the state
        # Curses always fails when drawing, so we need to catch the exception
        stdscr.clear()
        curses.curs_set(0)
        try:
            state.draw()
        except Exception as e:
            # Only enable this if you REALLY NEED TO DEBUG
            # Because otherwise it will print a billion errors if you try resize the window
            logging.exception(e)
            pass

        stdscr.refresh()
        curses.doupdate()

        # Sleep interval seems to prevent flickering
        # We ignore this if we're in text input mode
        sleep(0.1)


wrapper(main)
