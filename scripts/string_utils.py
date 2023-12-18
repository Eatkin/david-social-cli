import requests
from PIL import Image
from io import BytesIO

# Define the ascii characters to use for the image
ascii_chars = list("$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'.")
# Alt, smaller gradient
ascii_chars = list(" .:-=+*#%@")[::-1]

def image_to_ascii(image_url):
    """Definitely not plaigarised from https://www.askpython.com/python/examples/turn-images-to-ascii-art-using-python"""
    image = get_image(image_url)
    if image is None:
        return None
    # resize the image
    max_width = 120
    max_height = 48
    image, new_width, new_height = resize_image(image, max_width, max_height)
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
        img = img.convert("RGBA")
        return img
    else:
        return None

def resize_image(img, max_width, max_height):
    """Resize an image to a max width"""
    # Code I found online to resize the image lol
    width, height = img.size
    aspect_ratio = height/width
    new_width = max_width
    # Why is it multiplied by 0.55? I don't know, and I definitely didn't just copy this from some random website
    new_height = int(0.55 * aspect_ratio * new_width)

    # Check if the new height is too tall
    if new_height > max_height:
        new_height = max_height
        new_width = int(new_height/(0.55 * aspect_ratio))

    img = img.resize((new_width, new_height))
    return img, new_width, new_height
