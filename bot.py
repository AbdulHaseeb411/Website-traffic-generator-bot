import csv
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time

# Function to check if a proxy is valid
def check_proxy(proxy):
    try:
        response = requests.get("http://ip-api.com/json", proxies={"http": proxy, "https": proxy}, timeout=5)
        if response.status_code == 200 and response.json()['status'] == 'success':
            print(f"Proxy is valid. IP: {response.json()['query']}")
            return True
        else:
            print("Proxy is not valid.")
            return False
    except Exception as e:
        print(f"Error checking proxy: {e}")
        return False

# Function to perform Google search and click on the website
def search_and_click(driver, keyword, website_title):
    try:
        print(f"Searching for keyword: {keyword}")
        driver.get("https://www.google.com")

        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.RETURN)

        print("Search performed, looking for the website...")
        website_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//h3[contains(text(), '{website_title}')]"))
        )

        print(f"Found website element with title: {website_title}, performing click.")
        actions = ActionChains(driver)
        actions.move_to_element(website_element).click().perform()
        response = requests.get("https://jojokango1.tumblr.com/")  # Replace with the actual URL
        if response.status_code != 200:
            print(f"Failed to access website. Status code: {response.status_code}")
            return
        time.sleep(3)  # Wait for the page to load
    except Exception as e:
        print(f"An error occurred: {e}")

# Function to read proxies from a CSV file
def read_proxies_from_csv(file_path):
    proxies = []
    with open(file_path, mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            proxy = f"http://{row['user']}:{row['password']}@{row['ip']}:{row['port']}"
            proxies.append(proxy)
    return proxies

# Main function to run the bot
def run_bot(proxy, keyword, website_title, clicks_per_proxy):
    print(f"Using proxy: {proxy}")
    print(f"Starting bot with {clicks_per_proxy} clicks per proxy.")
    
    # Configure Chrome with proxy settings
    chrome_options = Options()
    chrome_options.add_argument(f'--proxy-server={proxy}')
    chrome_options.add_argument('--proxy-bypass-list=*') 

    # Initialize Chrome WebDriver using WebDriver Manager
    chrome_driver_path = "chromedriver.exe"
        
        # Initialize WebDriver
    driver = webdriver.Chrome(service=Service(chrome_driver_path), options=chrome_options)

    # Perform the search and click process 'clicks_per_proxy' times
    for i in range(clicks_per_proxy):
        print(f"Performing click {i+1} out of {clicks_per_proxy}...")
        search_and_click(driver, keyword, website_title)

    driver.quit()
    print("Bot run complete, closing browser.")
    time.sleep(5)  # Pause before finishing

if __name__ == "__main__":
    proxies = read_proxies_from_csv('proxies.csv')

    keyword = "jojokango1.tumblr"  # Replace with your desired search keyword
    website_title = "JOJOBET: Güncel Giriş Adresleri - Yeni — Ask me anything"  # Replace with your website's title from the search results

    clicks_per_proxy = 2  # Set the number of clicks to perform per proxy

    for proxy in proxies:
        if check_proxy(proxy):  # Check if the proxy is valid
            run_bot(proxy, keyword, website_title, clicks_per_proxy)
        else:
            print(f"Skipping invalid proxy: {proxy}")
