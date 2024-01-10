import curses
import os
from enum import Enum
from datetime import datetime
from scripts.ds_components import Menu, Ticker, AsciiImage, Feed
import scripts.api_routes as david_api
from scripts.colours import ColourConstants

# We need to create a feeds dictionary to store the feed objects so we can save our place in them
feeds = {}

# Create special keywords for bootlicker and global feeds for use in the feeds dictionary
# This is to ensure they are differentiated from user feeds
# But for example if there was a user called 'bootlicker' that would cause issues
class FeedType(Enum):
    BOOTLICKER = 0
    GLOBAL = 1

class State():
    def update(self):
        """Update the state"""
        # Update the menu
        update = self.menu.update()
        # If the menu returns a state, return it
        if update is None or isinstance(update, State):
            return update
        # Otherwise the menu has returned a function so call it
        update()
        return None

    def draw(self):
        """Draw the state"""
        # Draw the menu
        self.menu.draw()

    def cleanup(self):
        """Clean up the state"""
        # Delete menu
        del self.menu

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
        menu_states = [StateFeed(self.stdscr, self.session, self.logger, "Bootlicker"),
                       StateFeed(self.stdscr, self.session, self.logger, "Global"),
                       StateExit(self.stdscr, self.session, self.logger),
                       StateExit(self.stdscr, self.session, self.logger),
                       StateExit(self.stdscr, self.session, self.logger),
                       StateExit(self.stdscr, self.session, self.logger)]
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
    def __init__(self, stdscr, session, logger, feed_type, user_feed=None):
        """Initialise the state"""
        self.stdscr = stdscr
        self.session = session
        self.logger = logger

        self.logger.info('initialising StateFeed')
        # This is the name of the user feed we are viewing
        self.user_feed = user_feed

        # Set up the feed
        self.feed_type = feed_type
        self.feed_key = FeedType.BOOTLICKER if feed_type == "Bootlicker" else FeedType.GLOBAL if feed_type == "Global" else self.user_feed
        if self.feed_key in feeds:
            self.feed = feeds[self.feed_key]
        else:
            self.feed = Feed(self.session, self.feed_type, user_feed)
            # Add our feed to the feeds dictionary
            feeds[self.feed_key] = self.feed

        # Create menu
        menu_items = ["Next Post", ]
        menu_functions = [self.next_post]

        # If we are not on index 0 of the feed then prepend with "Previous post"
        if self.feed.post_index != 0:
            menu_items.insert(0, "Previous Post")
            menu_functions.insert(0, self.previous_post())

        self.menu = Menu(self.stdscr, menu_items, menu_functions)

        self.current_post = self.feed.get_post(self.feed.post_index)

        # Initialise colours
        self.colours = ColourConstants()
        self.colours.init_colours()

    # Navigation functions
    def next_post(self):
        """Go to the next post"""
        self.feed.post_index += 1
        self.current_post = self.feed.get_post(self.feed.post_index)

        # Check if we have reached the end of the feed or if post index is 1
        if self.feed.post_index == 1:
            # Prepend "Previous Post" to the menu
            self.menu.update_menu("Previous Post", self.previous_post, 0)

        # If we have reached the end of the feed try and get more posts
        if self.feed.post_index == len(self.feed.posts) - 1:
            # Get more posts
            more_posts_loaded = self.feed.load_more_posts()
            if not more_posts_loaded:
                # If there are no more posts remove "Next Post" from the menu
                self.menu.update_menu("Next Post", self.next_post, None)
        pass

    def previous_post(self):
        """Go to the previous post"""
        # TODO: Check if we are at the start of the feed for menu updating
        # TODO: Check if there is an attached image for menu updating
        pass

    def update(self):
        """Update the state"""
        # Call the parent update function
        return super().update()

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
        self.stdscr.addstr(f"@{self.current_post['username']} posted at {date_time}\n")
        self.stdscr.addstr(linebreak)

        # Post content
        self.stdscr.addstr(f"{self.current_post['content']}\n")
        self.stdscr.addstr(linebreak)

        # Likes and comments
        if len(self.current_post['liked_by']) > 0:
            likers = ", ".join(self.current_post['liked_by'])
        else:
            likers = "Nobody, you should be the first! :3"
        self.stdscr.addstr(f"Liked by: {likers}\n")

        # TODO: Tell the user who has replied to the post
        if self.current_post['ncomments'] > 0:
            commenters = self.current_post['ncomments']
        else:
            commenters = "Nobody has replied to this post, you should be the first! :3"
        if self.current_post['ncomments'] > 0:
            self.stdscr.addstr(f"{commenters} replies\n")

        if self.current_post['attached_image'] != "":
            self.stdscr.addstr("Image attached, you should look at it! :3\n")
            self.stdscr.addstr(linebreak)

    def draw(self):
        """Draw the state"""
        # Draw the post
        self.draw_post()
        # Call the parent draw function
        super().draw()

    def cleanup(self):
        return super().cleanup()
