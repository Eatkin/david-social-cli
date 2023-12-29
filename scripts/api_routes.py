import os
import requests
import json
from scripts.console import console


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
    "avi_url": os.environ.get("DAVID_GET_AVI_URL"),
}

# Lookup table for the parameters of each route
# (Mostly just for my own reference)
route_params = {
    "profile": ["username"],
    "check_already_liked": ["postId"],
    "get_cat_pets": [],
    "user_posts": ["username"],
    "replies": ["postId"],
    "post_data": ["id"],
    "user_list": [],
    "bootlicker_feed": ["id"],
    "global_feed": [],
    "get_bootlickers": ["id"],
    "get_followers": ["id"],
    "get_likes": ["id"],
    "avi_url": ["id"],
}

def validate_routes(quiet=False):
    # Loop over the get routes to check if they are set
    all_routes_missing = True
    routes_missing = []
    for route in get_routes:
        if get_routes[route] == "" or get_routes[route] is None:
            if not quiet:
                print(f"Error: {route} is not set in environment variables")
            routes_missing.append(route)
        else:
            all_routes_missing = False

    if not quiet:
        if all_routes_missing:
            print("Error: no routes set in environment variables")
            print("Please contact David for API routes")
        elif len(routes_missing) > 0:
            print(f"Missing routes: {routes_missing}")
            print("Functionality will be limited")
        else:
            print("All routes set! :3")

    return routes_missing

def get_api_response(route, params=[]):
    if route in missing_routes:
        console.print(f"Error: {route} is not set in environment variables")
        return None
    if route not in get_routes:
        console.print(f"Error: {route} is not a valid route")
        return None

    params = {p_name: p for p_name, p in zip(route_params[route], params)}

    # Make the request
    response = requests.get(get_routes[route], params=params)

    if response.status_code == 200:
        json_data = response.json()
        try:
            return json.loads(json_data)
        except:
            return json_data
    else:
        console.print(f"Error: {response.status_code} {response.reason}")
        return None


missing_routes = validate_routes(quiet=True)
