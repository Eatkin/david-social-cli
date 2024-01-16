# David Social Command Line Interface
## Description
This is a command line interface so you can use [David Social](https://www.davidsocial.com) from your Terminal.

It uses the David Social API and allows you to read posts from your friends, like things, make new posts, pet cats and check out the profiles of your David Social crushes (i.e. everyone on David Social).

## Requirements
* Built with Python 3.11.0
* Required libraries are listed in requirements.txt
* You will need a David Social account to use this CLI. You can sign up by asking David to make you an account.
* (OPTIONAL) [Pyenv](https://github.com/pyenv/pyenv) for a virtual environment

## Installation
### Using Make
1. Clone this repository
2. make all will setup a Pyenv virtual environment and install the required libraries
3. Run the CLI with `python david.py`

### Manually
1. Clone this repository
2. (OPTIONAL) Setup a virtual environment with Pyenv
3. Install the required libraries with `pip install -r requirements.txt`
4. Run the CLI with `python david.py`

## Usage
### Login
1. Run the CLI with `python david.py`
2. Login credentials can either be provided through environment variables (DAVID_USERNAME and DAVID_PASSWORD) or by filling in secrets.yaml. YAML files will be created if they do not exist.
3. You may hardcode your credentials in scripts/secrets.py which is probably very insecure.
4. If you do not have a David Social account, you can sign up by asking David to make you an account.

### Configuration
1. config.yaml will be created if it does not exist. This file contains the configuration for the CLI.
2. Default configuration is:
```
preserve_feed_position: false
refresh_rate: 0.1
clear_logs: false
```
* preserve_feed_position: If true, the CLI will remember your position in the feed when you leave a feed view and return to it. Otherwise feeds will always start at the first post.
* refresh_rate: The rate at which the Terminal refreshes. Lower values refresh faster, but this can cause flickering. Increase this value if you experience flickering.
* clear_logs: If true, the CLI will clear the log files when you exit. Otherwise log files will be preserved.

### Commands
The CLI uses Curses to display the interface. You can use the arrow keys to navigate the interface. Pressing enter will select an option.

## Issues
* Resizing the Terminal can cause the interface to break. If this happens, restart the CLI.
* If the interface does not respond or crashes, view the log files in the logs directory for more information. If you are unable to resolve the issue, please open an issue on this repository.

## Future Plans and Limitations
* Add a way of searching the David Social userbase
* You cannot follow (bootlick) users through the CLI
* You cannot edit your profile through the CLI
