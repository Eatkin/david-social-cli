from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from html2text import html2text
from scripts.console import console
from scripts.toml_utils import get_secrets
import scripts.api_routes as david_api


def init_webdriver():
    """Initialize the webdriver"""
    # Setup the browser as headless
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(options=chrome_options)
    return driver

def get_david_homepage():
    """Get the homepage of David's website"""
    url = "https://www.davidsocial.com/"
    driver.get(url)
    # Javascript is used to load the content of the page
    # So we need to wait until the "welcomepage" div is loaded
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located(("id", "welcomepage")))

    # Now we can parse the content but delete the form
    soup = BeautifulSoup(driver.page_source, "html.parser")
    # Remove the form element from the soup
    soup.form.decompose()
    # Just grab the "welcomepage" div
    soup = soup.find("div", {"id": "welcomepage"})
    return soup

def get_david_ticker():
    """Gets the ticker at the top of the feed"""
    # Should be on the feed page now so we'll wait for post elements to load
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "post")))

    # Now they've loaded we can get the ticker content
    # Get all ticker elements
    tickers = driver.find_elements(By.CLASS_NAME, "marquee")
    # David usefully reuses the marquee class for other things so grab the last one
    # And hope for the best lol
    ticker = tickers[-1].text
    return ticker

def update_david_ticker():
    """Heads to the update ticker page and submits an update"""
    # Click on the anchor tag with content "update ticker or submit cat petting pics"
    update_ticker_anchor = driver.find_element(By.LINK_TEXT, "update ticker or submit cat petting pics")
    # Click
    update_ticker_anchor.click()

    # Wait for the textarea to load
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "textarea")))

    # Find the textarea
    textarea = driver.find_element(By.TAG_NAME, "textarea")
    # Find the submit button
    submit_button = driver.find_element(By.TAG_NAME, "button")

    input = console.input("Update the David Social ticker here :3 ")

    # Send the input to the textarea
    textarea.send_keys(input)

    # Click the submit button
    submit_button.click()

    # Wait for the alert to pop up
    alert = wait.until(EC.alert_is_present())
    # Accept the alert
    alert.accept()

    console.print("Ticker updated!")

    # Now go back to the feed
    # Find the anchor tag that contains the text "Feed"
    feed_anchor = driver.find_element(By.PARTIAL_LINK_TEXT, "Feed")
    feed_anchor.click()

    # Wait for the feed to load
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "post")))



def post_to_david_social():
    """Submit a post!"""
    input = console.input("Write stuff to your friends here :3 ")
    # Find the elements with id posting-box
    posting_box = driver.find_element(By.ID, "posting-box")

    # Set the inner html of the textarea to an empty string
    # (Otherwise it includes Write stuff to your friends here :3)
    posting_box.clear()

    # Set the content of the textarea
    posting_box.send_keys(input)

    # Find the button (its the second one, very good design David including no ids thank you)
    submit_button = driver.find_elements(By.TAG_NAME, "button")[1]

    # Press button
    submit_button.click()


def parse_soup(soup):
    """Just returns the soup without tags as formatted by html2text"""
    # Loop through all the tags and convert them to text
    output = ""
    output += html2text(str(soup)) + "\n"

    # Recursively strip the newlines to be a maximum of 2
    while "\n\n\n" in output:
        output = output.replace("\n\n\n", "\n\n")

    return output

def login(output=True):
    """Login to David Social"""
    url = "https://www.davidsocial.com/"

    driver.get(url)

    username, password = get_secrets()

    # Wait for content to load
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located(("id", "welcomepage")))

    # I'd like to take a moment to thank David for using good form semantics
    # (Sarcasm)
    # (Sorry David ly <3)
    # Find all inputs elements
    username_input, password_input = driver.find_elements(By.TAG_NAME, "input")

    # Find the button
    login_button = driver.find_element(By.TAG_NAME, "button")

    # Fill in the username and password
    username_input.send_keys(username)
    password_input.send_keys(password)

    # Click the login button
    login_button.click()

    # If we fill in incorrect credentials literally nothing happens (lol)
    # So wait to see if we're redirected, if not then we know we've failed
    try:
        # Logging in pops up an alert
        # Very good design thank you again David
        alert = wait.until(EC.alert_is_present())
        alert.accept()
        if output:
            console.print("Login success!")
        return True
    except:
        if output:
            console.print("Incorrect username or password, please review your secrets.toml file.")
        return False


# Make the driver importable
driver = init_webdriver()
