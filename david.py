import os
from time import sleep
import scripts.toml_utils as tu
import scripts.api_routes as david_api
import scripts.string_utils as su
import scripts.argparse_utils as au
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

def login():
    username, password = tu.get_secrets()
    session = david_api.query_api("login", [username, password])
    return session

def print_ticker():
    console.print("Getting ticker does not work right now, enjoy this error message instead :)", end="\n\r")
    ticker = david_api.query_api("get-ticker-text")
    # Ticker is html so extract text from the soup
    if ticker is None:
        ticker = "No ticker text"
    console.print("Ticker: " + ticker, end="\n\r")
    console.print("-" * 80, end="\n\r")

def print_catpets():
    catpets = david_api.query_api("get-cat-pets")
    if catpets is not None:
        console.print(f"The cat has been pet {catpets['pets']} times", end="\n\r")
        console.print("(^・ω・^ )", end="\n\r")
        console.print("-" * 80, end="\n\r")

def pet_cat():
    david_api.query_api("pet-cat", cookies=cookies)
    console.print("You pet the cat", end="\n\r")
    print_catpets()
    console.print("-" * 80, end="\n\r")

def print_bootlicker_feed():
    params = [] if args.feed is None else [args.feed]
    bootlicker_feed = david_api.query_api("bootlicker-feed", params=params, cookies=cookies)
    if bootlicker_feed is not None:
        # Print the feed
        print_feed(bootlicker_feed)

def print_global_feed():
    # Default to 1 day
    params = [1] if args.global_feed is None else [args.global_feed]
    global_feed = david_api.query_api("global-feed", params=params, cookies=cookies)
    if global_feed is not None:
        print_feed(global_feed)

def update_ticker():
    if args.update_ticker == "":
        console.print("Error: ticker cannot be empty", end="\n\r")
    else:
        david_api.query_api("public-set-ticker-text", params=[args.update_ticker], cookies=cookies)
        console.print("Ticker updated!", end="\n\r")

def make_post():
    if args.post == "":
        console.print("Error: post cannot be empty", end="\n\r")
    else:
        # TODO: add a check for the length of the post
        # We can post 240 characters I think
        # So give the option of splitting post into post + replies
        try:
            david_api.query_api("new-post", params=[args.post, 0], cookies=cookies)
            console.print("Posted!", end="\n\r")
            console.print("-" * 80, end="\n\r")
        except:
            console.print("Error: failed to post", end="\n\r")

def print_replies():
    # For this we call the post_data route to get the initial post
    # Then the replies route to get the replies
    post_data = david_api.query_api("get-post", [args.get_replies], cookies=cookies)
    replies = david_api.query_api("replies", [args.get_replies], cookies=cookies)
    # Join the post data and replies
    if post_data is not None and replies is not None:
        post_data = [post_data]
        post_data.extend(replies)
        # Now use the print_feed function to print the replies
        print_feed(post_data)
    else:
        console.print("Error: failed to get replies", end="\n\r")

def print_avatar():
    # Use the get_avatar route to get the avatar
    avatar_url = david_api.query_api("avi-url", [args.get_avatar], cookies=cookies)
    if avatar_url is not None:
        # Convert to ascii
        console.print(f"{args.get_avatar}'s avatar for your viewing pleasure:", end="\n\r")
        avi_ascii = su.image_to_ascii(avatar_url, url=True)
        console.print(avi_ascii, end="\n\r")
        console.print("-" * 80, end="\n\r")

def print_user_posts():
    posts = david_api.query_api("user-posts", [args.get_user_posts], cookies=cookies)
    # Use the print feed utility
    if posts is not None:
        print_feed(posts)
    else:
        console.print("Error: failed to get user posts", end="\n\r")

def print_bootlickers():
    bootlickers = david_api.query_api("bootlickers", [args.get_bootlickers], cookies=cookies)
    if bootlickers is not None:
        # Take 5 seconds to print it out
        sleep_interval = 5 / len(bootlickers)
        console.print(f"{args.get_bootlickers}'s bootlickers:", end="\n\r")
        for bootlicker in bootlickers:
            console.print(f"- {bootlicker}", end="\n\r")
            sleep(sleep_interval)
    else:
        console.print("Error: failed to get bootlickers", end="\n\r")
    console.print("-" * 80, end="\n\r")

def print_bootlicking():
    bootlicking = david_api.query_api("bootlicking", [args.get_bootlicking], cookies=cookies)
    if bootlicking is not None:
        sleep_interval = 5 / len(bootlicking)
        console.print(f"{args.get_bootlicking}'s bootlicking:", end="\n\r")
        for bootlicker in bootlicking:
            console.print(f"- {bootlicker}", end="\n\r")
            sleep(sleep_interval)
    else:
        console.print("Error: failed to get bootlicking", end="\n\r")
    console.print("-" * 80, end="\n\r")

# Main execution
if __name__ == "__main__":
    print_david_logo()
    args = get_args()
    console.print("Loading David Social...", end="\n\r")

    # Ping DS to check if it is up
    ping = david_api.query_api("ping")
    if ping is None:
        console.print("Oh no, David Social is down!! How will we ever survive? :(", end="\n\r")
        exit(1)

    session = login()
    if session is None:
        console.print("Error: failed to login", end="\n\r")
        exit(1)

    cookies = session.cookies

    console.print("Welcome to David Social!", end="\n\r")

    # Run through the arguments
    if args.ticker:
        print_ticker()
    if args.pet_cat:
        pet_cat()
    # This line is elif because we print catpets when we pet the cat anyway
    elif args.catpets:
        print_catpets()
    if args.feed != -1:
        print_bootlicker_feed()
    if args.global_feed != -1:
        print_global_feed()
    if args.update_ticker:
        update_ticker()
    if args.post:
        make_post()
    if args.get_replies:
        print_replies()
    if args.get_avatar:
        print_avatar()
    # Note this prints ALL posts
    if args.get_user_posts:
        print_user_posts()
    if args.get_bootlickers:
        print_bootlickers()
    if args.get_bootlicking:
        print_bootlicking()
