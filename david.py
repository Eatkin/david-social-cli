import scripts.toml_utils as tu
import scripts.chromium_utils as cu
from rich.console import Console
from rich.markdown import Markdown

# Initialise the console
console = Console()

# Get the username and password
username, password = tu.get_secrets()
driver = cu.init_webdriver()
# Get the homepage
homepage_soup = cu.get_david_homepage(driver)
homepage_content = cu.parse_soup(homepage_soup)

# Homepage is in markdown format so parse it with rich
homepage_markdown = Markdown(homepage_content)
console.print(homepage_markdown)
