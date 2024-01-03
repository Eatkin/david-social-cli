from time import sleep
import datetime
import scripts.string_utils as su
from scripts.console import console

# How long to take to display the feed
FEED_DISPLAY_TIME = 5

def print_feed(feed):
    sleep_interval = FEED_DISPLAY_TIME / len(feed)
    for post in feed:
        post_id = post['id']
        replies = post['ncomments']
        david_selection = post['david_selection']
        # Format the timestamp
        timestamp = post['timestamp']
        timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        date_time = timestamp.strftime("%d/%m/%Y %H:%M:%S")

        # Display the post
        console.print("-" * 80, end="\n\r")
        if david_selection:
            console.print("*:･ﾟ✧*:･ﾟ✧ David Selection", end="\n\r")
        console.print(f"ID: {post_id} | Replies: {replies}")
        console.print(f"Posted by {post['username']} at {date_time}", end="\n\r")
        console.print(post['content'], end="\n\r")
        console.print("-" * 80, end="\n\r")

        # Display any likes (can use the get-likes route but this works too)
        likes = post['liked_by']
        likes = ", ".join(likes)
        console.print(f"Liked by: {likes}", end="\n\r")

        # If there is an image attached convert to ascii and display it
        image_url = post['attached_image']
        if image_url != "":
            ascii_image = su.image_to_ascii(image_url)
            if ascii_image is not None:
                console.print("-" * 80, end="\n\r")
                console.print("Attached image:", end="\n\r")
                # Use the default print because markdown doesn't work with ascii and it fucks the console print command up
                print(ascii_image)
        sleep(sleep_interval)

    console.print("-" * 80, end="\n\r")
