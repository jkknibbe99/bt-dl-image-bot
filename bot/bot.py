import selenium
from config import login_data, chromedriver_data
import time, os, sys
from config import getDataValue
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

# Initialize globals
driver = None
actionChains = None

FILTER_OPTIONS = {
    1 : 'Today',
    2 : 'Today & Yesterday',
    7 : 'Past 7 Days',
    14 : 'Past 14 Days',
    30 : 'Past 30 Days',
    45 : 'Past 45 Days',
    60 : 'Past 60 Days',
}


# Initialize chrome driver
def initDriver():
    # Get path to chromedriver
    if os.name == 'nt':  # Windows
        directory = chromedriver_data['directory'].replace('/', '\\')
        chromedriver_path = (os.path.realpath(__file__)[::-1][(os.path.realpath(__file__)[::-1].find('\\')+1):])[::-1] + directory + 'chromedriver_100_win.exe'
    else:  # Mac
        chromedriver_path = (os.path.realpath(__file__)[::-1][(os.path.realpath(__file__)[::-1].find('/')+1):])[::-1] + chromedriver_data['directory'] + 'chromedriver_100_mac'
    # Declare chromedriver
    global driver
    chrome_options = None
    downloads_path = getDataValue('init.json', 'downloads_path')
    if downloads_path is not None:
        chrome_options = webdriver.ChromeOptions()
        prefs = {'download.default_directory' : downloads_path}
        chrome_options.add_experimental_option('prefs', prefs)
    try:
        if chrome_options is None:
            driver = webdriver.Chrome(executable_path=chromedriver_path)
        else:
            driver = webdriver.Chrome(executable_path=chromedriver_path,options=chrome_options)
    except selenium.common.exceptions.WebDriverException as e:
        print(e)
        print('Current chromedriver_path =', chromedriver_path)
        sys.exit()


# Initialize actionChains. This is used to perform actions like scroling elements into view
def initActionChains():
    global actionChains
    actionChains = ActionChains(driver)


# Log into BuilderTrend
def login():
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


# Set filter for daily logs
def setFilter(num_days):
    # Go to daily logs page
    driver.get('https://buildertrend.net/DailyLogs/DailyLogsList.aspx')
    # Click to open Filter options
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="reactDailyLogsListDiv"]/div/section/div[2]/form/div/div/div[1]/div/div[1]/div/div/span'))).click()
    # Click on Date input box
    date_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="8"]')))
    # date_input.click()
    # Enter days to filter by
    if num_days not in FILTER_OPTIONS:
        msg = 'The parameter num_days entered (' + num_days + ') is not valid. Please enter one of the following: '
        for key in FILTER_OPTIONS:
            msg += key + ', '
        msg = msg[:-2]  # Remove the final comma and space
        raise ValueError(msg)
    else:
        date_input.send_keys(FILTER_OPTIONS[num_days])
        date_input.send_keys(Keys.ENTER)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="reactDailyLogsListDiv"]/div/section/div[2]/form/div/div/div[2]/div/div[2]/button[1]/span'))).click()


# Download the daily logs images
def downloadImages():
    # Find JobList div
    job_list = driver.find_element(By.XPATH, '//div[contains(@class, "JobList")]')

    # TODO: scroll to bottom of the JobList so that all jobs list items are visible

    # Get all JobListItem elements
    job_list_items = job_list.find_elements(By.CSS_SELECTOR, 'li.JobListItem:not(.AllJobs)')

    # Iterate through all JobListItems
    for job_list_item in job_list_items:
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(job_list_item)).click()
        except selenium.common.exceptions.ElementClickInterceptedException:
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(job_list_item)).click()
        
    

    # Set # items per page to 20 for testing purposes

    # TODO: Need to see what pages are needed or if any specific filter needs to be set up
    # WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#DailyLogPagingTop'))).send_keys('20' + Keys.ENTER)


    # For each daily log, go into 'View All Attachments' pane
    dailyLogs = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.DailyLogListItem')))
    for log in dailyLogs:
        # bt_file_wrapper = log.find_element(By.XPATH, "//div[contains(concat(' ', @class, ' '), ' bt-file-wrapper ')]")  # Find the file wrapper element
        bt_file_wrapper = log.find_element(By.XPATH, '//div[contains(@class, "bt-file-wrapper")]')  # Find the file wrapper element
        bt_file_wrapper_id = bt_file_wrapper.get_dom_attribute('id')  # Get the ID of the file wrapper element
        view_files_btn_xpath = '//*[@id="' + bt_file_wrapper_id + '"]/div/div/button[2]'  # Create Xpath to the view files button
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, view_files_btn_xpath))).click()  # Click the view files button
        # TODO: remove \/
        time.sleep(2)
        # Should now be within the Daily Log List Attachments Dialog box
        # Find the dialog box
        # Grab all the dialog boxes
        img_dialogs = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "bt-file-wrapper--dialog")]')))
        # Grab the last dialog box found (This is the most recently opened one)
        img_dialog = img_dialogs[len(img_dialogs)-1]  # Need this because everytime a view all attachments dialog box is opened, it creates the html code dynamically
        img_containers = img_dialog.find_element(By.XPATH, '//div[contains(@class, "bt-file-wrapper")]/div/div/bt-file-viewer/div/div/bt-file-viewer-grid/div/div/div[contains(@class, "bt-file-viewer-grid--item")]')
        for img_container in img_containers:
            pass
        


    # Click on all image download buttons

    # thumbnails = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.bt-file-viewer--thumbnail-wrapper')))
    # for tn in thumbnails:
    #     tn_id = tn.get_dom_attribute('id')  # Thumbnail id
    #     dnload_btn_xpath = '//div[@id="' + tn_id + '"]/a[2]'  # download button xpath
    #     dnload_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, dnload_btn_xpath)))  # download button element
    #     actionChains.move_to_element(dnload_btn).perform()  # scroll to the download button
    #     dnload_btn.click()


# Checks if the given xpath is visible to the given driver
def check_exists(xpath, driver):
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True


# Close chrome driver bot
def quit():
    os.system('cls' if os.name == 'nt' else 'clear')
    print('\n\nProgram Finished\n')
    driver.quit()


# Main method
if __name__ == '__main__':
    initDriver()
    initActionChains()
    login()
    setFilter(7)
    downloadImages()
    time.sleep(5)
    quit()