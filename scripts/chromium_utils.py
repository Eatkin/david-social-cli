from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from html2text import html2text

def init_webdriver():
    """Initialize the webdriver"""
    # Setup the browser as headless
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(options=chrome_options)
    return driver

def get_david_homepage(driver):
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

def parse_soup(soup):
    """Just returns the soup without tags as formatted by html2text"""
    # Loop through all the tags and convert them to text
    output = ""
    output += html2text(str(soup)) + "\n"

    # Recursively strip the newlines to be a maximum of 2
    while "\n\n\n" in output:
        output = output.replace("\n\n\n", "\n\n")

    return output
