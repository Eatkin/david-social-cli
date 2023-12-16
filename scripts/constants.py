# Set up enums
class State:
    """Enum for the state of the app"""
    HOME = 0
    LOGIN = 1
    FEED = 2

# Menu is a dictionary of lists
# The keys are the states
menu = {
    State.HOME: ['Login', 'Contact David', 'Exit'],
}
