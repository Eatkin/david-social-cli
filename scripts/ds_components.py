import curses
from datetime import datetime
from math import floor
from bs4 import BeautifulSoup
from scripts.colours import ColourConstants
import scripts.api_routes as david_api
import scripts.string_utils as su


class Menu():
    def __init__(self, stdscr, items, states):
        # Initialise colours
        self.colours = ColourConstants()
        self.colours.init_colours()
        # Other stuff
        self.stdscr = stdscr
        self.items = items
        self.states = states
        self.cols = 0
        self.rows = 0
        self.selection = 0
        # Used for spacing
        if len(self.items) > 0:
            self.longest_item = len(max(self.items, key=len))
        else:
            self.longest_item = 0

    def clear_row(self, row):
        """Blank out the specified row"""
        _, width = curses.initscr().getmaxyx()
        self.stdscr.addstr(row, 0, " " * (width - 1), self.cols)

    def get_key(self, key, key_check):
        """Check if a key is pressed"""
        return 1 if key == key_check else 0

    def update(self):
        """Navigation with curses"""
        self.stdscr.nodelay(True)
        key = self.stdscr.getch()

        # Jank ass way of getting input lmao
        hinput = self.get_key(key, curses.KEY_RIGHT) - self.get_key(key, curses.KEY_LEFT)
        vinput = self.get_key(key, curses.KEY_DOWN) - self.get_key(key, curses.KEY_UP)
        # Hinput simply increments or decrements
        if hinput != 0:
            self.selection += hinput
            if self.selection < 0:
                self.selection = len(self.items) - 1
            if self.selection >= len(self.items):
                self.selection = 0

        # Vinput is more annoying to handle
        if vinput != 0 and self.rows > 0:
            self.selection += self.cols * vinput
            if self.selection < 0:
                self.selection = self.cols * self.rows + self.selection
            if self.selection >= len(self.items):
                self.selection = len(self.items) - 1

        if key == curses.KEY_ENTER or key == 10 or key == 13:
            return self.states[self.selection]

        return None

    def update_menu(self, item, function, pos):
        """Update the menu items"""
        # If pos is none then we remove it
        if pos is None:
            # Get the index of the item
            index = self.items.index(item)
            # If the item is selected then we need to change the selection
            if index == self.selection:
                # If the item is the last item then we need to decrement the selection
                if index == len(self.items) - 1:
                    self.selection -= 1

            # Remove the item and state
            del self.items[index]
            del self.states[index]
        else:
            self.items.insert(pos, item)
            self.states.insert(pos, function)
            # Update selection
            if pos <= self.selection:
                self.selection += 1

        # Update longest item
        self.longest_item = len(max(self.items, key=len))

    def clear_menu(self):
        """Remove all menu items"""
        self.items = []
        self.functions = []

    def has_item(self, item):
        """Check if the menu has an item"""
        return item in self.items

    def get_num_items(self):
        """Return the number of items in the menu"""
        return len(self.items)

    def get_items(self):
        """Return the menu items as a copy"""
        return self.items.copy()

    def draw(self):
        """Draw the menu"""
        # Reset rows and columns
        self.rows = 0
        self.cols = 0
        # Get the height and width of the terminal
        height, width = curses.initscr().getmaxyx()

        # Define the coordinates of the menu items
        coords = []
        current_width = 0
        count_cols = True
        for item in self.items:
            if current_width + self.longest_item + 1 > width:
                current_width = 0
                self.rows += 1
                centre = round((self.longest_item - len(item))/2)
                coords.append((current_width + centre, self.rows))
                count_cols = False
            else:
                # Counts how many columns there are
                if count_cols:
                    self.cols += 1
                # Append this before adjusting the width
                centre = round((self.longest_item - len(item))/2)
                coords.append((current_width + centre, self.rows))

            # Consistent spacing
            current_width += self.longest_item + 1

        # Set initial drawing coordinates
        x = 0
        y = height - self.rows - 1

        # Blank rows
        for row in range(y, height):
            self.clear_row(row)

        # Print menu items
        for item in self.items:
            x_offset, y_offset = coords.pop(0)
            col = self.colours.HIGHLIGHT if self.selection == self.items.index(item) else self.colours.WHITE_BLACK
            self.stdscr.addstr(y + y_offset, x + x_offset, item, col)

    def get_rows(self):
        """Return the height of the menu"""
        return self.rows

