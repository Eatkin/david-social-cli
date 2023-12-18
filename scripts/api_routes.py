import os

# Define routes for the API
# Uses environment variables to hide the routes
get_routes = {
    "profile": os.environ.get("DAVID_GET_PROFILE"),
    "check_already_liked": os.environ.get("DAVID_GET_CHECK_ALREADY_LIKED"),
    "get_cat_pets": os.environ.get("DAVID_GET_CAT_PETS"),
    "user_posts": os.environ.get("DAVID_GET_USER_POSTS"),
    "replies": os.environ.get("DAVID_GET_REPLIES"),
    "post_data": os.environ.get("DAVID_GET_POST_DATA"),
    "user_list": os.environ.get("DAVID_GET_USER_LIST"),
    "bootlicker_feed": os.environ.get("DAVID_GET_BOOTLICKER_FEED"),
    "global_feed": os.environ.get("DAVID_GET_GLOBAL_FEED"),
    "get_bootlickers": os.environ.get("DAVID_GET_BOOTLICKERS"),
    "get_followers": os.environ.get("DAVID_GET_FOLLOWERS"),
    "get_likes": os.environ.get("DAVID_GET_LIKES"),
    "avi-url": os.environ.get("DAVID_GET_AVI_URL"),
}

# Lookup table for the parameters of each route
route_params = {
    "profile": ["username"],
    "check_already_liked": ["postId"],
    "get_cat_pets": ["postId"],
    "user_posts": ["username"],
    "replies": ["postId"],
    "post_data": ["id"],
    "user_list": [],
    "bootlicker_feed": ["id"],
    "global_feed": [],
    "get_bootlickers": ["id"],
    "get_followers": ["id"],
    "get_likes": ["id"],
    "avi-url": ["id"],
}

def validate_routes():
    # Loop over the get routes to check if they are set
    all_routes_missing = True
    routes_missing = []
    for route in get_routes:
        if get_routes[route] is None:
            print(f"Error: {route} is not set in environment variables")
            routes_missing.append(route)
        else:
            all_routes_missing = False

    if all_routes_missing:
        print("Error: no routes set in environment variables")
        print("Please contact David for API routes")
    elif len(routes_missing) > 0:
        print(f"Missing routes: {routes_missing}")
        print("Functionality will be limited")

    return routes_missing
