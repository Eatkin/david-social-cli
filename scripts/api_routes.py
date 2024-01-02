import requests
import json
from bs4 import BeautifulSoup
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
    'pet-cat': (requests.get, '/api/pet-cat'),
    'get-cat-pets': (requests.get, '/api/get-cat-pets'),
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
    'pet-cat': [],
    'get-cat-pets': [],
}

def query_api(route, params=[], cookies=None):
    if route not in routes:
        console.print(f"Error: {route} is not a valid route")
        return None

    params = {p_name: p for p_name, p in zip(route_params[route], params)}

    # Construct url
    url = BASE_URL + routes[route][1]

    # Make the request
    response = routes[route][0](url, json=params, cookies=cookies)

    if response.status_code == 200:
        # Specific exception for login
        if route == "login":
            # This returns the session
            return response

        # Some of the get requests return a string instead of json
        try:
            json_data = response.json()
        except:
            html = response.text
            soup = BeautifulSoup(html, "html.parser")
            # Extract the text from the soup
            json_data = soup.text

        # Check if there IS data
        if json_data == "" or json_data is None:
            console.print(f"Error: {route} returned no data")
            return None

        # Finally parse the json if applicable
        try:
            return json.loads(json_data)
        except:
            return json_data
    else:
        console.print(f"Error: {response.status_code} {response.reason}")
        return None
