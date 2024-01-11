import curses
import os
import requests
from io import BytesIO
from PIL import Image
from enum import Enum
from datetime import datetime
from scripts.ds_components import Menu, Ticker, AsciiImage, Feed
import scripts.api_routes as david_api
from scripts.colours import ColourConstants
import scripts.env_utils as eu

# TODO: Feed state has a divider of "-" between posts, this doesn't get resized if Terminal is resized

# TODO: Add a ticker update state
# TODO: Remember to check for conditions for when the ticker update is invalid (see what the api returns)
# TODO: Remember to update ticker in StateMain() if we are on the ticker update state (I have no idea how to do this rn, states can't communicate with each other)
# TODO: ^ MAYBE an optional callback function can be included in the standard dictionary for menu items
# TODO: Add a cat petting state

# OPTIONAL TODO: Create an object for menu functions instead of using dictionaries

# We need to create a feeds dictionary to store the feed objects so we can save our place in them
feeds = {}

# Create special keywords for bootlicker and global feeds for use in the feeds dictionary
# This is to ensure they are differentiated from user feeds
# But for example if there was a user called 'bootlicker' that would cause issues
class FeedType(Enum):
    BOOTLICKER = 0
    GLOBAL = 1

# State history for regressing to a previous state
state_history = []

class State():
    def update(self):
        """Update the state"""
        # Update the menu
        update = self.menu.update()
        if update is None:
            return None

        if update['type'] == 'state_change':
            # Create an instance of the state
            state = update['state'](*update['args'])
            # Call the associated function with the state as the argument
            return update['function'](state)
        elif update['type'] == 'function':
            # Call the associated function
            return update['function'](*update['args'])

        return None

    def draw(self):
        """Draw the state"""
        # Draw the menu
        self.menu.draw()

    def cleanup(self):
        """Clean up the state"""
        # Delete menu
        del self.menu

    def advance_state(self, state):
        """Advance the state"""
        # Add the current state to the history
        state_history.append(self)

        # state is an object so we can just return it
        return state

    def regress_state(self):
        """Regress the state"""
        # Cleanup
        self.cleanup()
        # Now revert to the previous state
        previous_state = state_history.pop()
        return previous_state

