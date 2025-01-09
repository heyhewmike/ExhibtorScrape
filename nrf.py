#!/bin/python3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time, platform, logging, os, sys, re

# Testing OS to use proper Gecko Driver
testingOS = platform.system()
testingPC = platform.node()
localPath = os.getcwd()

if testingOS == "Windows":
    gecko_path = "./geckodriver.exe"
elif testingOS == "Linux":
    gecko_path = "./geckodriver"
else:
    gecko_path = "./geckodriver.exe"

# Generating Timestamps
timestamp = time.strftime("%Y%m%d-%H%M")
year = time.strftime("%Y")

page = 0 # creating page variable

# Generating the logging & screenshot folder & file
logging_fold = "nrf_"+str(timestamp)
logFldr = os.path.join(logging_fold)
os.makedirs(logFldr, exist_ok=True)
logFilename = os.path.join(logFldr, "NRF_Results.log")
logging.basicConfig(filename=str(logFilename), level=logging.INFO)

logging.info(f"Testing OS: {testingOS}")
logging.info(f"Testing PC: {testingPC}")
logging.info(f"Test run performed: {timestamp}")

#### Firefox Setup
from selenium.webdriver.firefox.options import Options
options = Options()


# Initialize the WebDriver
driver = webdriver.Firefox(options=options)  # Use GeckoDriver
driver.set_window_size(1920, 1080)
wait = WebDriverWait(driver, 10) # Sets the length of time for the dynamic wait to max out at. Typically 10 is enough

# URL of the NRF (nat retail fed) exhibitor directory
start_url = "https://nrfbigshow2025.smallworldlabs.com/exhibitors"  # Update this to the new URL
driver.get(start_url)
logging.info("Browser launched")

# Data storage for the csv xlsx
data = []

# Function to extract text and href for Booth
def get_booth_info(element, selector, by=By.XPATH):
    try:
        booth_element = element.find_element(by, selector)
        booth_text = booth_element.text.strip() # Gets the text from the booth info and strips anything around it so that it is text only
        booth_href = booth_element.get_attribute("href") # Gets the URL from the href in the html
        logging.info("Got Booth number and URL")
        return {"text": booth_text, "href": booth_href}
    except:
        logging.info("Found no booth info")
        return {"text": "None Available", "href": "None Available"}

# Function to get sibling text based on Parent-Sibling logic
def safe_get_sibling_text(driver, parent_text, sibling_class="profileResponse"):
    try:
        # Locate the parent div based on its label text
        parent = driver.find_element(By.XPATH, f"//div[contains(@class, 'text-secondary') and contains(text(), '{parent_text}')]/../..") # Locates the Child Field (Company/Founded/Website/...) on the page and then locates the description by navigating up 2 levels and back down
        
        # Locate the sibling with the specified class
        logging.info(f"Getting sibling info for {parent_text}")
        return parent.find_element(By.CLASS_NAME, sibling_class).text.strip()
    except Exception as e:
        logging.error(f"Failed to get sibling info for {parent_text}: {e}")
        return "None Available"

# Setting variable to 1 for the first page
page+=1

