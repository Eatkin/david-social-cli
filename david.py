import scripts.toml_utils as tu
import scripts.chromium_utils as cu
import scripts.menu_utils as mu
import scripts.api_routes as david_api
from rich.markdown import Markdown
from scripts.constants import State
from scripts.console import console

# Set up global variables
ticker = None
feed = None

# Set up state
state = State.HOME

# Check the API routes
console.print("Checking API routes...", end="\n\r")
missing_routes = david_api.validate_routes()

console.print("Loading David Social...", end="\n\r")

# Get our username
username, _ = tu.get_secrets()
del _

# Main loop
while True:
    if state == State.HOME:
        # Get the homepage
        homepage_soup = cu.get_david_homepage()
        homepage_content = cu.parse_soup(homepage_soup)

        # Homepage is in markdown format so parse it with rich
        homepage_markdown = Markdown(homepage_content)

        console.print(homepage_markdown)
        console.print("-" * 80, end="\n\r")
    elif state == State.LOGGED_IN:
        # We've just logged in so display the ticker and ask user for input
        # Get the ticker (once)
        # TODO: if we update the ticker we need to update this
        if ticker is None:
            ticker = cu.get_david_ticker()
        console.print("-" * 80, end="\n\r")
        console.print("Welcome to David Social!", end="\n\r")
        console.print("Ticker: " + ticker, end="\n\r")
        console.print("-" * 80, end="\n\r")

        # We can use API routes to get the feed and things
        if feed is None:
            feed = david_api.get_bootlicker_feed(username)

    # Display our menu options
    menu_options = mu.menu[state]

    # Print out menu options
    for option in menu_options:
        console.print(f"({option[0]}){option[1:]}", end="\n\r")

    # Get the user's input
    user_input = ""
    valid_inputs = [option[0].lower() for option in menu_options]
    while user_input not in valid_inputs:
        user_input = console.input("Please select an option: ",)

    # Perform the relevant action
    menu_index = valid_inputs.index(user_input)
    # Execute the command in menu_functions
    function = mu.menu_functions[state][menu_index]
    success = function()

    # Change state if required
    if function == mu.login_wrapper:
        if success:
            state = State.LOGGED_IN
        else:
            state = State.HOME
    elif function == mu.update_ticker_wrapper:
        # Set ticker to none because we've updated it
        if success:
            ticker = None
