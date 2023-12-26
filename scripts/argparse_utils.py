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
    args.add_argument("-f", "--feed", action="store_true", help="Get the feed")
    args.add_argument("-gf", "--global-feed", action="store_true", help="Get the global feed")
    args.add_argument("-t", "--ticker", action="store_true", help="Get the ticker")
    args.add_argument("-p", "--post", type=str, help="Make a post")
    args.add_argument("-ut", "--update-ticker", type=str, help="Update the ticker")
    return args

def validate_arguments(args):
    """Validate the arguments passed to argparse_init."""
    # Cannot get feed and global feed at the same time
    if args.feed and args.global_feed:
        print("Cannot get feed and global feed at the same time")
        return False

    return True

def get_arguments(args):
    """Get the arguments passed to argparse_init."""
    return args.parse_args()
