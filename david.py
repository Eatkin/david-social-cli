#!/usr/bin/env

import os
import sys
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
import scripts.file_utils as utils

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
    base_dir = f"{utils.get_home_dir()}/.david_logs"
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
    # Create a logfile with the current date and time
    log_level = logging.DEBUG if "--logs" in sys.argv else logging.CRITICAL        
    filename = f"{base_dir}/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    logging.basicConfig(filename=filename, level=log_level, encoding="utf-8")
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

    # Clear cached username
    try:
        os.remove("username.txt")
    except:
        pass

atexit.register(cleanup)

def get_credentials(overwrite=False):
    curses.echo()
    stdscr.clear()
    if not overwrite:
        stdscr.addstr("No credentials file found\n")

    # Get user input
    while True:
        stdscr.addstr("Enter your username: ")
        username = stdscr.getstr().decode()
        stdscr.addstr("Enter your password: ")
        password = stdscr.getstr().decode()
        stdscr.addstr("Is this correct? (y/n): ")
        confirm = stdscr.getstr().decode().lower()
        if confirm == "y":
            break
        else:
            stdscr.clear()
            stdscr.refresh()

    save_creds = False
    # Ask if user wants to save credentials
    while True:
        stdscr.clear()
        confirmation_message = "Do you want to save your credentials? (y/n): "
        if overwrite:
            confirmation_message = "Do you want to overwrite your credentials? (y/n): "
        stdscr.addstr(confirmation_message)
        confirm = stdscr.getstr().decode().lower()
        logging.info(f"save_creds: {save_creds}")
        if confirm.lower() == "y":
            save_creds = True
            break
        elif confirm.lower() == "n":
            break
        else:
            stdscr.clear()
            stdscr.refresh()

    curses.noecho()

    if save_creds:
        logging.info("Saving credentials to ~/")
        stdscr.addstr(f"saving credentials to ~/")
        secrets.write_secrets(username, password)
    else:
        logging.info("Not saving credentials")
        logging.info("Caching username in file")
        # Cache the username in a file
        with open("username.txt", "w") as f:
            f.write(username)

    return username, password

def login():
    """Gets the user's credentials and logs them in"""
    # Check if credentials are saved
    username, password = secrets.parse_secrets()

    # If not get them from input
    if username is None or password is None:
        username, password = get_credentials()
    else:
        # If they are we ask if they want to use saved credentials
        while True:
            curses.echo()
            stdscr.clear()
            stdscr.addstr("Do you want to use the saved credentials? (y/n): ")
            confirm = stdscr.getstr().decode().lower()
            if confirm == "y":
                break
            elif confirm == "n":
                username, password = get_credentials(overwrite=True)
                break
            else:
                stdscr.clear()
                stdscr.refresh()

        curses.noecho()


    session = david_api.query_api("login", [username, password])

    if session is None:
        stdscr.clear()
        stdscr.addstr("Login failed\n")
        secrets.clear_secrets()
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
