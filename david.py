import os
import logging
import atexit
import curses
from curses import wrapper
from datetime import datetime
from time import sleep
import scripts.secrets as secrets
import scripts.config as config
import scripts.api_routes as david_api
from scripts.states import StateMain
import scripts.config as config

# Initialise curses
stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
curses.start_color()

# Get log clearing setting
config_dict = config.read_config()
clear_logs = config_dict['clear_logs']

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
    """Cleanup curses and remove logfile if empty or if logs should be cleared"""
    curses.endwin()

    # Check if the logfile is empty or if logs should be cleared
    if os.stat(LOGFILE).st_size == 0 or clear_logs:
        # If it is, delete it
        os.remove(LOGFILE)

atexit.register(cleanup)

def login():
    username, password = secrets.parse_secrets()
    if username is None or password is None:
        stdscr.clear()
        stdscr.addstr("Username or password not found\n")
        stdscr.addstr("Credentials may be provided as environment variables (DAVID_USERNAME, DAVID_PASSWORD)\n")
        stdscr.addstr("Alternatively you can fill in secret.YAML\n")
        stdscr.refresh()
        sleep(7)
        exit(1)

    session = david_api.query_api("login", [username, password])

    if session is None:
        stdscr.clear()
        stdscr.addstr("Login failed\n")
        stdscr.addstr("Check your username and password\n")
        stdscr.addstr("They should be defined as environment variables (DAVID_USERNAME, DAVID_PASSWORD)\n")
        stdscr.addstr("Alternatively you can fill in secret.YAML\n")
        logging.error("Login failed")
        stdscr.refresh()
        sleep(7)
        exit(1)
    return session

def main(stdscr):
    """Main function"""
    # Read config for refresh rate
    config_dict = config.read_config()
    refresh_rate = config_dict['refresh_rate']

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
        try:
            state.draw()
        except Exception as e:
            # Only enable this if you REALLY NEED TO DEBUG
            # Because otherwise it will print a billion errors if you try resize the window
            # logging.exception(e)
            pass

        stdscr.refresh()
        curses.doupdate()

        # Sleep interval seems to prevent flickering
        sleep(refresh_rate)


wrapper(main)
