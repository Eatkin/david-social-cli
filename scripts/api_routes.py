import os
import requests
import json
from scripts.console import console


BASE_URL = "https://www.davidsocial.com"

# Define routes for the API
# Uses environment variables to hide the routes
routes = {
    'ping': (requests.get, '/api/ping'),
    'version': (requests.get, '/api/version'),
    'avi-url': (requests.get, '/api/avi-url'),
    'user-posts': (requests.get, '/api/user-posts'),
    'replies': (requests.get, '/api/replies'),
    'get-post': (requests.get, '/api/get-post'),
    'user-list': (requests.get, '/api/user-list'),
    'bootlickers': (requests.get, '/api/bootlickers'),
    'bootlicking': (requests.get, '/api/bootlicking'),
    'liked-by': (requests.get, '/api/liked-by'),
    'profile': (requests.get, '/api/profile'),
    'get-ticker-text': (requests.get, '/api/get-ticker-text'),
    'login': (requests.post, '/login'),
    'global-feed': (requests.post, '/api/global-feed'),
    'bootlicker-feed': (requests.post, '/api/bootlicker-feed'),
    'new-post': (requests.post, '/api/new-post'),
    'delete-post': (requests.post, '/api/delete-post'),
    'like-post': (requests.post, '/api/like-post'),
    'my-notifications': (requests.post, '/api/my-notifications'),
    'public-set-ticker-text': (requests.post, '/api/public-set-ticker-text'),
}

# Lookup table for the parameters of each route
# (Mostly just for my own reference)
route_params = {
    'ping': [],
    'version': [],
    'avi-url': ['username'],
    'user-posts': ['username'],
    'replies': ['id'],
    'get-post': ['id'],
    'user-list': [],
    'bootlickers': ['username'],
    'bootlicking': ['username'],
    'liked-by': ['id'],
    'profile': ['username'],
    'get-ticker-text': [],
    'login': ['username', 'password'],
    'global-feed': ['window'],
    'bootlicker-feed': ['window'],
    'new-post': ['text', 'replyTo'],
    'delete-post': ['id'],
    'like-post': ['id'],
    'my-notifications': [],
    'public-set-ticker-text': ['text'],
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
        # Check if there IS data
        if json_data == "" or json_data is None:
            console.print(f"Error: {route} returned no data")
            return None
        try:
            return json.loads(json_data)
        except:
            return json_data
    else:
        console.print(f"Error: {response.status_code} {response.reason}")
        return None


missing_routes = validate_routes(quiet=True)
