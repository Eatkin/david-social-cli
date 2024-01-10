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
from scripts.states import State, StateMain, StateExit

"""
TODO: Kill myself
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

def change_state(state, new_state, stdscr, session, logger):
    """Changes the state"""
    state.cleanup()
    del state
    return new_state(stdscr, session, logger)

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
            update = state.update()
            if update is not None:
                state = change_state(state, update, stdscr, session, LOGGER)
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

        stdscr.refresh()
        curses.doupdate()


wrapper(main)
