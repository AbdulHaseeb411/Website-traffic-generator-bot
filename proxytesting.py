from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
import time

# Define proxy settings
username = ""
password = ""
ip_address ="" 
port = ""
proxy = f"http://{username}:{password}@{ip_address}:{port}"

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument(f'--proxy-server={proxy}')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# Initialize the WebDriver
def get_driver():
    service = Service()  # Optionally specify the path to chromedriver here
    return webdriver.Chrome(service=service, options=chrome_options)

# Try to open the URL with retry
url = "https://jojokango1.tumblr.com"
max_retries = 3
for attempt in range(max_retries):
    try:
        driver = get_driver()
        driver.get(url)
        time.sleep(5)  # Allow time to load the page
        print("Page loaded successfully!")
        break  # Exit the loop if successful
    except WebDriverException as e:
        print(f"WebDriverException occurred: {e}")
        time.sleep(2)  # Wait before retrying
    except Exception as e:
        print(f"An error occurred: {e}")
        break  # Exit on unexpected errors
    finally:
        driver.quit()
