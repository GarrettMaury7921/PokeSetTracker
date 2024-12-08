import requests
from datetime import datetime
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import unquote
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = "xxxxx"


# Get the current date
def get_current_date():
    # Get the current date
    date = datetime.now()

    # Format the date as mm/dd/yy
    formatted_date = date.strftime('%m/%d/%y')
    file_friendly_formatted_date = datetime.today().strftime('%m_%d_%Y')

    return formatted_date, file_friendly_formatted_date


# Get the HTML from the website
def query(url_sets):
    website = requests.get(url_sets)
    website_text = website.text
    return website_text


# Parse through the HTML to find the links to all of the sets on the website
def parse(html):
    number_of_sets = 0
    soup = BeautifulSoup(html, 'html.parser')
    set_links = []
    for link in soup.find_all('a', href=True):
        if link['href'].startswith('/set/'):
            set_links.append(link['href'])
            number_of_sets = number_of_sets + 1
    print('Number of Sets: ' + str(number_of_sets))
    return set_links


# Goes to each page on the website and finds the total price
def find_total_value(set_link, debug):
    new_link = url + set_link

    # Set up the web driver (using Firefox)
    options = Options()
    options.add_argument('--headless')  # Ensure headless mode is set

    # Specify the correct path to geckodriver
    service = Service(executable_path='C:/WebDrivers/geckodriver.exe')

    # Specify the correct path to the Firefox binary if it's not in the default location
    options.binary_location = 'C:/Program Files/Mozilla Firefox/firefox.exe'

    driver = webdriver.Firefox(service=service, options=options)

    try:
        driver.get(new_link)  # Navigate to the link
        if debug:
            print(f"Loaded URL: {new_link}")

        # Initialize WebDriverWait
        wait = WebDriverWait(driver, 60)

        # Wait for the 'TOTAL VALUE' span to be present
        total_value_span = wait.until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'TOTAL VALUE')]"))
        )

        # Check the span value until updated from 'N/A'
        while True:
            dollar_span = total_value_span.find_element(By.XPATH,
                                                        "following-sibling::span[contains(@class, 'MuiTypography-root')]")
            if dollar_span.text.strip() != "N/A":
                break
            time.sleep(1)

        if debug:
            print(f"Element found: {dollar_span.text.strip()}")

        return dollar_span.text.strip()

    except Exception as e:
        print(f"An error occurred in find_total_value: {e}")
        return None  # Return None for failed operations

    finally:
        try:
            driver.quit()  # Ensure driver quits even if an error occurs
        except Exception as quit_error:
            print(f"Error while quitting driver: {quit_error}")


# Function to process each link
def process_link(set_index, set_link, debug=True):
    try:
        name = concatenate_set_name(set_link)
        price = find_total_value(set_link, debug)
        return set_index, name, price
    except Exception as e:
        print(f"Error processing link {set_link}: {e}")
        return set_index, None, None


# Make the name more readable when printing it out later
def concatenate_set_name(name):
    # Extract the part after "/set/"
    set_name = name.split('/set/')[1]

    # Decode URL-encoded characters
    decoded_name = unquote(set_name)

    # Replace '+' with a space
    cleaned_name = decoded_name.replace('+', ' ')

    # Remove all characters that are not allowed in filenames
    # Windows and Linux disallow certain characters in filenames
    sanitized_name = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '', cleaned_name)

    # Additionally, remove any leading or trailing whitespace
    sanitized_name = sanitized_name.strip()

    return sanitized_name