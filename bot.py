from config import login_data, chromedriver_data
import time, os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

def initDriver():
    # Get path to chromedriver
    if os.name == 'nt':  # Windows
        directory = chromedriver_data['directory'].replace('/', '\\')
        chromedriver_path = (os.path.realpath(__file__)[::-1][(os.path.realpath(__file__)[::-1].find('\\')+1):])[::-1] + directory + 'chromedriver_100_win.exe'
    else:  # Mac
        chromedriver_path = (os.path.realpath(__file__)[::-1][(os.path.realpath(__file__)[::-1].find('/')+1):])[::-1] + chromedriver_data['directory'] + 'chromedriver_100_mac'

    # Declare chromedriver
    chrome_options = webdriver.ChromeOptions()
    prefs = {'download.default_directory' : '/path/to/dir'}
    chrome_options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(executable_path=chromedriver_path,chrome_options=chrome_options)
    return driver


# Initialize actionChains. This is used to perform actions like scroling elements into view
def initActionChains(driver):
    actions = ActionChains(driver)
    return actions


# Log into BuilderTrend
def login(login_data, driver):
    # Go to the login url
    driver.get(login_data['login_url'])

    # Log in
    driver.find_element(By.XPATH, '//*[@id="username"]').send_keys(login_data['username'])  # Enter username
    driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(login_data['password'])  # Enter password
    driver.find_element(By.XPATH, '//*[@id="reactLoginListDiv"]/div/div/div/div/div[3]/div/div/div/form/button').click()  # Click login button

    # Wait for main dashboard to load in
    for i in range(10):
        time.sleep(1)
        if check_exists('//*[@id="reactMainNavigation"]/div[1]/div/ul/li[2]', driver):
            break

# Download the daily logs images
def downloadImages(driver, actionChains):
    # Go to daily logs page
    driver.get('https://buildertrend.net/DailyLogs/DailyLogsList.aspx')

    # Select all listed jobs
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="reactJobPicker"]/div/div[2]/div/div/div[1]/div/div/li[1]/div/div'))).click()

    # Set # items per page to 20 for testing purposes
    # TODO: Need to see what pages are needed or if any specific filter needs to be set up
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#DailyLogPagingTop'))).send_keys('20' + Keys.ENTER)


    # Go into 'View All Attachments' pane

    # dailyLogs = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.DailyLogListItem')))
    # for log in dailyLogs:
        # bt_file_wrapper = log.find_element_by_xpath("//div[contains(concat(' ', @class, ' '), ' bt-file-wrapper ')]")  # Find the file wrapper element
        # bt_file_wrapper_id = bt_file_wrapper.get_dom_attribute('id')  # Get the ID of the file wrapper element
        # view_files_btn_xpath = '//*[@id="' + bt_file_wrapper_id + '"]/div/div/button[2]'  # Create Xpath to the view files button
        # WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, view_files_btn_xpath))).click()  # Click the view files button
        # driver.implicitly_wait(3)


    # Click on all image download buttons
    thumbnails = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.bt-file-viewer--thumbnail-wrapper')))
    for tn in thumbnails:
        tn_id = tn.get_dom_attribute('id')  # Thumbnail id
        dnload_btn_xpath = '//div[@id="' + tn_id + '"]/a[2]'  # download button xpath
        dnload_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, dnload_btn_xpath)))  # download button element
        actionChains.move_to_element(dnload_btn).perform()  # scroll to the download button
        dnload_btn.click()

    # Close chrome
    driver.quit()


# Checks if the given xpath is visible to the given driver
def check_exists(xpath, driver):
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True


# Main method
if __name__ == '__main__':
    driver = initDriver()
    actionChains = initActionChains(driver)
    login(login_data, driver)
    downloadImages(driver, actionChains)