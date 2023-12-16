from scripts.constants import State
from scripts.console import console
import scripts.toml_utils as tu
from scripts.chromium_utils import login


# Menu states and functions
# The functions are just aliases for the states
def quit():
    console.print("Thank you for using David Social!")
    exit()

def contact_david():
    console.print("David may be contacted if you wish to join David Social or if you have forgotten your password", end="\n\r")
    console.print("You'll have to ask David for his email though")

def login_wrapper():
    username, password = tu.get_secrets()
    success = login(username, password)


# Menu is a dictionary of lists
# The keys are the states
menu = {
    State.HOME: ['Login', 'Contact David', 'Exit'],
}

menu_functions = {
    State.HOME: [login_wrapper, contact_david, quit]
}
