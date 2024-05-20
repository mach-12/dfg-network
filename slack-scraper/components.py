# Selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains

from datetime import datetime, timedelta
import time
import json
import os

# Injecting Enums
from settings import Config, LoginPage, ChannelsPage

def load_webdriver(cookies_file: str):
    # Initialize the driver and open the Slack workspace URL
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.set_window_position(0, 0)
    driver.set_window_size(1024, 1024)
    wait = WebDriverWait(driver, 1000)

    # Load URL
    print("Loading", Config.SLACK_WORKSPACE_URL.value)
    driver.get(Config.SLACK_WORKSPACE_URL.value)

    # Load cookies if they exist
    cookies_exists = load_cookies(driver, cookies_file)
    driver.refresh()
    return driver, wait, cookies_exists

def store_cookies(driver: WebDriver, file_path: str):
    cookies = driver.get_cookies()
    with open(file_path, 'w') as file:
        json.dump(cookies, file)

def load_cookies(driver: WebDriver, file_path: str):
    """Loads cookies and Returns truthy value if it exists"""
    try:
        with open(file_path, 'r') as file:
            cookies = json.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)

        return True

    except FileNotFoundError:
        print("Cookies file not found. Proceeding without loading cookies.")
        return False

def login_to_slack(driver: WebDriver):
    # Find elements
    email = driver.find_element(By.ID, LoginPage.ENTER_EMAIL.value)
    password = driver.find_element(By.ID, LoginPage.ENTER_PASSWORD.value)
    signin_btn = driver.find_element(By.ID, LoginPage.SIGNIN.value)

    # Log in
    email.send_keys(Config.SLACK_EMAIL.value)
    password.send_keys(Config.SLACK_PASSWORD.value)
    time.sleep(0.2)
    signin_btn.click()

def navigate_to_channel(driver: WebDriver, wait):
    """
    Select and click the channel name
    """
    channel_name = Config.CHANNEL_NAME.value

    try:
        channel = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, f'[data-qa="channel_sidebar_name_{channel_name}"]')))
        print("Channel found", channel.text)
        channel.click()


    except:
        raise Exception(f"DOES NOT EXIST: Could not find channel by name: {channel_name}")

def scrape_channel(driver: WebDriver, scroll_offset: int, time_delay: float):
    """
    Scrape the specific channel
    """
    
    # Date till which you want to scrape up to
    start_date = datetime.strptime(f'{Config.START_YEAR.value}-{Config.START_MONTH.value}-{Config.START_DATE.value}', '%Y-%m-%d')
    date_found = False
    
    scraped_data = []
    failures = 0
    
    while not date_found:
        date_buttons = driver.find_elements(By.CLASS_NAME, ChannelsPage.DATE_BUTTON.value)
        for button in date_buttons:
            date = parse_date(button.text)
            if date < start_date:
                print("Found the desired date:", date)
                date_found = True
                break

        if not date_found:
            data, faced_error = scrape_posts(driver)
            scraped_data.append(data)
            if faced_error:
                failures += 1
            print("Saved data of", data['sender_name'])
            time.sleep(time_delay)
            scroll_up(driver, scroll_offset)
            
    return scraped_data, failures

def scrape_posts(driver: WebDriver):
    """
    Find all posts and store
    """

    containers = driver.find_elements(By.CLASS_NAME, ChannelsPage.BASE_CONTAINER.value)

    for container in containers:
        faced_error = False

        try:
            image_button = container.find_element(By.CLASS_NAME, ChannelsPage.PROFILE.value)
            image_link = image_button.find_element(By.TAG_NAME, 'img').get_attribute('src')
        except:
            image_link = "404"
            faced_error = True
        try:
            sender_button = container.find_element(By.CSS_SELECTOR, ChannelsPage.USERNAME.value)
            sender_id = sender_button.get_attribute('data-message-sender')
            sender_name = sender_button.text
        except:
            sender_name = "404"
            sender_id = "404"
            faced_error = True

        try:
            timestamp = container.find_element(By.CLASS_NAME, ChannelsPage.TIMESTAMP.value).text
        except:
            timestamp = "404"
            faced_error = True

        try:
            information = container.find_element(By.CLASS_NAME, ChannelsPage.INTRODUCTION.value).get_attribute('outerHTML')
        except:
            information = "404"
            faced_error = True

        # Store the extracted data in a dictionary
        data = {
            'image_link': image_link,
            'sender_id': sender_id,
            'sender_name': sender_name,
            'timestamp': timestamp,
            'information': information
        }
        return data, faced_error


def parse_date(input_date: str):
    """
    Handles the various date formats and returns datetime objects
    """
    input_date = input_date.strip()

    formats = [
        "%A, %d %B",  # Friday, 17th May
        "%d %B %Y",   # 12 December 2023
        "Today %H:%M", # Today xyz
        "Yesterday %H:%M" # Yesterday xyz
    ]

    for fmt in formats:
        try:
            parsed_date = datetime.strptime(input_date, fmt)

            if 'Today' in fmt:
                parsed_date = datetime.now().replace(hour=parsed_date.hour, minute=parsed_date.minute)
            elif 'Yesterday' in fmt:
                parsed_date = (datetime.now() - timedelta(days=1)).replace(hour=parsed_date.hour, minute=parsed_date.minute)

            if parsed_date.year == 1900:
                parsed_date = parsed_date.replace(year=datetime.now().year)

            return parsed_date
        except ValueError:
            pass

    raise ValueError("Failed to parse date: {}".format(input_date))


def scroll_up(driver: WebDriver, scroll_offset: int):
    """
    Handling the custom scrollbar by doing a drag & drop action
    """
    scrollbar_bar = driver.find_elements(By.CLASS_NAME, ChannelsPage.SCROLL_BAR.value)[1]

    actions = ActionChains(driver)

    actions.drag_and_drop_by_offset(scrollbar_bar, 0, scroll_offset).perform()

def save_scraped_data(scraped_data, failures, outputs_folder='outputs'):
    # Create DataFrame and drop duplicates
    df = pd.DataFrame(scraped_data)

    # Generate timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Ensure outputs folder exists
    os.makedirs(outputs_folder, exist_ok=True)

    # Define file path with timestamp
    file_path = os.path.join(outputs_folder, f'scraped_file_{timestamp}.csv')

    # Save DataFrame to CSV
    df.to_csv(file_path, index=False)

    # Print results
    print("Scraped Profiles:", df.drop_duplicates(subset=["sender_name"]).reset_index(drop=True).shape[0])
    print("Failures:", failures)
