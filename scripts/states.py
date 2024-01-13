import curses
import os
import requests
import csv
from random import choice
from math import floor
from io import BytesIO
from PIL import Image
from enum import Enum
from datetime import datetime
from scripts.ds_components import Menu, Ticker, AsciiImage, Feed
import scripts.api_routes as david_api
from scripts.colours import ColourConstants
import scripts.env_utils as eu

# TODO: Add a confirmation for the text entry class, or error message if it fails, or prompt if message is blank
# TODO: Check notifications
# TODO: View profile
# TODO: Bootlick user if we aren't already bootlicking them
# TODO: Delete post if it is our post (probably rly annoying to do)
# TODO: Search users?
# TODO: Some of the kaomoji doesn't display properly, try triple quotes maybe

# OPTIONAL TODO: Create an object for menu functions instead of using dictionaries

# We need to create a feeds dictionary to store the feed objects so we can save our place in them
feeds = {}

# Create special keywords for bootlicker and global feeds for use in the feeds dictionary
# This is to ensure they are differentiated from user feeds
# But for example if there was a user called 'bootlicker' that would cause issues
class FeedType(Enum):
    BOOTLICKER = 0
    GLOBAL = 1

# Constants for text entry
class TextEntryType(Enum):
    NEW_POST = 0
    REPLY = 1
    TICKER_UPDATE = 2

# State history for regressing to a previous state
state_history = []

class State():
    def __init__(self):
        self.callback = None

    def update(self):
        """Update the state"""
        # Perform one time functions if necessary
        if self.callback is not None:
            self.callback()
            self.callback = None

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

    def advance_state(self, state, callback=None):
        """Advance the state"""
        # Add the current state to the history
        state_history.append(self)

        # Set the callback
        if callback is not None:
            state.callback = callback

        # state is an object so we can just return it
        return state

    def regress_state(self, callback=None):
        """Regress the state"""
        # Cleanup
        self.cleanup()
        # Now revert to the previous state
        previous_state = state_history.pop()
        # Set the callback
        if callback is not None:
            previous_state.callback = callback
        return previous_state