class Ticker():
    """Ticker class"""
    def __init__(self, stdscr):
        # Initialise the colour constants
        self.colours = ColourConstants()
        self.colours.init_colours()
        _, width = curses.initscr().getmaxyx()
        self.stdscr = stdscr
        # Get the ticker, we default to None
        self.text = None
        self.text = ""
        self.get_ticker()
        self.ticker_x = 0
        self.ticker_spacing = max(round(width * 0.2), 2)
        self.t = datetime.now()
        self.ticker = self.text
        self.ticker_update_rate = 0.2

    def get_ticker(self):
        """Get new ticker text from the API"""
        r = david_api.query_api("get-ticker-text")
        if r is not None:
            # Parse the ticker text - it's in html
            soup = BeautifulSoup(r['tickerText'], "html.parser")
            # Extract the text from the soup
            self.text = soup.text.strip()
        elif self.text is not None:
            return
        else:
            self.text = "Ticker text not found :("


    def update(self):
        """Updates the ticker text"""
        _, width = curses.initscr().getmaxyx()
        # Update spacing basedd on Terminal width
        self.ticker_spacing = max(round(width * 0.2), 2)

        # Update the ticker text position
        dt = datetime.now() - self.t
        if dt.total_seconds() > self.ticker_update_rate:
            self.t = datetime.now()
            self.ticker_x += 1

        # Wrap ticker_x
        if self.ticker_x >= len(self.text) + self.ticker_spacing:
            self.ticker_x = 0

        # Update the actual text to display
        self.ticker = list(self.text) + list(" " * self.ticker_spacing) + list(self.text)
        # Add enough repeats of the ticker text to fill the screen
        while len(self.ticker) < width * 2:
            self.ticker = self.ticker + list(" " * self.ticker_spacing) + self.ticker

        # Slice the ticker text to fit the screen
        self.ticker = self.ticker[self.ticker_x:self.ticker_x + width - 1]

        # Join the ticker back into a string
        self.ticker = "".join(self.ticker)

    def draw(self):
        """Prints the ticker text with scrolling"""
        # Print the ticker with a colour pair
        self.stdscr.addstr(self.ticker, curses.A_ITALIC | self.colours.YELLOW_BLACK)

class AsciiImage():
    """Ascii image class"""
    def __init__(self, stdscr, image_path, url, centre=True, dim_adjust=(0, 0)):
        """Initialise the ascii image"""
        self.stdscr = stdscr
        self.image_url = image_path
        self.url = url
        self.ascii = None
        self.centre = centre
        self.dim_adjust = dim_adjust

        # Dimemsion adjustment
        self.max_width = 0
        self.max_height = 0

        # Initial image generation
        self.generate_image()


    def generate_image(self):
        """Generate the ascii image"""
        # Set the max width and height
        self.max_height, self.max_width = curses.initscr().getmaxyx()

        # Delete ascii if it exists
        if self.ascii:
            del self.ascii

        self.ascii = su.image_to_ascii(self.image_url, self.url, dim_adjust=self.dim_adjust)
        # Centre the ascii image if required
        if self.centre:
            # Get the width of the ascii image
            ascii_width = len(self.ascii.split("\n")[0])
            # Get the width of the terminal
            _, max_width = curses.initscr().getmaxyx()
            # Centre the ascii image
            centre = floor((max_width - ascii_width)/2)
            self.ascii = "\n".join([" "*centre + line for line in self.ascii.split("\n")])

    def get_dims(self):
        return len(self.ascii.split("\n")) - self.dim_adjust[1], len(self.ascii.split("\n")[0]) - self.dim_adjust[0]

    def set_dim_adjust(self, dim_adjust):
        """Set the dimension adjustment"""
        self.dim_adjust = dim_adjust

    def update(self):
        """Check if the image requires updating due to terminal resize"""
        # Get terminal size
        t_height, t_width = curses.initscr().getmaxyx()
        # Check if the terminal size has changed
        if t_height != self.max_height or t_width != self.max_width:
            self.generate_image()
            # Update
            self.max_height = t_height
            self.max_width = t_width

    def draw(self):
        """Draw the ascii image"""
        self.stdscr.addstr(self.ascii)

