import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


def save_credentials(username, password):
    with open("credentials.txt", "w") as file:
        file.write(f"{username}\n{password}")


def load_credentials():
    if not os.path.exists("credentials.txt"):
        return None

    with open("credentials.txt", "r") as file:
        lines = file.readlines()
        if len(lines) >= 2:
            return lines[0].strip(), lines[1].strip()

    return None


def prompt_credentials():
    username = input("Enter your Instagram username: ")
    password = input("Enter your Instagram password: ")
    save_credentials(username, password)
    return username, password


def login(driver, username, password):
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(2)

    username_input = driver.find_element(By.CSS_SELECTOR, "input[name='username']")
    password_input = driver.find_element(By.CSS_SELECTOR, "input[name='password']")

    username_input.send_keys(username)
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)
    time.sleep(5)


def check_logged_in(driver):
    try:
        # Look for a specific element that indicates the user is logged in
        driver.find_element(By.XPATH, "//span[text()='Home']")
        print("Logged In Successfully!")
        return True
    except NoSuchElementException:
        print("!!! NOT Logged In !!!")
        return False


if __name__ == "__main__":
    # Set up ChromeDriver options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Set up ChromeDriver service
    service = Service(ChromeDriverManager().install())

    # Initialize the WebDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)

    credentials = load_credentials()

    if credentials is None:
        username, password = prompt_credentials()
    else:
        username, password = credentials

    # Find the element by xpath to check stories and scrape usernames
    home_url = "https://www.instagram.com/"
    notification_cancel = '//div[@role="dialog"]//button[.="Not Now"]'
    stories_xpath = "//div[@role='menu']//div[@role='presentation']/div[1]/ul/li[@class]//div[@dir='auto']/div[text()]"
    next_button_xpath = "//div[@role='menu']//div[@role='presentation']/following-sibling::button[@aria-label='Next']"

    login(driver, username, password)  # Assuming you have already logged in

    driver.get(home_url)
    time.sleep(2)

    # Click 'Not Now' if notification popup appears
    try:
        not_now_button = driver.find_element(By.XPATH, notification_cancel)
        not_now_button.click()
        time.sleep(2)
    except NoSuchElementException:
        pass  # If 'Not Now' button is not present, move on

    usernames = []

    while True:
        # Scrape usernames
        current_usernames = driver.find_elements(By.XPATH, stories_xpath)
        for username_element in current_usernames:
            usernames.append(username_element.text)

        # Click next button
        try:
            next_button = driver.find_element(By.XPATH, next_button_xpath)
            next_button.click()
            time.sleep(2)  # Adjust sleep time if needed
        except NoSuchElementException:
            print("No more next buttons found.")
            break  # Break the loop if no more next buttons are found

    # Save usernames to a text file
    with open("followers.txt", "w") as file:
        for username in usernames:
            file.write(username + "\n")

    print("Usernames saved to followers.txt file.")

    # Close the driver session
    driver.quit()
