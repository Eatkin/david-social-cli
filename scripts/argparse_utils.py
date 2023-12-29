import argparse

def argparse_init():
    """Initialize argparse with common arguments.
    Arguments:
    -f --feed - Get the feed
    -gf --global-feed - Get the global feed
    -t --ticker - Get the ticker
    -p --post - Make a post (requires string)
    -ut --update-ticker - Update the ticker"""
    args = argparse.ArgumentParser()
    args.add_argument("-f", "--feed", type=int, help="Get a number of posts from your Bootlicker feed e.g. -f 10")
    args.add_argument("-gf", "--global-feed", type=int, help="Get a number of posts from the global feed e.g. -gf 10")
    args.add_argument("-t", "--ticker", action="store_true", help="Get the ticker e.g. -t", default=None)
    args.add_argument("-p", "--post", type=str, help="Make a post e.g. -p \"Hello friends :3\"", default=None)
    args.add_argument("-ut", "--update-ticker", type=str, help="Update the ticker e.g. -ut \"Hello everyone on David Social :3\"", default=None)
    args.add_argument("-cp", "--catpets", action="store_true", help="Get the number of cat pets, e.g. -cp", default=None)
    args.add_argument("-gr", "--get-replies", type=int, help="Get replies to a post by post id, e.g. -gr 123", default=None)
    args.add_argument("-gav", "--get-avatar", type=str, help="Get a user's avatar, e.g. -gav username", default=None)
    # These need adding in the future
    args.add_argument("-gup", "--get-user-posts", type=str, help="Get a user's posts, e.g. -gup username", default=None)
    args.add_argument("-gb", "--get-bootlickers", type=str, help="Get a user's bootlickers, e.g. -gb username", default=None)

    return args

def validate_arguments(args):
    """Validate the arguments passed to argparse_init."""
    # Cannot get feed and global feed at the same time
    if args.feed and args.global_feed:
        print("Cannot get feed and global feed at the same time")
        return False

    # If no arguments are passed then print help
    if not any(vars(args).values()):
        print("No arguments passed")
        return False

    return True

def parse_args(parser):
    """Parse the arguments passed to argparse_init."""
    args = parser.parse_args()
    return args
