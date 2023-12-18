from scripts.constants import State
from scripts.console import console
from scripts.chromium_utils import login, post_to_david_social, update_david_ticker


# Menu states and functions
# The functions are just aliases for the states
def quit():
    console.print("Thank you for using David Social!")
    exit()

def contact_david():
    console.print("David may be contacted if you wish to join David Social or if you have forgotten your password", end="\n\r")
    console.print("You'll have to ask David for his email though")
    return True

def login_wrapper():
    success = login()
    return success

def post_wrapper():
    post_to_david_social()
    return True

def update_ticker_wrapper():
    update_david_ticker()
    return True


# Menu is a dictionary of lists
# The keys are the states
menu = {
    State.HOME: ['Login', 'Contact David', 'Exit'],
    State.LOGGED_IN: ['Update ticker', 'Make a post', 'Feed', 'Profile', 'Search', 'Read news', 'Notifications', 'Exit']
}

menu_functions = {
    State.HOME: [login_wrapper, contact_david, quit],
    State.LOGGED_IN: [update_ticker_wrapper, post_wrapper, quit, quit, quit, quit, quit, quit]
}