class StateMain(State):
    def __init__(self, stdscr, session, logger, callback=None):
        """Initialise the state"""
        super().__init__()
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
        menu_items = ["Bootlicker Feed", "Global Feed", "Pet the Cat", "New Post", "Update Ticker", "Exit", ]
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
                {
                    'type': 'state_change',
                    'function': self.advance_state,
                    'state': StatePetCat,
                    'args': (self.stdscr, self.session, self.logger)
                },
                {
                    'type': 'state_change',
                    'function': self.advance_state,
                    'state': StateTextEntry,
                    'args': (self.stdscr, self.session, self.logger, TextEntryType.NEW_POST, 0)
                },
                {
                    'type': 'state_change',
                    'function': self.advance_state,
                    'state': StateTextEntry,
                    'args': (self.stdscr, self.session, self.logger, TextEntryType.TICKER_UPDATE, None)
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

    def update_ticker(self):
        """Update the ticker"""
        # Update the ticker
        self.ticker.get_ticker()


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
        super().__init__()

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
    def __init__(self, stdscr, session, logger, feed_type, additional_params=None, parent=None, callback=None):
        """Initialise the state"""
        super().__init__()

        self.stdscr = stdscr
        self.session = session
        self.logger = logger

        self.callback = callback

        # Used for either post ID or username
        self.additional_params = additional_params

        # Parent is used for replying to a post
        self.parent = parent

        self.parent_content = None

        # Make a request to the api to get the parent post from ID
        if self.parent is not None:
            response = david_api.query_api("get-post", [self.parent], self.session.cookies)
            self.parent_content = f"@{response['username']}: {response['content']}"

        # Set up the feed
        self.feed_type = feed_type
        self.feed_key = FeedType.BOOTLICKER if self.feed_type == "Bootlicker" else FeedType.GLOBAL if self.feed_type == "Global" else self.parent

        # This will cache the feed object so we don't have to keep making requests unnecessarily
        if self.feed_key in feeds:
            self.logger.info(f"Feed {self.feed_key} already exists, using cached feed")
            self.feed = feeds[self.feed_key]
        else:
            self.feed = Feed(self.session, self.feed_type, self.additional_params)
            # Add our feed to the feeds dictionary
            feeds[self.feed_key] = self.feed

        self.menu = Menu(self.stdscr, [], [])

        self.current_post = self.feed.get_post(self.feed.post_index)

        # Setup menu functions
        self.setup_menu_functions()

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
        self.view_replies_func = {
            'type': 'state_change',
            'function': self.advance_state,
            'state': StateFeed,
            'args': (self.stdscr, self.session, self.logger, "Reply", self.current_post['id'], self.current_post['id'])
        }
        self.reply_to_post_func = {
            'type': 'state_change',
            'function': self.advance_state,
            'state': StateTextEntry,
            'args': (self.stdscr, self.session, self.logger, TextEntryType.REPLY, self.current_post['id'], f"@{self.current_post['username']} {self.current_post['content']}")
        }

    def update_menu_functions(self):
        """Update any menu functions that need updating"""
        # Update the reply function to reply to the parent post, not the reply
        # Define the parent-  we inherit it to prevent replying to replies
        parent = self.current_post['id'] if self.parent is None else self.parent
        self.reply_to_post_func['args'] = (self.stdscr, self.session, self.logger, TextEntryType.REPLY, parent, f"@{self.current_post['username']} {self.current_post['content']}")

        # Update the view replies function to view the replies to the current post
        self.view_replies_func['args'] = (self.stdscr, self.session, self.logger, "Reply", self.current_post['id'], self.current_post['id'])

        # If we're in a reply thread we add a callback to update the post to the back function
        # Check the class name because it keeps trying to add a callback to StateMain which doesn't have an update_post function so it crashes
        # This is easier than actually trying to trace this stupid bug
        if self.feed_type == "Reply" and state_history[-1].__class__.__name__ == "StateFeed":
            par_state = state_history[-1]
            self.back_func['args'] = [par_state.update_post]
        else:
            self.back_func['args'] = []

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

        # Update menu functions
        self.update_menu_functions()

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

        # If there are replies then append with "View Replies"
        # But only if we are NOT on a reply thread
        if self.current_post['ncomments'] > 0 and self.parent is None:
            self.menu.update_menu("View Replies", self.view_replies_func, self.menu.get_num_items())

        if self.current_post['attached_image'] != "":
            self.menu.update_menu("View Attached Image", self.view_image_func, self.menu.get_num_items())

        # Add a reply option indiscriminately
        self.menu.update_menu("Reply", self.reply_to_post_func, self.menu.get_num_items())

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

    def update_post(self):
        """Updates the current post"""
        self.logger.info(f"Updating post {self.current_post['id']}")
        self.current_post = self.feed.update_post(self.feed.post_index)
        # Update the menu too
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
        curses.update_lines_cols()
        linebreak = "-" * (curses.COLS - 1) + "\n"

        # If this is a David Selection say so
        if self.current_post['david_selection']:
            self.stdscr.addstr("*:･ﾟ✧*:･ﾟ✧ David Selection\n", self.colours.YELLOW_BLACK | curses.A_BLINK)
            self.stdscr.addstr(linebreak)

        # If we're in a reply thread display the parent post
        if self.parent_content is not None:
            self.stdscr.addstr("Replying to: \n", self.colours.GREEN_BLACK)
            self.stdscr.addstr(f"{self.parent_content.split(' ')[0]} ", self.colours.YELLOW_BLACK)
            self.stdscr.addstr(f"{' '.join(self.parent_content.split(' ')[1:])}\n")
            self.stdscr.addstr(linebreak)

        # Username and timestamp
        timestamp = self.current_post['timestamp']
        timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        date_time = timestamp.strftime("%d/%m/%Y %H:%M:%S")
        self.stdscr.addstr(f"@{self.current_post['username']} ", self.colours.YELLOW_BLACK)
        self.stdscr.addstr("posted at ")
        self.stdscr.addstr(f"{date_time}\n", self.colours.GREEN_BLACK)
        # Removing this line break cause it looks weird
        # self.stdscr.addstr(linebreak)
        self.stdscr.addstr("\n")

        # Post content
        # Skip if blank
        body = self.current_post['content']
        if body.strip() != "":
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

        # Commenters
        if self.current_post['ncomments'] > 0:
            # We don't get who has left a comment from the feed so we have to query the api
            # (might be slow)
            if 'commenters' not in self.current_post:
                response = david_api.query_api("replies", [self.current_post['id']], self.session.cookies)
                # Cache the replies in the feed cache
                # Create a feed object first
                if self.current_post['id'] not in feeds:
                    feeds[self.current_post['id']] = Feed(self.session, "Reply", self.current_post['id'])

                if response is None:
                    self.current_post['commenters'] = None
                else:
                    self.current_post['commenters'] = [reply['username'] for reply in response]
                    # Make it a set to remove duplicates
                    self.current_post['commenters'] = list(set(self.current_post['commenters']))
            # Then we can join the list of commenters
            if self.current_post['commenters'] is None:
                self.current_post['commenters'] = f"{self.current_post['ncomments']} replies"
            else:
                try:
                    num_commenters = len(self.current_post['commenters'])
                    if num_commenters > 1:
                        commenters = ", ".join(self.current_post['commenters'][:-1])
                        commenters += " and "
                        commenters += self.current_post['commenters'][-1]
                        commenters += " have replied to this post"
                    else:
                        commenters = self.current_post['commenters'][0]
                        commenters += " has replied to this post"
                except Exception as e:
                    self.logger.exception(e)
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

class StatePetCat(State):
    def __init__(self, stdscr, session, logger):
        """Initialise the state"""
        super().__init__()

        self.stdscr = stdscr
        self.session = session
        self.logger = logger

       # Load self.cat_kaomoji_list from assets/kaomoji.csv
        self.cat_kaomoji_list = []

        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets/kaomoji.csv"), "r") as f:
            reader = csv.reader(f)
            for row in reader:
                self.cat_kaomoji_list.append(row[0])


        self.pet_cat()

        # Create a menu with a back button
        menu_items = ["Pet it again!", "Back"]
        menu_functions = [
            {
                'type': 'function',
                'function': self.pet_cat,
                'args': []
            },
            {
                'type': 'function',
                'function': self.regress_state,
                'args': []
            }
        ]
        self.menu = Menu(self.stdscr, menu_items, menu_functions)

        # Initialise colours
        self.colours = ColourConstants()
        self.colours.init_colours()

    def pet_cat(self):
        # We call the api again and get a new kaomoji
        # Pet the cat
        response = david_api.query_api("pet-cat", cookies=self.session.cookies)

        if response is None:
            self.logger.error("pet-cat returned None")

        # Get number of catpets
        self.catpets = david_api.query_api("get-cat-pets", cookies=self.session.cookies)

        # Default to a string if we get none
        if self.catpets is None:
            self.catpets = "an unknown number of"
        else:
            self.catpets = self.catpets['pets']

        # Get a random kaomoji
        self.cat_kaomoji = choice(self.cat_kaomoji_list)


    def draw(self):
        # Get available space
        rows, cols = curses.initscr().getmaxyx()
        cols -= 1
        # Centre the number of catpets
        cat_pets_text = f"The cat has been petted {self.catpets} times!"
        # Add some decoration
        cat_pets_text = f"ੈ♡‧₊˚{cat_pets_text} ೄྀ࿐ˊˎ-\n"
        cat_pets_offset = 0.5 * (cols - round(len(cat_pets_text)))
        # Make sure we don't go below 0
        cat_pets_offset = max(0, round(cat_pets_offset))
        # Print the catpets with padding
        self.stdscr.addstr(f"\n{' ' * cat_pets_offset} {cat_pets_text}", self.colours.GREEN_BLACK | curses.A_BLINK)

        # Centre the kaomoji
        centre_x = round((cols - max(len(line) for line in self.cat_kaomoji.split("\n"))) / 2)
        centre_y = round((rows - len(self.cat_kaomoji.split("\n"))) / 2)
        # Format the kaomoji by padding with spaces
        kaomoji_print = "\n".join([f"{' ' * centre_x}{line}" for line in self.cat_kaomoji.split("\n")])
        # Print the kaomoji
        self.stdscr.addstr(centre_y, 0, kaomoji_print, self.colours.YELLOW_BLACK)

        # Inherit the draw function
        super().draw()

class StateTextEntry(State):
    def __init__(self, stdscr, session, logger, type=TextEntryType.NEW_POST, params=None, post_body=None):
        self.stdscr = stdscr
        self.session = session
        self.logger = logger

        # Set up Curses for text entry
        self.stdscr.nodelay(True)
        # Also flush inputs so we don't get a backlog of key presses
        curses.flushinp()

        self.params = [params] if params is not None else [0]

        self.post_body = post_body

        # Our text entry box
        self.text_entry = ""

        self.prompt = "Blah blah blah bloo bloo bloo"
        # Choose an API endpoint based on the type
        if type == TextEntryType.NEW_POST or type == TextEntryType.REPLY:
            self.api_endpoint = "new-post"
            self.prompt = "Write stuff to your friends :3"

            # If we provide a param then we are replying to a post, if not we are posting a new post (so set it to 0)
            if type == TextEntryType.REPLY:
                self.prompt = "Reply to this post :3"
                # Also fill in @username for text entry
                self.text_entry = post_body.split(" ")[0] + " "
        elif type == TextEntryType.TICKER_UPDATE:
            self.api_endpoint = "public-set-ticker-text"
            self.prompt = "Update the ticker :3"
            # We don't need any params for this so remove them
            self.params = []

        self.type = type


        # Create a blank menu (we won't need one)
        self.menu = Menu(stdscr, [], [])

        # Initialise colours
        self.colours = ColourConstants()
        self.colours.init_colours()

        self.callback = None
        self.callback_args = []

    def blank_row(self, row):
        """Draws spaces across the row"""
        # Get avaiable space
        _, cols = curses.initscr().getmaxyx()
        # Draw spaces
        self.stdscr.addstr(row, 0, " " * cols)

    def update(self):
        # This allows us to return a value from the draw function where all the logic is
        if self.callback is not None:
            return self.callback()

    def submit(self):
        try:
            # Poke the API with the text and additional params
            response = david_api.query_api(self.api_endpoint, [self.text_entry] + self.params, cookies=self.session.cookies)
            # Could probably add some sort of confirmation here

            # If we are posting a new message and bootlicker/global feeds are in the feeds dictionary then we need to update them
            if self.type == TextEntryType.NEW_POST:
                if FeedType.BOOTLICKER in feeds:
                    feeds[FeedType.BOOTLICKER].update()
                if FeedType.GLOBAL in feeds:
                    feeds[FeedType.GLOBAL].update()

            # Regress state
            par_state = state_history[-1]
            if self.type == TextEntryType.TICKER_UPDATE:
                self.callback_args = [par_state.update_ticker]

            if self.type == TextEntryType.REPLY:
                self.callback_args = [par_state.update_post]
                # We also want to update the reply thread
                try:
                    feeds[self.params[0]].update()
                except Exception as e:
                    # This sometimes throws a key error I think
                    # It doesn't really matter cause everything seems to work properly with the try/except
                    self.logger.error(f"Error updating reply thread: {e}")
            return self.regress_state(*self.callback_args)
        except Exception as e:
            # This ensures we don't continuously try to submit the post
            self.logger.error(f"Error submitting post: {e}")
            return self.regress_state()

    # TODO: Feedback if submitted post is blank
    # TODO: Trying to blank more than one row causes flickering, just blank the row we're on because that's the only one that will chagne
    def draw(self):
        """Draw the state"""
        # Draw the prompt centred
        rows, cols = curses.initscr().getmaxyx()
        cols -= 1
        # Centre the prompt
        prompt_offset = round(0.5 * (cols - len(self.prompt)))
        # Draw it
        self.stdscr.addstr(f"\n{' ' * prompt_offset}{self.prompt}\n", self.colours.GREEN_BLACK)
        # Then say press esc to go back
        esc_message = "Press Esc to cancel"
        esc_offset = round(0.5 * (cols - len(esc_message)))
        self.stdscr.addstr(f"{' ' * esc_offset}{esc_message}\n", self.colours.RED_BLACK)

        # If we're replying, add the post we're replying to
        if self.type == TextEntryType.REPLY:
            self.stdscr.addstr("Replying to: ")
            self.stdscr.addstr(f"{self.post_body.split(' ')[0]} ", self.colours.YELLOW_BLACK)
            self.stdscr.addstr(" ")
            self.stdscr.addstr(" ".join(self.post_body.split(' ')[1:]) + "\n")

        # Get the y position to draw at
        y = curses.initscr().getyx()[0]

        # Enter text gathering loop
        while self.callback is None:
            # Get updated available space
            rows, cols = curses.initscr().getmaxyx()
            cols -= 1

            # Get any key presses
            key = self.stdscr.getch()

            # If we press escape then we want to cancel
            if key == 27:
                n = self.stdscr.getch()
                self.callback = self.regress_state
                break
            # If we press enter then we want to submit
            # Curses says enter is 343, but it's actually 10 apparently
            elif key == curses.KEY_ENTER or key == 10 or key == 13:
                # Check if we have any text
                if self.text_entry != "":
                    self.callback = self.submit
                    break
            elif key == curses.KEY_BACKSPACE:
                if len(self.text_entry) > 0:
                    self.text_entry = self.text_entry[:-1]
                    # Blank out the row we're on so we don't get artifacts
                    lines = floor(len(self.text_entry) / cols)
                    self.blank_row(y + lines)
            elif key != -1:
                # Make sure key is in the appropriate range
                if key >= 32 and key <= 255:
                    self.text_entry += chr(key)

            # draw the text box content
            box_centre = round(0.5 * (cols - len(self.text_entry)))
            box_centre = max(0, box_centre)
            self.stdscr.addstr(y, box_centre, f"{self.text_entry}", self.colours.YELLOW_BLACK)

        # Inherit the draw function
        # Actually don't because there is no menu to draw
        # And also it breaks things lol
        # super().draw()

    def cleanup(self):
        """Cleanup the state"""
        # Set nodelay back to false
        self.stdscr.nodelay(False)
        # Inherit the cleanup function
        super().cleanup()