"""Notes on the feed class:
response json structure is a list of dictionaries with keys:
- id
- username
- content
- likes
- avi
- attached_image
- userid (None)
- timestamp
- reply_to
- liked_by
- ncomments
- david_selection
"""
class Feed():
    def __init__(self, session, type="Bootlicker", additional_params=None):
        """Create feed, type can be Bootlicker or Global"""
        # TODO: Handling of user feeds and reply threads
        # Fetch posts based on type
        self.type = type
        self.session = session
        if self.type == "Bootlicker":
            self.api_route = "bootlicker-feed"
            self.params = [50]
        elif self.type == "Global":
            self.api_route = "global-feed"
            self.params = [1]
        elif self.type == "User":
            self.api_route = "user-posts"
            self.params = [additional_params]
        elif self.type == "Reply":
            self.api_route = "replies"
            self.params = [additional_params]
        elif self.type == "Notifications":
            self.api_route = "my-notifications"
            self.params = []

        # Query the api
        # The window is a parameter which we can hold on to if we wish to load more posts
        self.posts = david_api.query_api(self.api_route, params=self.params, cookies=self.session.cookies)

        # Now we've got our feed let's see if there's anything in it
        # (Also handles failure to retrieve posts)
        if len(self.posts) == 0 or self.posts is None:
            # Create a post saying there are no posts
            post = {
                "id": "0",
                "username": "David",
                "content": "There are no posts to display also David didn't actually post this",
                "likes": 0,
                "avi": "",
                "attached_image": "",
                "userid": None,
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "reply_to": None,
                "liked_by": [],
                "ncomments": 0,
                "david_selection": False
            }
            self.posts = [post]

        self.post_index = 0

    def get_post(self, index):
        """Get a post from the feed"""
        return self.posts[index]

    def update_post(self, index):
        """Update a post in the feed"""
        # Query the api
        post = david_api.query_api("get-post", params=[self.get_post_id(index)], cookies=self.session.cookies)
        # Replace the post in the feed
        self.posts[index] = post

        return post

    def delete_post(self, index):
        """Remove a post from the feed"""
        # Remove the post from the feed
        del self.posts[index]
        # Post index remains the same, but we need to reduce window by 1 if we're on bootlicker feed
        if self.type == "Bootlicker":
            self.params[0] -= 1

    def get_post_id(self, index):
        """Get the post id from the feed"""
        return self.posts[index]["id"]

    def get_replies(self, index):
        """Get the replies to a post"""
        # Use the replies route
        id = self.get_post_id(index)
        return david_api.query_api("replies", params=[id], cookies=self.session.cookies)

    def has_image(self, index):
        """Check if a post has an image"""
        return self.posts[index]["attached_image"] != ""

    def get_image(self, index):
        """Get the image from a post"""
        return self.posts[index]["attached_image"]

    def update(self):
        """Update the feed"""
        # Query the api
        new_posts = david_api.query_api(self.api_route, params=self.params, cookies=self.session.cookies)
        # We need to loop through the new posts until we hit a post that is already in the feed
        for post in new_posts:
            if post not in self.posts:
                # Add the post to the feed if it isn't a David selection
                if not post["david_selection"]:
                    self.posts = [post] + self.posts
                    # Also increment the post index - if we preserve the post index then we can keep the user in the same place
                    self.post_index += 1

    def load_more_posts(self):
        """Load more posts
        Returns: True if more posts were loaded, False if there are no more posts"""
        # This will cause problems if more than 50 posts have been posted to Bootlicker feed since the user last loaded it
        # I'm going to use the ostrich method and ignore this problem
        if self.type == "Bootlicker":
            self.params[0] += 50
        elif self.type == "Global":
            self.params[0] += 1
        elif self.type == "User" or self.type == "Reply" or self.type == "Notifications":
            return False

        # Query the api with the new window size
        new_posts = david_api.query_api(self.api_route, params=self.params, cookies=self.session.cookies)

        # We now have the annoying problem of David 'Intelligence' being inserted into the posts list
        # So basically we need to find the last post in self.posts in the new posts list
        # This loop ensures we don't pick a David Selection as the last post
        i = -1
        while self.posts[i]["david_selection"]:
            i -= 1
            # Failsafe to prevent infinite loop
            if -i > len(self.posts):
                return False

        last_post = self.posts[-i]
        # This actually crashes so lazy try except to make sure it doesn't break
        try:
            # Find the index of the last post
            last_post_index = new_posts.index(last_post)
            # There is an exception if (somehow) we reach the end of the feed
            if last_post_index == len(new_posts) - 1:
                # In this case we don't need to do anything
                return False
        except:
            return False
        # Now slice the new posts list to get the new posts
        new_posts = new_posts[last_post_index + 1:]
        # Now we can append the new posts to the old posts
        self.posts += new_posts
        return True