while True:
    # Locate all "Explore" buttons on the page
    explore_buttons = driver.find_elements(By.XPATH, "//button[contains(@class, 'btn') and contains(., 'Explore')]")
    logging.info("Located all Explore buttons")
    for i in range(len(explore_buttons)):
        try:
            # Re-fetch all "Explore" buttons to avoid stale element issues
            explore_buttons = driver.find_elements(By.XPATH, "//button[contains(@class, 'btn') and contains(., 'Explore')]")
            
            # Click the "Explore" button at index i
            explore_buttons[i].click()
            logging.info("Clicked on Explore button")

            wait.until(EC.visibility_of_element_located(("xpath", '/html/body/div[4]/div[2]/div[1]/div[2]/div/div/div[5]/div[2]/div[1]/div/div/span/a'))) # Booth Link or try inside the curly bracket instead of the html path{ ".//a[contains(@class, 'generic-option-link')]" }
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") # Scroll to the bottom of the page
            time.sleep(2)
            # Extract details
            logging.info("Calling booth info")
            booth = get_booth_info(driver, ".//a[contains(@class, 'generic-option-link')]", by=By.XPATH) # Updated and dynamic XPath
            
            # Use Parent-Sibling logic for these fields
            logging.info("Calling Company Details")
            company = safe_get_sibling_text(driver, "Name")
            what_we_do = safe_get_sibling_text(driver, "What We Do")
            founded = safe_get_sibling_text(driver, "Founded")
            website = safe_get_sibling_text(driver, "Website")
            categories = safe_get_sibling_text(driver, "Categories")
            sani_company = re.sub(r',', "", company) # Removes commas from the company name to prepare for file names
            sani_comp = re.sub(r'[\\/*?:"<>| ]', "_", sani_company).rstrip("_") # Replaces all listed special charaters with an underscore and strips any trailing underscore
            screenshot_name = f'Page_{page}_Company_{sani_comp}_{booth["text"]}.png' # Generates screenshot name
            screenshot_path = os.path.join(logFldr, str(screenshot_name)) # Generates Screenshot file path
            driver.save_screenshot(screenshot_path) # Takes screenshot
            screensave = os.path.join(localPath, screenshot_path) # Not presently used
            # Logs the data to the logging file Just in Case
            logging.info(f"""

*&#
Exhibitor Page: {page}
Company: {company}
Booth #: {booth["text"]}
Booth URL: {booth["href"]}
What We Do: {what_we_do}
Founded: {founded}
Website: {website}
Categories: {categories}
Screenshot: {screenshot_path}
#&*
""")
            
            # Store the data
            data.append({
                "Exhibitor Page": page,
                "Company": company,
                "Booth Text": booth["text"],
                "Booth Link": booth["href"],
                "What We Do": what_we_do,
                "Founded": founded,
                "Website": website,
                "Categories": categories,
                "Screenshot": screenshot_path
            })
            
            # Go back to the exhibitors page
            logging.info("Clicking Back")
            driver.back() # Uses browser back functionality
            if page>=2:
                wait.until_not(EC.visibility_of_element_located(("xpath", "//a[contains(@class, 'fa-spinner')]"))) # Spinner to move forward to current page
                logging.info("Spinner is now gone")
                logging.info(f"Page value is: {page}")
                time.sleep(2)
                # Re-fetch all "Explore" buttons to avoid stale element issues. This is helping on the moving forward to next exhibitor
                explore_buttons = driver.find_elements(By.XPATH, "//button[contains(@class, 'btn') and contains(., 'Explore')]")
                try:
                    active_page_element = driver.find_element(By.XPATH, "//div[contains(@class, 'pager-pages')]/span[contains(@class, 'pager-num') and not(@href)]") # Pulls paginator page number
                    active_page = active_page_element.text.strip() # Cleans it up to have just the number
                    if int(active_page) == page: # Compares active page to my variable
                        logging.info(f"Confirmed on the correct page: {active_page}")
                    else:
                        logging.error(f"Expected to be on page {page}, but found on page {active_page}")
                        sys.exit(1)  # Exit the script with an error status
                except Exception as e:
                    logging.error(f"Failed to verify active page: {e}")
                    logging.info("Exiting script due to error in page verification.")
                    sys.exit(1)  # Exit the script with an error status
                logging.info("Spinner to return to current page done")
            logging.info("Waiting for progress paginator bar to disappear")
            wait.until_not(EC.visibility_of_element_located(("xpath", "//a[contains(@class, 'paginator-overlay')]"))) # .paginator-overlay
        except Exception as e:
            print(f"Error processing card at index {i}: {e}")
            driver.back()
            time.sleep(2)
    
    # Try to go to the next page, if available
    try:
        # Screenshot generation for moving forward --- These aid in troubleshooting
        errstamp = time.strftime("%Y%m%d-%H%M")
        screenshot_name = f"Next_Page-1_{errstamp}.png"
        screenshot_path = os.path.join(logFldr, str(screenshot_name))
        driver.save_screenshot(screenshot_path)
        next_button = driver.find_element(By.XPATH, "//a[contains(@class, 'pager-right-next')]") # Sets the method to locate the 1 page next button
        logging.info("Set next_button")
        next_button.click() # Clicks the Next 1 page button
        logging.info("Clicked next_button")
        time.sleep(1)
        wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'btn') and contains(., 'Explore')]"))) # Waits until it can find an "Explore" button or 10 seconds to pass which ever comes first
        logging.info("Next page loaded")
        # Screenshot generation for moving forward --- These aid in troubleshooting
        screenshot_name = f"Next_Page-2_{errstamp}.png"
        screenshot_path = os.path.join(logFldr, str(screenshot_name))
        driver.save_screenshot(screenshot_path)
        page+=1 # Adds 1 to the variable for page tracking varification and spinner logic
    except:
        print("No more pages.")
        break

# Close the driver
driver.quit()

# Save data to CSV and Excel
df = pd.DataFrame(data) # Saves data to variable for writing to files
df.to_csv(os.path.join(logFldr, f"NRF-exhibitors_{year}.csv"), index=False) # Writes to CSV File
df.to_excel(os.path.join(logFldr, f"NRF-exhibitors_{year}.xlsx"), index=False) # Writes to XLSX
logging.info(f"Data scraping completed and saved to NRF-exhibitors_{year}.csv and NRF-exhibitors_{year}.xlsx.")
print(f"Data scraping completed and saved to NRF-exhibitors_{year}.csv and NRF-exhibitors_{year}.xlsx.")
