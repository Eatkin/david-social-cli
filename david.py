"""TODO: clean up menu_utils and constants because they are not used
Add error handling for when the API request fails
"""

import os
import scripts.toml_utils as tu
import scripts.chromium_utils as cu
import scripts.api_routes as david_api
import scripts.string_utils as su
import scripts.argparse_utils as au
from rich.markdown import Markdown
from scripts.console import console
from scripts.feed_utils import print_feed

def print_david_logo():
    # Print out this very cool David Social logo
    david_logo = os.path.join(os.path.dirname(__file__), "assets/david.png")
    david_ascii = su.image_to_ascii(david_logo, url=False)
    console.print(david_ascii, end="\n\r")

def get_args():
    # Initialize argparse
    parser = au.argparse_init()
    args = au.parse_args(parser)
    # Validate the arguments
    if not au.validate_arguments(args):
        print("Failed to validate arguments")
        parser.print_help()
        exit(1)
    return args

def validate_api_routes():
    # Check the API routes
    console.print("Checking API routes...", end="\n\r")
    missing_routes = david_api.validate_routes()

    return missing_routes

def get_username():
    # Get our username
    username, _ = tu.get_secrets()
    del _

    return username

def print_homepage():
    # Get the homepage
    homepage_soup = cu.get_david_homepage()
    homepage_content = cu.parse_soup(homepage_soup)

    # Homepage is in markdown format so parse it with rich
    homepage_markdown = Markdown(homepage_content)
    console.print(homepage_markdown)
    console.print("-" * 80, end="\n\r")

def login():
    # Login
    console.print("Logging in...", end="\n\r")
    success = cu.login()
    if not success:
        exit(1)

def print_ticker():
    ticker = cu.get_david_ticker()
    console.print("Ticker: " + ticker, end="\n\r")
    console.print("-" * 80, end="\n\r")

def print_catpets():
    catpets = david_api.get_api_response("get_cat_pets")
    console.print(f"The cat has been pet {catpets['pets']} times", end="\n\r")
    console.print(" (^・ω・^ ) ", end="\n\r")
    console.print("-" * 80, end="\n\r")

def print_bootlicker_feed():
    bootlicker_feed = david_api.get_api_response("bootlicker_feed", [username])
    # Print the feed
    print_feed(bootlicker_feed[:args.feed])

def print_global_feed():
    global_feed = david_api.get_api_response("global_feed")
    print_feed(global_feed[:args.global_feed])

def update_ticker():
    if args.update_ticker == "":
        console.print("Error: ticker cannot be empty", end="\n\r")
    else:
        cu.update_david_ticker(args.update_ticker)
        console.print("-" * 80, end="\n\r")

def make_post():
    if args.post == "":
        console.print("Error: post cannot be empty", end="\n\r")
    else:
        cu.post_to_david_social(args.post)
        console.print("-" * 80, end="\n\r")

def print_replies():
    # For this we call the post_data route to get the initial post
    # Then the replies route to get the replies
    post_data = david_api.get_api_response("post_data", [args.get_replies])
    replies = david_api.get_api_response("replies", [args.get_replies])
    # Join the post data and replies
    post_data = [post_data]
    post_data.extend(replies)
    # Now use the print_feed function to print the replies
    print_feed(post_data)

def print_avatar():
    # Use the get_avatar route to get the avatar
    console.print(f"{args.get_avatar}'s avatar for your viewing pleasure:", end="\n\r")
    avatar_url = david_api.get_api_response("avi_url", [args.get_avatar])
    # Convert to ascii
    avi_ascii = su.image_to_ascii(avatar_url, url=True)
    console.print(avi_ascii, end="\n\r")
    console.print("-" * 80, end="\n\r")


# Main execution
if __name__ == "__main__":
    print_david_logo()
    args = get_args()
    missing_routes = validate_api_routes()
    console.print("Loading David Social...", end="\n\r")
    username = get_username()
    print_homepage()
    login()
    console.print("Welcome to David Social!", end="\n\r")
    # Run through the arguments
    if args.ticker:
        print_ticker()
    if args.catpets:
        print_catpets()
    if args.feed:
        print_bootlicker_feed()
    if args.global_feed:
        print_global_feed()
    if args.update_ticker:
        update_ticker()
    if args.post:
        make_post()
    if args.get_replies:
        print_replies()
    if args.get_avatar:
        print_avatar()
