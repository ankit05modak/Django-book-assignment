"""Utilities to scrape book data from the configured book website and
persist it to the database.

This module uses Selenium (Chrome) to navigate pages and BeautifulSoup to
parse HTML. Functions perform network requests and have side effects
(opening a browser and writing to the database).
"""

import re
from typing import Tuple
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager

from .constants import BOOK_WEBSITE_URL
from .models import Book


def scrape_book(category: str):
    """Scrape all books for a given category and save them to the DB.

    This is the high-level workflow that:
    - creates a Chrome webdriver via `setup_webdriver()`;
    - opens the site root and finds the matching category link with
        `get_category_url()`;
    - navigates the category pages and collects all book URLs using
        `get_book_urls()`;
    - for each book URL, extracts title, price and description with
        `get_book_data()` and persists the record via `save_book()`;
    - closes the webdriver when finished.

    Args:
            category (str): Human-readable category name to scrape (case-insensitive).

    Raises:
            Exception: If the category endpoint cannot be found on the site.
    """
    # Setup the webdriver & open website in chrome-browser
    driver = setup_webdriver()

    # Open the main tab.
    driver = open_webpage(url=BOOK_WEBSITE_URL, driver=driver)

    # Locate the required category on webpage and perform click.
    category_endppoint = get_category_url(driver=driver, category_name=category)

    if not category_endppoint:
        raise Exception("Category endpoint not found.")

    category_url = BOOK_WEBSITE_URL + category_endppoint

    # Open the category page
    driver.get(category_url)

    # Get all books urls
    book_urls = get_book_urls(driver=driver, category_url=category_url)

    book_genre = category

    # Process each book
    for book_url in book_urls:
        book_name, book_price, book_description = get_book_data(
            driver=driver, book_url=book_url
        )

        save_book(
            book_name=book_name,
            book_description=book_description,
            book_price=book_price,
            book_genre=book_genre,
        )

    # Close the driver
    driver.close()


def get_category_url(driver: WebDriver, category_name: str):
    """Return the href for a category link on the currently loaded page.

    Parses `driver.page_source` and searches category links. Matching is
    case-insensitive and trims surrounding whitespace.

    Args:
        driver (WebDriver): Selenium webdriver with the page already loaded.
        category_name (str): Category name to match.

    Returns:
        str | None: The href value of the matching category link (may be
        relative), or `None` if no matching link is found.
    """
    soup = BeautifulSoup(driver.page_source, "html.parser")

    for a in soup.select("ul li a"):
        if a.text.strip().lower() == category_name.lower():
            return a["href"]

    return None


def setup_webdriver() -> webdriver:
    """Create and return a configured Chrome webdriver instance.

    Uses `webdriver_manager` to install and manage the ChromeDriver binary
    automatically and configures a few common Chrome options. The caller
    is responsible for closing the driver (`driver.close()` / `driver.quit()`).

    Returns:
        selenium.webdriver.Chrome: A configured Chrome webdriver instance.
    """
    # Chrome driver setup.
    chrome_options = Options()

    # NOTE: Following are some config settings to play around. Have fun!
    # chrome_options.add_argument("--headless")  # Enabling this makes the script run in headless mode. (The browser window wont get popped up.)
    # chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # Automatically manage chrome-driver
    service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=chrome_options)

    return driver


def open_webpage(url: str, driver: WebDriver) -> WebDriver:
    """Navigate the provided webdriver to `url` and return the driver.

    Args:
        url (str): URL to open in the browser.
        driver (WebDriver): Selenium webdriver instance.

    Returns:
        WebDriver: The same webdriver after navigation.
    """
    driver.get(url)

    return driver


def get_book_urls(driver: WebDriver, category_url: str) -> list:
    """Collect all book page URLs for a category, following pagination.

    The function parses `driver.page_source` to extract links from each
    `article.product_pod`, resolves relative URLs using `category_url`, and
    follows pagination links (`li.next a`) until no next page exists.

    Args:
        driver (WebDriver): Selenium webdriver on the category listing page.
        category_url (str): Base category URL used to resolve relative links.

    Returns:
        list[str]: Fully resolved book detail page URLs.
    """
    book_urls = []

    while True:
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Get all books urls
        books = soup.select("article.product_pod")

        for book in books:
            link = book.select_one("h3 a")["href"]
            full_url = urljoin(category_url, link)
            book_urls.append(full_url)

        # check for next page
        next_button = soup.select_one("li.next a")

        if next_button:
            next_page = next_button["href"]

            base_url = driver.current_url.rsplit("/", 1)[0]

            driver.get(f"{base_url}/{next_page}")

        else:
            break

    return book_urls


def get_book_data(driver: WebDriver, book_url: str) -> Tuple[str, int, str]:
    """Retrieve title, price and description from a book detail page.

    Navigates the webdriver to `book_url` and parses the page with
    BeautifulSoup. Attempts to extract:
    - title from `div.product_main h1`;
    - price from `.price_color` (numeric portion captured via regex);
    - description from the paragraph following `#product_description`.

    On parse errors this function prints the exception and returns sensible
    defaults (empty strings or `None` for price).

    Args:
        driver (WebDriver): Selenium webdriver instance.
        book_url (str): Full URL of the book detail page.

    Returns:
        tuple: `(name, price, description)` where `name` and `description`
        are strings and `price` is the numeric price string (e.g. '12.34')
        or `None` if not found.
    """
    # Open each book webpage to scrape the data
    driver.get(book_url)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Product name
    try:
        name = soup.select_one("div.product_main h1").text.strip()
    except Exception as e:
        print(e)
        print("Book name not found -> {book_url}")
        name = ""

    # Price
    try:
        price_text = soup.select_one(".price_color").text.strip()
        price = re.search(r"\d+\.\d+", price_text).group()
    except Exception as e:
        print(e)
        print("Book price not found -> {book_url}")
        price = None

    # Product description
    try:
        description = soup.select_one("#product_description + p").text.strip()
    except Exception as e:
        print(e)
        print("Book description not found -> {book_url}")
        description = ""

    return (name, price, description)


def save_book(book_name: str, book_price: int, book_description: str, book_genre: str):
    """Persist a scraped book to the database (create or update by title).

    Uses `Book.objects.update_or_create` with `title=book_name` and updates
    the `genre`, `price` and `description` fields.

    Args:
        book_name (str): Title of the book (lookup key).
        book_price (int | str | None): Price value to store (may be `None`).
        book_description (str): Text description of the book.
        book_genre (str): Genre/category name to set on the record.
    """
    obj, created = Book.objects.update_or_create(
        title=book_name,
        defaults={
            "genre": book_genre,
            "price": book_price,
            "description": book_description,
        },
    )
