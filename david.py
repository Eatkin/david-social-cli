import scripts.toml_utils as tu
import scripts.chromium_utils as cu
import scripts.menu_utils as mu
from rich.markdown import Markdown
from scripts.constants import State
from scripts.console import console

# Set up state
state = State.HOME

console.print("Loading David Social...", end="\n\r")

# Main loop
while True:
    if state == State.HOME:
        # Get the homepage
        homepage_soup = cu.get_david_homepage()
        homepage_content = cu.parse_soup(homepage_soup)

        # Homepage is in markdown format so parse it with rich
        homepage_markdown = Markdown(homepage_content)

        console.print(homepage_markdown)
    elif state == State.LOGIN:
        # Get the username and password
        username, password = tu.get_secrets()

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
    mu.menu_functions[state][menu_index]()
