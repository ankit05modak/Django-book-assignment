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
    """Scrape books based on given category.

    Args:
        category (str): _description_
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


def get_category_url(driver: WebDriver, category_name: str):
    soup = BeautifulSoup(driver.page_source, "html.parser")

    for a in soup.select("ul li a"):
        if a.text.strip().lower() == category_name.lower():
            return a["href"]

    return None


def setup_webdriver() -> webdriver:
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
    driver.get(url)

    return driver


def get_book_urls(driver: WebDriver, category_url: str) -> list:
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Get all books urls
    books = soup.select("article.product_pod")

    book_urls = []

    for book in books:
        link = book.select_one("h3 a")["href"]
        full_url = urljoin(category_url, link)
        book_urls.append(full_url)

    return book_urls


def get_book_data(driver: WebDriver, book_url: str) -> Tuple[str, int, str]:
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
    obj, created = Book.objects.update_or_create(
        title=book_name,
        defaults={
            "genre": book_genre,
            "price": book_price,
            "description": book_description,
        },
    )
