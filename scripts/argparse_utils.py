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
    args.add_argument("-f", "--feed", type=int, help="Get a number of posts from your Bootlicker feed e.g. -f 10 (number optional)", default=-1, nargs="?")
    args.add_argument("-gf", "--global-feed", type=int, help="Get n days of posts from the global feed e.g. -gf 10 (number optional)", default=-1, nargs="?")
    args.add_argument("-t", "--ticker", action="store_true", help="Get the ticker e.g. -t")
    args.add_argument("-p", "--post", type=str, help="Make a post e.g. -p \"Hello friends :3\"")
    args.add_argument("-ut", "--update-ticker", type=str, help="Update the ticker e.g. -ut \"Hello everyone on David Social :3\"")
    args.add_argument("-cp", "--catpets", action="store_true", help="Get the number of cat pets, e.g. -cp")
    args.add_argument("-pc", "--pet-cat", action="store_true", help="Pet the cat, e.g. -pc")
    args.add_argument("-gr", "--get-replies", type=int, help="Get replies to a post by post id, e.g. -gr 123")
    args.add_argument("-gav", "--get-avatar", type=str, help="Get a user's avatar, e.g. -gav username")
    args.add_argument("-gup", "--get-user-posts", type=str, help="Get a user's posts, e.g. -gup username")
    # Below not implemented
    args.add_argument("-gb", "--get-bootlickers", type=str, help="Get a user's bootlickers, e.g. -gb username")
    args.add_argument("-gbg", "--get-bootlicking", type=str, help="Get a user's bootlicking, e.g. -gbg username")

    return args

def validate_arguments(args):
    """Validate the arguments passed to argparse_init."""
    args_provided = False
    for arg in vars(args):
        if arg == "feed" or arg == "global_feed":
            if getattr(args, arg) != -1:
                args_provided = True
                break
        elif getattr(args, arg):
            args_provided = True
            break

    if not args_provided:
        print("No arguments provided")
        return False

    # Cannot get feed and global feed at the same time
    # This is a bit of a hacky way to do it
    # Basically default argument is -1, but we can provide no argument
    # If we provide no argument it is set to None
    # So if both are not -1 we have provided both
    if args.feed != -1 and args.global_feed != -1:
        print("Cannot get feed and global feed at the same time")
        return False

    return True

def parse_args(parser):
    """Parse the arguments passed to argparse_init."""
    args = parser.parse_args()
    return args