class StateMain(State):
    def __init__(self, stdscr, session, logger):
        """Initialise the state"""
        self.stdscr = stdscr
        self.session = session
        self.logger = logger

        self.logger.info('initialising StateMain')
        # Set up the david ascii art
        # Get the path to the david ascii art - first go up a directory, then go into assets
        self.david_logo = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets/david.png")

        # Get the version
        self.version = david_api.query_api("version")
        self.version = self.version['version']

        # Session
        self.session = session

        # Ticker
        self.ticker = Ticker(self.stdscr)

        self.menu_rows = 1

        self.david_ascii = None

        # Initialise the menu
        menu_items = ["Bootlicker Feed", "Global Feed", "Bootlicking", "Catpets", "Pet Cat", "Exit", ]
        menu_states = [
                {
                    'type': 'state_change',
                    'function': self.advance_state,
                    'state': StateFeed,
                    'args': (self.stdscr, self.session, self.logger, "Bootlicker")
                },
                {
                    'type': 'state_change',
                    'function': self.advance_state,
                    'state': StateFeed,
                    'args': (self.stdscr, self.session, self.logger, "Global")
                },
                # Placeholders
                {
                    'type': 'state_change',
                    'function': self.advance_state,
                    'state': StateExit,
                    'args': (self.stdscr, self.session, self.logger)
                },
                {
                    'type': 'state_change',
                    'function': self.advance_state,
                    'state': StateExit,
                    'args': (self.stdscr, self.session, self.logger)
                },
                {
                    'type': 'state_change',
                    'function': self.advance_state,
                    'state': StateExit,
                    'args': (self.stdscr, self.session, self.logger)
                },
                {
                    'type': 'state_change',
                    'function': self.advance_state,
                    'state': StateExit,
                    'args': (self.stdscr, self.session, self.logger)
                },
                ]
        self.menu = Menu(self.stdscr, menu_items, menu_states)

    def generate_david_ascii(self):
        """Generate the ascii art"""
        # Get the ascii art
        self.david_ascii = AsciiImage(self.stdscr, self.david_logo, url=False, centre=True, dim_adjust=(0, self.menu_rows + 1))

    def update(self):
        """Update the state"""
        curses.update_lines_cols()
        self.menu_rows = self.menu.get_rows()
        # Update the ticker
        self.ticker.update()

        # Call the parent update function
        return super().update()

    def update_ascii(self):
        """Update ascii to fit the terminal"""
        # We need to generate the ascii if it doesn't exist
        # This makes sure it is generated with the correct dimensions (accounting for menu)
        # If we generate it initially it will be generated with the wrong dimensions
        if self.david_ascii is None:
            self.generate_david_ascii()
            return

        # Pass the new dimensions to the ascii object
        self.david_ascii.set_dim_adjust((0, self.menu_rows + 1))

        # Use the ascii image's update function
        self.david_ascii.update()


    def cleanup(self):
        """Clean up the state"""
        self.logger.info('cleaning up StateMain stuff')
        # Delete the ticker object
        del self.ticker
        # Delete the ascii object
        del self.david_ascii
        super().cleanup()

    def draw(self):
        """Draw the state"""
        # Print the ticker
        self.ticker.draw()

        self.stdscr.addstr("\n")
        welcome_message = f"Welcome to David Social version {self.version}!"
        # Centre the welcome message
        _, max_width = curses.initscr().getmaxyx()
        max_width -= 1
        centre = round((max_width - len(welcome_message))/2)
        self.stdscr.addstr(" "*centre + welcome_message + "\n")

        # Call update ascii here because we know the available space
        self.update_ascii()

        # Print the ascii
        self.david_ascii.draw()

        # Call the parent draw function
        super().draw()

class StateExit(State):
    def __init__(self, stdscr, session, logger):
        """Initialise the state"""
        self.logger = logger
        self.logger.info('initialising StateExit')
        self.stdscr = stdscr
        self.countdown = 3
        self.t = datetime.now()
        # Create blank menu
        self.menu = Menu(self.stdscr, [], [])

    def update(self):
        """Update the state, countdown to exit"""
        dt = datetime.now() - self.t
        self.countdown -= dt.total_seconds()
        self.t = datetime.now()
        if self.countdown <= 0:
            exit(0)

        super().update()

    def draw(self):
        """Draw the state"""
        self.stdscr.addstr("Goodbye!\n")

        super().draw()

    def cleanup(self):
        """Clean up the state"""
        self.logger.info('cleaning up StateExit stuff')
        del self.menu

