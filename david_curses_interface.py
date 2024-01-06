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

def print_ticker(stdscr, text, ticker_x):
    """Prints the ticker text with scrolling"""
    width = curses.COLS
    ticker_spacing = round(width * 0.2)
    # Print the ticker with ticker_x being the offset by exploding it into a list
    ticker = list(text)
    # Add enough repeats of the ticker text to fill the screen
    while len(ticker) < width * 2:
        ticker = ticker + list(" " * ticker_spacing) + ticker

    # Slice the ticker text to fit the screen
    ticker = ticker[ticker_x:ticker_x + width - 1]

    # Join the ticker back into a string
    ticker = "".join(ticker)
    # Print the ticker with a colour pair
    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    YELLOW_BLACK = curses.color_pair(1)
    stdscr.addstr(ticker, curses.A_ITALIC | curses.A_BLINK | YELLOW_BLACK)

    # Wrap ticker_x
    if ticker_x >= len(text) + ticker_spacing:
        ticker_x = 0

    return ticker_x

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
        # Print welcome message
        stdscr.clear()
        curses.curs_set(0)
        # Print the ticker text and handle scrolling
        ticker_x = print_ticker(stdscr, ticker_text, ticker_x)
        dt = datetime.now() - t
        if dt.total_seconds() > ticker_update_rate:
            t = datetime.now()
            ticker_x += 1

        stdscr.addstr("\n\n")
        stdscr.addstr(f"Welcome to David Social version {version}!")

        stdscr.refresh()
        curses.doupdate()

LOGFILE = logging_init()

wrapper(main)
