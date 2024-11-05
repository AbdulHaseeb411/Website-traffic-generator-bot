import sys
import csv
import requests
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from PyQt5 import QtWidgets
import time

class TrafficBot(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Traffic Bot")
        self.setGeometry(100, 100, 600, 500)

        layout = QtWidgets.QVBoxLayout()

        self.file_input = QtWidgets.QLineEdit(self)
        self.file_input.setPlaceholderText("Enter Proxies CSV file path")
        layout.addWidget(self.file_input)

        self.browse_file_btn = QtWidgets.QPushButton("Browse CSV", self)
        self.browse_file_btn.clicked.connect(self.browse_file)
        layout.addWidget(self.browse_file_btn)

        self.keywords_file_input = QtWidgets.QLineEdit(self)
        self.keywords_file_input.setPlaceholderText("Enter Keywords CSV file path")
        layout.addWidget(self.keywords_file_input)

        self.browse_keywords_file_btn = QtWidgets.QPushButton("Browse Keywords", self)
        self.browse_keywords_file_btn.clicked.connect(self.browse_keywords_file)
        layout.addWidget(self.browse_keywords_file_btn)

        self.clicks_per_proxy_input = QtWidgets.QSpinBox(self)
        self.clicks_per_proxy_input.setRange(1, 100)
        self.clicks_per_proxy_input.setValue(5)
        layout.addWidget(QtWidgets.QLabel("Clicks per Proxy:"))
        layout.addWidget(self.clicks_per_proxy_input)

        self.thread_count_input = QtWidgets.QSpinBox(self)
        self.thread_count_input.setRange(1, 32)
        self.thread_count_input.setValue(4)
        layout.addWidget(QtWidgets.QLabel("Number of Threads:"))
        layout.addWidget(self.thread_count_input)

        self.multithreading_checkbox = QtWidgets.QCheckBox("Enable Multithreading")
        layout.addWidget(self.multithreading_checkbox)

        self.start_btn = QtWidgets.QPushButton("Start Bot", self)
        self.start_btn.clicked.connect(self.start_bot)
        layout.addWidget(self.start_btn)

        self.status_output = QtWidgets.QTextBrowser(self)
        layout.addWidget(self.status_output)

        self.setLayout(layout)

    def browse_file(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Proxies CSV File", "", "CSV Files (*.csv)")
        if file_path:
            self.file_input.setText(file_path)

    def browse_keywords_file(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Keywords CSV File", "", "CSV Files (*.csv)")
        if file_path:
            self.keywords_file_input.setText(file_path)

    def start_bot(self):
        proxies_file_path = self.file_input.text()
        keywords_file_path = self.keywords_file_input.text()
        proxies = self.read_proxies_from_csv(proxies_file_path)
        keywords_and_titles = self.read_keywords_from_csv(keywords_file_path)
        clicks_per_proxy = self.clicks_per_proxy_input.value()
        threading_enabled = self.multithreading_checkbox.isChecked()
        thread_count = self.thread_count_input.value()

        if threading_enabled:
            threads = []
            for proxy in proxies:
                if self.check_proxy(proxy):
                    for keyword, website_title in keywords_and_titles:
                        thread = threading.Thread(target=self.run_bot, args=(proxy, keyword, website_title, clicks_per_proxy))
                        threads.append(thread)
                        thread.start()
                else:
                    self.status_output.append(f"Skipping invalid proxy: {proxy}")

            for thread in threads:
                thread.join()
        else:
            for proxy in proxies:
                if self.check_proxy(proxy):
                    for keyword, website_title in keywords_and_titles:
                        self.run_bot(proxy, keyword, website_title, clicks_per_proxy)
                else:
                    self.status_output.append(f"Skipping invalid proxy: {proxy}")

    def check_proxy(self, proxy):
        try:
            response = requests.get("http://ip-api.com/json", proxies={"http": proxy, "https": proxy}, timeout=5)
            if response.status_code == 200 and response.json()['status'] == 'success':
                self.status_output.append(f"Proxy is valid: {response.json()['query']}")
                return True
            else:
                self.status_output.append("Proxy is not valid.")
                return False
        except Exception as e:
            self.status_output.append(f"Error checking proxy: {e}")
            return False

    def search_and_click(self, driver, keyword, website_title):
        try:
            driver.get("https://www.google.com")
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            search_box.send_keys(keyword + Keys.RETURN)

            self.status_output.append(f"Searching for: {keyword} and looking for title: {website_title}")
            website_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//h3[contains(text(), '{website_title}')]"))
            )
            actions = ActionChains(driver)
            actions.move_to_element(website_element).click().perform()
            time.sleep(3)
            self.status_output.append(f"Clicked on the website title: {website_title}")
        except Exception as e:
            self.status_output.append(f"An error occurred while searching and clicking: {e}")

    def read_proxies_from_csv(self, file_path):
        proxies = []
        try:
            with open(file_path, mode='r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    proxy = f"http://{row['user']}:{row['password']}@{row['ip']}:{row['port']}"
                    proxies.append(proxy)
            self.status_output.append(f"Loaded {len(proxies)} proxies from {file_path}.")
        except Exception as e:
            self.status_output.append(f"Error loading proxies CSV: {e}")
        return proxies

    def read_keywords_from_csv(self, file_path):
        keywords_and_titles = []
        try:
            with open(file_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    keyword = str(row['keyword'])
                    website_title = str(row['website_title'])
                    keywords_and_titles.append((keyword, website_title))
                    self.status_output.append(f"Read keyword: '{keyword}' with website title: '{website_title}'")
            self.status_output.append(f"Loaded {len(keywords_and_titles)} keywords and titles from {file_path}.")
        except Exception as e:
            self.status_output.append(f"Error loading keywords CSV: {e}")
        return keywords_and_titles

    def run_bot(self, proxy, keyword, website_title, clicks_per_proxy):
        chrome_options = Options()
        chrome_options.add_argument('--incognito')  # Run in incognito mode
        chrome_options.add_argument('--disable-extensions')  # Disable extensions 

        if proxy:
            chrome_options.add_argument(f'--proxy-server={proxy}')
            self.status_output.append(f"Using proxy: {proxy}")
        else:
            self.status_output.append("No proxy provided, running Chrome without proxy.")

        chrome_driver_path = ChromeDriverManager().install()

        driver = webdriver.Chrome(service=Service(chrome_driver_path), options=chrome_options)

        for i in range(clicks_per_proxy):
            self.status_output.append(f"Performing click {i + 1} of {clicks_per_proxy} with proxy: {proxy if proxy else 'None'}...")
            if keyword:
                self.search_and_click(driver, keyword, website_title)

        driver.quit()
        self.status_output.append("Bot run complete, closing browser.")

def main():
    app = QtWidgets.QApplication(sys.argv)
    bot = TrafficBot()
    bot.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
