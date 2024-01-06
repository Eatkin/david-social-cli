from time import sleep
import curses
from curses import wrapper
import scripts.env_utils as eu
import scripts.api_routes as david_api
import scripts.string_utils as su
import scripts.argparse_utils as au
from scripts.console import console
from scripts.feed_utils import print_feed

def main(stdscr):
    stdscr.clear()
    curses.curs_set(0)
    stdscr.addstr("Loading David Social...")
    stdscr.refresh()

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
    stdscr.addstr(f"Welcome to David Social version {version}")
    stdscr.refresh()
    sleep(2)
    pass

wrapper(main)
