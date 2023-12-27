import datetime
import os
import scripts.toml_utils as tu
import scripts.chromium_utils as cu
import scripts.menu_utils as mu
import scripts.api_routes as david_api
import scripts.string_utils as su
import scripts.argparse_utils as au
from rich.markdown import Markdown
from scripts.constants import State
from scripts.console import console
from scripts.feed_utils import print_feed

# Print out this very cool David Social logo
david_logo = os.path.join(os.path.dirname(__file__), "assets/david.png")
david_ascii = su.image_to_ascii(david_logo, url=False)
console.print(david_ascii, end="\n\r")

# Initialize argparse
parser = au.argparse_init()
args = au.parse_args(parser)
# Validate the arguments
if not au.validate_arguments(args):
    print("Failed to validate arguments")
    parser.print_help()
    exit(1)

# Check the API routes
console.print("Checking API routes...", end="\n\r")
missing_routes = david_api.validate_routes()

console.print("Loading David Social...", end="\n\r")

# Get our username
username, _ = tu.get_secrets()
del _

# Get the homepage
homepage_soup = cu.get_david_homepage()
homepage_content = cu.parse_soup(homepage_soup)

# Homepage is in markdown format so parse it with rich
homepage_markdown = Markdown(homepage_content)

console.print(homepage_markdown)

console.print("-" * 80, end="\n\r")

# Login
console.print("Logging in...", end="\n\r")
success = cu.login()
if not success:
    exit(1)


# We've logged in so we can get the ticker (if necessary)
if args.ticker:
    ticker = cu.get_david_ticker()

    console.print("Welcome to David Social!", end="\n\r")
    console.print("Ticker: " + ticker, end="\n\r")
    console.print("-" * 80, end="\n\r")

if args.catpets:
    catpets = david_api.get_api_response("get_cat_pets")
    console.print(f"The cat has been pet {catpets['pets']} times", end="\n\r")
    console.print("-" * 80, end="\n\r")

if args.feed:
    feed = david_api.get_api_response("bootlicker_feed", [username])
    # Print the feed
    print_feed(feed[:args.feed])


if args.global_feed:
    global_feed = david_api.get_api_response("global_feed")
    print_feed(global_feed[:args.global_feed])

if args.update_ticker:
    if args.update_ticker == "":
        console.print("Error: ticker cannot be empty", end="\n\r")
    else:
        cu.update_david_ticker(args.update_ticker)
        console.print("-" * 80, end="\n\r")

if args.post:
    if args.post == "":
        console.print("Error: post cannot be empty", end="\n\r")
    else:
        cu.post_to_david_social(args.post)
        console.print("-" * 80, end="\n\r")

"""TODO:
Cleanup the code below and remove anything redundant
Also cleanup the code above lol
"""
# # Set up global variables
# ticker = None
# feed = None
# feed_index = 0

# # Set up state
# state = State.HOME

# # Main loop
# while True:
#     if state == State.HOME:
#         # Get the homepage
#         homepage_soup = cu.get_david_homepage()
#         homepage_content = cu.parse_soup(homepage_soup)

#         # Homepage is in markdown format so parse it with rich
#         homepage_markdown = Markdown(homepage_content)

#         console.print(homepage_markdown)
#         console.print("-" * 80, end="\n\r")
#     elif state == State.LOGGED_IN:
#         # We've just logged in so display the ticker and ask user for input
#         # Get the ticker (once)
#         if ticker is None:
#             ticker = cu.get_david_ticker()
#         console.print("-" * 80, end="\n\r")
#         console.print("Welcome to David Social!", end="\n\r")
#         console.print("Ticker: " + ticker, end="\n\r")
#         console.print("-" * 80, end="\n\r")

#         # We can use API routes to get the feed and things
#         if feed is None:
#             feed = david_api.get_api_response("bootlicker_feed", [username])
#     elif state == State.BOOTLICKER_FEED:
#         if feed is None:
#             console.print("Failed to get feed", end="\n\r")
#         for post in feed:
#             # Format the timestamp
#             timestamp = post['timestamp']
#             timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
#             date_time = timestamp.strftime("%d/%m/%Y %H:%M:%S")

#             # Display the post
#             console.print("-" * 80, end="\n\r")
#             console.print(f"{post['username']} at {date_time}", end="\n\r")
#             console.print(post['content'], end="\n\r")
#             console.print("-" * 80, end="\n\r")

#             # Display any likes (can use the get-likes route but this works too)
#             likes = post['liked_by']
#             likes = ", ".join(likes)
#             console.print(f"Liked by: {likes}", end="\n\r")

#             # If there is an image attached convert to ascii and display it
#             image_url = post['attached_image']
#             if image_url != "":
#                 ascii_image = su.image_to_ascii(image_url)
#                 if ascii_image is not None:
#                     console.print("-" * 80, end="\n\r")
#                     console.print("Attached image:", end="\n\r")
#                     # Use the default print because markdown doesn't work with ascii and it fucks the console print command up
#                     print(ascii_image)



#     # Display our menu options
#     menu_options = mu.menu[state]

#     # Print out menu options
#     for option in menu_options:
#         console.print(f"({option[0]}){option[1:]}", end="\n\r")

#     # Get the user's input
#     user_input = ""
#     valid_inputs = [option[0].lower() for option in menu_options]
#     while user_input not in valid_inputs:
#         user_input = console.input("Please select an option: ",)

#     # Perform the relevant action
#     menu_index = valid_inputs.index(user_input)
#     # Execute the command in menu_functions
#     function = mu.menu_functions[state][menu_index]
#     success = function()

#     # Change state if required
#     if function == mu.login_wrapper:
#         if success:
#             state = State.LOGGED_IN
#         else:
#             state = State.HOME
#     elif function == mu.update_ticker_wrapper:
#         # Set ticker to none because we've updated it
#         if success:
#             ticker = None
#     elif function == mu.view_feed:
#         if success:
#             state = State.BOOTLICKER_FEED
#             feed_index = 0
