import os
import time

from components import load_webdriver, login_to_slack, scrape_channel, navigate_to_channel, store_cookies, save_scraped_data

if __name__=="__main__":

    print("Initializing driver")

    # Path to store the cookies
    cookies_file = 'cookies/cookie.json'
    os.makedirs('cookies', exist_ok=True)

    # Initialize Web Driver
    driver, wait, cookies_exists = load_webdriver(cookies_file)

    # Else, Log In and Store
    if not cookies_exists:
        login_to_slack(driver)

        # Store cookies after logging in
        store_cookies(driver, cookies_file)

    time.sleep(2)

# Go to the channel
    navigate_to_channel(driver, wait)

    time.sleep(4)

    # Scrape Channel
    SCROLL_OFFSET = -2
    TIME_DELAY = 0.6
    scraped_data, failures = scrape_channel(driver, scroll_offset=SCROLL_OFFSET, time_delay=TIME_DELAY)

    # Save results
    save_scraped_data(scraped_data, failures, outputs_folder='outputs')
    driver.quit()