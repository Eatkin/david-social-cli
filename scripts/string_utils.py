import requests
from PIL import Image
from io import BytesIO
import curses

# Define the ascii characters to use for the image
# ascii_chars = list("$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'.")
# Alt, smaller gradient (looks better imo)
ascii_chars = list(" .:-=+*#%@")[::-1]

def image_to_ascii(image, url=True):
    """Definitely not plaigarised from https://www.askpython.com/python/examples/turn-images-to-ascii-art-using-python"""
    if url:
        image = get_image(image)
        exif = image.getexif()
        rot = exif.get(274, None)
        width, height = image.size
        max_size = (max(width, height), max(width, height))
        rotated_size = (height, width)
        """Guide to rotation values:
        1 = Horizontal (normal)
        2 = Mirror horizontal
        3 = Rotate 180
        4 = Mirror vertical
        5 = Mirror horizontal and rotate 270 CW
        6 = Rotate 90 CW
        7 = Mirror horizontal and rotate 90 CW
        8 = Rotate 270 CW"""
        # Process the image as necessary using a dictionary with functions
        rot_dict = {
            1: lambda x: x,
            2: lambda x: x.transpose(Image.FLIP_LEFT_RIGHT),
            3: lambda x: x.rotate(180),
            4: lambda x: x.rotate(180).transpose(Image.FLIP_LEFT_RIGHT),
            5: lambda x: x.resize(max_size).rotate(-90).transpose(Image.FLIP_LEFT_RIGHT).resize(rotated_size),
            6: lambda x: x.resize(max_size).rotate(-90).resize(rotated_size),
            7: lambda x: x.resize(max_size).rotate(90).transpose(Image.FLIP_LEFT_RIGHT).resize(rotated_size),
            8: lambda x: x.resize(max_size).rotate(90).resize(rotated_size),
        }
        if rot is not None:
            image = rot_dict[rot](image)
    else:
        image = Image.open(image)
        image = image.convert("RGBA")
    if image is None:
        return None

    # Resize the image
    # This checks for the available space in the terminal
    MAX_HEIGHT, MAX_WIDTH = curses.initscr().getmaxyx()
    # Get current cursor position to avoid overflow
    y, x = curses.initscr().getyx()
    MAX_HEIGHT -= y
    MAX_WIDTH -= x
    image, new_width, new_height = resize_image(image, MAX_WIDTH, MAX_HEIGHT)

    # Convert to greyscale
    image = image.convert('L')
    # Convert to ascii chars
    pixels = image.getdata()
    # Calculate how much to divide by based on ascii_chars list length
    div = 255/(len(ascii_chars))
    # Use min() to avoid index out of range errors which happen for some reason and I'm too stupid/lazy to fix
    new_pixels = [ascii_chars[min(round(pixel/div), len(ascii_chars) - 1)] for pixel in pixels]
    new_pixels = ''.join(new_pixels)

    # split string of chars into multiple strings of length equal to new width and create a list
    new_pixels_count = len(new_pixels)
    ascii_image = [new_pixels[index:index + new_width] for index in range(0, new_pixels_count, new_width)]
    ascii_image = "\n".join(ascii_image)
    return ascii_image

def get_image(image_url):
    """Get an image from a url"""
    response = requests.get(image_url)
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
        # Convert otherwise it yells at me for some reason
        # This is a public repo why am I writing things like this
        img = img.convert("RGBA")
        return img
    else:
        return None

def resize_image(img, max_width, max_height):
    """Resize an image to a max width"""
    # Code I definitely didn't find online to resize the image lol
    width, height = img.size
    aspect_ratio = height/width
    new_width = max_width
    # Font is taller than it is wide so we need to reduce the height by a factor
    # This is good enough based on trying to resize the David Social logo
    reduction_factor = 0.475
    new_height = int(reduction_factor * aspect_ratio * new_width)

    # Check if the new height is too tall
    if new_height > max_height:
        new_height = max_height
        new_width = int(new_height/(reduction_factor * aspect_ratio))

    img = img.resize((new_width, new_height))
    return img, new_width, new_height
