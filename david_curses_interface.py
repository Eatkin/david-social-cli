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
import scripts.argparse_utils as au
from scripts.console import console
from scripts.feed_utils import print_feed

def cleanup():
    """Cleanup curses and remove logfile if there are no logs"""
    curses.endwin()

    # Check if the logfile is empty
    if os.stat(LOGFILE).st_size == 0:
        # If it is, delete it
        os.remove(LOGFILE)

atexit.register(cleanup)

def logging_init():
    """Createss a logfile with the current date and time"""
    # Make a logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.mkdir("logs")
    # Create a logfile with the current date and time
    filename = f"logs/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    logging.basicConfig(filename=filename, level=logging.DEBUG, encoding="utf-8")
    return filename

def get_david_logo_ascii():
    """Returns ascii art of the David Social logo"""
    # Print out this very cool David Social logo
    david_logo = os.path.join(os.path.dirname(__file__), "assets/david.png")
    david_ascii = su.image_to_ascii(david_logo, url=False)
    return david_ascii

def main(stdscr):
    """Main function"""
    stdscr = curses.initscr()
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

    # Print welcome message
    stdscr.addstr(f"Welcome to David Social version {version}!")
    stdscr.refresh()
    sleep(2)
    pass

LOGFILE = logging_init()

wrapper(main)
