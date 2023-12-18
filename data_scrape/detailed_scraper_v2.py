from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
import time
import os

# Setup download directory
download_dir = r"C:\Users\Lukas Svendsen\Desktop\visualisering\data_detailed"
os.makedirs(download_dir, exist_ok=True)

# Setting Chrome options
chrome_options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=chrome_options)
driver.get("https://fauna.au.dk/jagt-og-vildtforvaltning/vildtudbytte/vildtudbytte-med-detaljer")

try:
    # Wait for the cookie consent button to be clickable and click it
    cookie_accept_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="cookiescript_accept"]'))
    )
    cookie_accept_button.click()
    time.sleep(5)
    
    dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="react-select-2-input"]'))
    )
    time.sleep(2)
    dropdown.click()
    
    time.sleep(2)

    
    # Example of locating and clicking an option
    # The XPath here is just an example and will likely need to be tailored to the specific site
    option_xpath = '/html/body/div[3]/div/div/div[1]/div[2]/div/div/div[1]/div'
    option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'react-select-2-listbox'))
    )
    option.click()

    
finally: 
    driver.quit()
    
