import os
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

# Setup Chrome driver with specific capabilities
options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-notifications")

# Initialize a new Chrome instance with the Chrome driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
time.sleep(60)
login_url = "https://www.facebook.com"

# Open the login page
driver.get(login_url)
time.sleep(30)

# Find and click the "Decline optional cookies" button if present
try:
    decline_cookies_button = driver.find_element(By.XPATH, "//span[contains(text(), 'Decline optional cookies')]")
    decline_cookies_button.click()
    print("Clicked on 'Decline optional cookies' button.")
except NoSuchElementException:
    print("No 'Decline optional cookies' button found.")

time.sleep(5)

# Wait for the email or username input field to become visible and interactable
print("Entering Username and Password")
wait = WebDriverWait(driver, 10)
username_field = wait.until(EC.visibility_of_element_located((By.ID, 'email')))

# Enter your username
username_field.send_keys("developer@volcano.nu")

# Find the password input field and enter your password
password_field = driver.find_element(By.ID, 'pass')
password_field.send_keys("A0LCM-5:9VJa,n6+")  # Replace "your_password" with your actual password
# Submit the login form
password_field.send_keys(Keys.RETURN)

time.sleep(10)
print("Signed in now")
base_path = "/Users/developer/Downloads/facebook/"

text_file_path = os.path.join(base_path, "targets.txt")

# Read the group names from the text file
with open(text_file_path, 'r') as file:
    group_names_text = file.read().splitlines()

# Iterate over each group name
for group_name in group_names_text:
    try:
        # Construct the group URL
        group_url = f"https://www.facebook.com/groups/{group_name}/events"

        # Open the group URL
        driver.get(group_url)
        print(f"Opening group: {group_url}")

        time.sleep(30)

        # Scroll down to load more articles
        driver.execute_script("window.scrollBy(0, 350)")
        time.sleep(2)

        # Initialize lists to store data
        events = []
        time_values = []
        links = []

        start_time = time.time()  # Start the timer

        while True:
            articles = driver.find_elements(By.XPATH, "//div[contains(@class,'x14vqqas x1nb4dca')]")
            for article in articles:
                try:
                    event_element = article.find_element(By.XPATH, ".//a/span")
                    event = event_element.text.strip()
                    events.append(event)

                    time_element = article.find_element(By.XPATH, ".//div[@class='xzueoph x1k70j0n']//span")
                    time_value = time_element.text.strip()
                    time_values.append(time_value)

                    link_element = article.find_element(By.XPATH, ".//a")
                    link = link_element.get_attribute("href")
                    links.append(link)
                except NoSuchElementException:
                    print("Some elements not found, skipping...")

            # Check if 10 minutes have passed
            if time.time() - start_time > 10:
                # Create a DataFrame
                df = pd.DataFrame({
                    'Event': events,
                    'Time Value': time_values,
                    'Link': links
                })

                df.drop_duplicates(inplace=True)

                # Define the path for the CSV file with the group name
                csv_file_path = os.path.join(base_path, f"{group_name}_partial.csv")

                # Save the DataFrame to a CSV file
                df.to_csv(csv_file_path, index=False)
                print(f"CSV file '{group_name}_partial.csv' saved successfully.")

                # Reset the lists and timer
                events = []
                time_values = []
                links = []
                start_time = time.time()

            # Scroll down to load more articles
            driver.execute_script("window.scrollBy(0, 100)")
            time.sleep(2)

            try:
                see_more_button = driver.find_element(By.XPATH, "//span[text()='See More']")
                see_more_button.click()
            except NoSuchElementException:
                print("No 'See More' button found or reached the end of the list.")
                break  # Exit the loop if there's no more "See More" button or reached the end of the list

        # Create a DataFrame from the remaining data after the loop
        df = pd.DataFrame({
            'Events': events,
            'Time Value': time_values,
            'Link': links
        })

        df.drop_duplicates(inplace=True)

        # Define the path for the CSV file with the group name
        csv_file_path = os.path.join(base_path, f"{group_name}.csv")

        # Save the remaining data to a CSV file
        df.to_csv(csv_file_path, index=False)
        print(f"CSV file '{group_name}.csv' saved successfully.")

    except WebDriverException as e:
        print(f"Error occurred: {e}")
        print("Saving collected data to CSV file...")
        df = pd.DataFrame({
            'Events': events,
            'Time Value': time_values,
            'Link': links
        })
        df.drop_duplicates(inplace=True)
        csv_file_path = os.path.join(base_path, f"{group_name}.csv")
        df.to_csv(csv_file_path, index=False)
        print(f"Partial CSV file '{group_name}.csv' saved successfully.")

# Close the browser
driver.quit()