class StateFeed(State):
    # TODO: ASCII art for attached images to fill space (NOT TESTED)
    # TODO: View attached image (needs an image viewer state plus should be able to open it properly as ASCII)
    # TODO: ^ MAYBE that, but at the moment it's just ascii and open with PIL
    # TODO: Reply to post (needs a reply state)
    # TODO: View replies (can use API request plus create a new feed state for this)
    # TODO: ^ As above, the feed state needs to have a special case for replies
    # TODO: Option to bootlick a user if we aren't already bootlicking them
    def __init__(self, stdscr, session, logger, feed_type, user_feed=None):
        """Initialise the state"""
        self.stdscr = stdscr
        self.session = session
        self.logger = logger

        # This is the name of the user feed we are viewing
        self.user_feed = user_feed

        # Set up the feed
        self.feed_type = feed_type
        self.feed_key = FeedType.BOOTLICKER if self.feed_type == "Bootlicker" else FeedType.GLOBAL if self.feed_type == "Global" else self.user_feed
        if self.feed_key in feeds:
            self.feed = feeds[self.feed_key]
        else:
            self.feed = Feed(self.session, self.feed_type, self.user_feed)
            # Add our feed to the feeds dictionary
            feeds[self.feed_key] = self.feed

        # Setup menu functions
        self.setup_menu_functions()

        self.menu = Menu(self.stdscr, [], [])

        self.current_post = self.feed.get_post(self.feed.post_index)

        # Initialise colours
        self.colours = ColourConstants()
        self.colours.init_colours()

        # Get our username
        self.username, _ = eu.parse_secrets()
        del _

        # Some miscellaneous variables
        self.have_liked = self.post_is_liked()
        self.attached_image = ""

        # Now update the menu
        self.update_menu()

    def setup_menu_functions(self):
        """Defines functions used by the menu"""
        self.next_post_func = {
            'type': 'function',
            'function': self.next_post,
            'args': []
        }
        self.prev_post_func = {
            'type': 'function',
            'function': self.previous_post,
            'args': []
        }
        self.like_func = {
            'type': 'function',
            'function': self.like_post,
            'args': []
        }
        self.view_image_func = {
            'type': 'function',
            'function': self.view_image,
            'args': []
        }
        self.back_func = {
            'type': 'function',
            'function': self.regress_state,
            'args': []
        }

    def update_menu(self):
        """Updates the menu"""
        # Update whether we have liked the post
        self.have_liked = self.post_is_liked()

        # Iterate through conditions for menu items and add them if necessary
        # In this order: Previous Post, Next Post, Like, View Replies, Reply, Bootlick (if not bootlicking), Delete (if our post), Back
        # We need to update menu pointer maybe so save the list of items
        menu_items = self.menu.get_items()

        # Check what item our menu pointer is on
        pointer_pos = self.menu.selection

        # Clear out menu
        self.menu.clear_menu()

        # Now we can add the items back in
        # If we are not on index 0 of the feed then prepend with "Previous post"
        if self.feed.post_index != 0:
            self.menu.update_menu("Previous Post", self.prev_post_func, self.menu.get_num_items())

        # If we are not on the last post of the feed then append with "Next post"
        if self.feed.post_index != len(self.feed.posts) - 1:
            self.menu.update_menu("Next Post", self.next_post_func, self.menu.get_num_items())

        # If we have not liked the post then append with "Like"
        if not self.have_liked:
            self.menu.update_menu("Like", self.like_func, self.menu.get_num_items())

        if self.current_post['attached_image'] != "":
            self.menu.update_menu("View Attached Image", self.view_image_func, self.menu.get_num_items())

        # Now finally add the back option
        self.menu.update_menu("Back", self.back_func, self.menu.get_num_items())

        # If there are no items our pointer is set to 0
        if len(menu_items) == 0:
            self.menu.selection = 0
            return None

        # What item are we on?
        item_on = menu_items[pointer_pos]
        # Get new items
        new_items = self.menu.get_items()
        # Do we still have that item?
        if item_on in new_items:
            # If so, set the menu pointer to that item
            self.menu.selection = new_items.index(item_on)
        # Otherwise we have to do some logic to figure out where to put the menu pointer
        else:
            if pointer_pos == len(menu_items) - 1:
                self.menu.selection = self.menu.get_num_items() - 1
            else:
                # In this case we're on next/previous/like because they're the only ones that can be removed
                # In which case it is easiest to move the pointer back one
                # If we go below 0 set to 0
                self.menu.selection = max(0, pointer_pos - 1)

        return None

    # Navigation functions
    def next_post(self):
        """Go to the next post"""
        self.feed.post_index += 1
        self.current_post = self.feed.get_post(self.feed.post_index)

        self.update_menu()

        # Clear attached image
        self.attached_image = ""

        return None

    def previous_post(self):
        """Go to the previous post"""
        self.feed.post_index -= 1
        self.current_post = self.feed.get_post(self.feed.post_index)

        # Check if post index is 0 and remove the previous post option if so
        if self.feed.post_index == 0:
            self.menu.update_menu("Previous Post", self.prev_post_func, None)

        self.update_menu()

        # Clear attached image
        self.attached_image = ""

        return None

    def post_is_liked(self):
        """Check if the post is liked"""
        # Check if we have liked the post
        if self.username.lower() in [liker.lower() for liker in self.current_post['liked_by']]:
            return True
        else:
            return False

    def like_post(self):
        """Likes the post"""
        response = david_api.query_api("like-post", [self.current_post['id']], self.session.cookies)
        if response is None:
            return None

        # Update feed object
        self.feed.posts[self.feed.post_index]['liked_by'].append(self.username)

        self.update_menu()
        return None

    def view_image(self):
        """View the attached image"""
        # Request the image
        r = requests.get(self.current_post['attached_image'])
        if r.status_code != 200:
            return None

        # Open and show image
        img = Image.open(BytesIO(r.content))
        img.show()

    def draw_post(self):
        """Draw the current post"""
        linebreak = "-" * (curses.COLS - 1) + "\n"

        # If this is a David Selection say so
        if self.current_post['david_selection']:
            self.stdscr.addstr("*:･ﾟ✧*:･ﾟ✧ David Selection\n", self.colours.YELLOW_BLACK | curses.A_BLINK)
            self.stdscr.addstr(linebreak)

        # Username and timestamp
        timestamp = self.current_post['timestamp']
        timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        date_time = timestamp.strftime("%d/%m/%Y %H:%M:%S")
        self.stdscr.addstr(f"@{self.current_post['username']} ", self.colours.YELLOW_BLACK)
        self.stdscr.addstr("posted at ")
        self.stdscr.addstr(f"{date_time}\n", self.colours.GREEN_BLACK)
        self.stdscr.addstr(linebreak)

        # Post content
        # Skip if blank
        body = self.current_post['content']
        if body != "":
            self.stdscr.addstr(f"{self.current_post['content']}\n")
            self.stdscr.addstr(linebreak)

        # Likes and comments
        likes = self.current_post['liked_by'].copy()
        # We put our name at the beginning in yellow to signify we have liked it
        if len(likes) > 0 and self.have_liked:
            # Find our position in the list of likers and remove it
            lowered_likes = [liker.lower() for liker in likes]
            del likes[lowered_likes.index(self.username.lower())]

            likers = ", ".join(likes)
            self.stdscr.addstr("Liked by: ", self.colours.GREEN_BLACK)
            # We want to put our name at the beginning and highlight it in yellow
            self.stdscr.addstr(self.username, self.colours.YELLOW_BLACK)
            if len(likes) > 0:
                self.stdscr.addstr(", ")
            self.stdscr.addstr(likers + "\n")
        elif len(likes) > 0 and not self.have_liked:
            likers = ", ".join(likes)
            self.stdscr.addstr("Liked by: ", self.colours.GREEN_BLACK)
            self.stdscr.addstr(likers + "\n")
        else:
            likers = "Nobody, you should be the first! :3"
            self.stdscr.addstr(likers + "\n")

        # Cleanup
        del likes

        self.stdscr.addstr(linebreak)

        # TODO: Tell the user who has replied to the post
        if self.current_post['ncomments'] > 0:
            commenters = f"{self.current_post['ncomments']} replies"
        else:
            commenters = "Nobody has replied to this post, you should be the first! :3"
        self.stdscr.addstr(commenters + "\n")

        if self.current_post['attached_image'] != "":
            self.stdscr.addstr(linebreak)
            rows = self.menu.get_rows()

            if self.attached_image == "":
                self.attached_image = AsciiImage(self.stdscr, self.current_post['attached_image'], url=True, centre=True, dim_adjust=(0, rows + 1))
            else:
                # Set the dim adjust to the current menu rows + 1
                self.attached_image.set_dim_adjust((0, rows + 1))
                # Update incase it needs resizing
                self.attached_image.update()
                # Then draw it
                self.attached_image.draw()

    def draw(self):
        """Draw the state"""
        # Draw the post
        self.draw_post()
        # Call the parent draw function
        super().draw()

    def cleanup(self):
        """Cleanup the state"""
        # We keep the feed but reset it's index to 0
        # This MIGHT be annoying and I might remove it
        self.feed.post_index = 0
        # Call the parent cleanup function
        super().cleanup()
