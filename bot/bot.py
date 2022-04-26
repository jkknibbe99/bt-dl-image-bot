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
first_job = True  # This is used by the downloadImages() function to know 

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
    driver.switch_to.default_content()
    # Find the date input box
    try:
        # date_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="8"]')))
        date_input = driver.find_element(By.XPATH, '//*[@id="8"]')
    except selenium.common.exceptions.NoSuchElementException:  # If date input is not visible, try opening the filter options pane
        # Click to open Filter options
        filter_options = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'form.FilterContainer span.ant-collapse-arrow')))
        while True:
            try:
                driver.find_element(By.CSS_SELECTOR, 'div.loadingBackground')
            except selenium.common.exceptions.NoSuchElementException:
                filter_options.click()
                break
        # Find the date input box
        date_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="8"]')))
    # Find the current date filter value
    curr_date_input = date_input.find_element(By.XPATH, '../../span[2]').text
    # If desired filter is already set, do nothing, else, set filter
    if curr_date_input == 'Past ' + str(num_days) + ' Days':
        pass
    else:
        # Enter days to filter by
        if num_days not in FILTER_OPTIONS:
            msg = 'The parameter num_days entered (' + num_days + ') is not valid. Please enter one of the following: '
            for key in FILTER_OPTIONS:
                msg += key + ', '
            msg = msg[:-2]  # Remove the final comma and space
            raise ValueError(msg)
        date_input.send_keys(FILTER_OPTIONS[num_days])
        date_input.send_keys(Keys.ENTER)
        # Check that loading background does not exist
        while true:
            try:
                driver.find_element(By.CSS_SELECTOR, 'div.loadingBackground')
            except selenium.common.exceptions.NoSuchElementException:
                # Click Update Results button
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="reactDailyLogsListDiv"]/div/section/div[2]/form/div/div/div[2]/div/div[2]/button[1]/span'))).click()
                break


# Check if daily logs are present on the webpage
def dailyLogsPresent():
    driver.switch_to.default_content()
    try:
        driver.find_element(By.CSS_SELECTOR, 'div.DailyLogListItem')
    except selenium.common.exceptions.NoSuchElementException:
        return False
    else:
        return True


# On the current screen, downloads all images from daily logs
def downloadDailyLogsImages():
    driver.switch_to.default_content()
    num_dailyLogs = len(WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.DailyLogListItem'))))
    for i in range(num_dailyLogs):
        dailyLog_container = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "DailyLogListItem")][' + str(i+1) + ']')))
        try:
            # bt_file_wrapper = log.find_element(By.CSS_SELECTOR, 'div.bt-file-wrapper')
            bt_file_wrapper = WebDriverWait(dailyLog_container, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.bt-file-wrapper')))
        except selenium.common.exceptions.NoSuchElementException:
            # Daily log has no images attached
            pass
        else:
            bt_file_wrapper_id = bt_file_wrapper.get_dom_attribute('id')  # Get the ID of the file wrapper element
            view_files_btn_xpath = '//*[@id="' + bt_file_wrapper_id + '"]/div/div/button[2]'  # Create Xpath to the view files button
            driver.switch_to.default_content()
            view_files_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, view_files_btn_xpath)))
            while True:
                try:
                    actionChains.move_to_element(view_files_btn).click().perform()  # Click the view files button
                    break
                except selenium.common.exceptions.ElementClickInterceptedException as e:
                    print(e)
            # Should now be within the Daily Log List Attachments Dialog box
            # Find the dialog box
            # Grab all the dialog boxes
            img_dialogs = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "bt-file-wrapper--dialog")]')))
            # Try accessing the first or last dialog box found (Typically these are the most recently opened ones)
            # Need this because every time a view all attachments dialog box is opened, it creates the html code dynamically
            img_dialog_search_time = 0.5 # Seconds
            try: #Try last dialog box
                img_dialog = WebDriverWait(driver, img_dialog_search_time).until(EC.visibility_of(img_dialogs[-1]))
            except selenium.common.exceptions.TimeoutException:
                try:  # Try first dialog box
                    img_dialog = WebDriverWait(driver, img_dialog_search_time).until(EC.visibility_of(img_dialogs[0]))
                except selenium.common.exceptions.TimeoutException:
                    # Look through all dialog boxes
                    db_found = False
                    for dialog_box in img_dialogs:
                        try:
                            img_dialog = WebDriverWait(driver, img_dialog_search_time).until(EC.visibility_of(dialog_box))
                            db_found = True
                            break
                        except selenium.common.exceptions.TimeoutException:
                            pass
                    if not db_found:
                        raise ValueError('Could not find the open image dialog box')
            # Grab list of all image containers
            img_containers = WebDriverWait(img_dialog, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.bt-file-viewer-grid--item')))
            # Click on all image download buttons
            if isinstance(img_containers, selenium.webdriver.remote.webelement.WebElement):  # If only one image found
                # Click single image download button
                dnld_btn = WebDriverWait(img_containers, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.bt-file-viewer-grid--download')))
                actionChains.move_to_element(dnld_btn).click().perform()
            elif len(img_containers) > 0:  # If multiple images
                for img_container in img_containers:
                    # Click on each image's download button
                    dnld_btn = WebDriverWait(img_container, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.bt-file-viewer-grid--download')))
                    actionChains.move_to_element(dnld_btn).click().perform()
            else:  # If unrecognized type returned
                raise ValueError('The img_containers variable is of type ' + str(type(img_containers)) + '. This type cannot be handled by this program')
            # Click X to close out of the attachements dialog
            img_dialog_close = img_dialog.find_element(By.CSS_SELECTOR, 'button.ui-dialog-titlebar-close')
            img_dialog_close = WebDriverWait(driver, 10).until(EC.visibility_of(img_dialog_close))
            actionChains.move_to_element(img_dialog_close).click().perform()


# Download the daily logs images
def downloadAllImages(number_of_days):
    # Go to daily logs page
    driver.get('https://buildertrend.net/DailyLogs/DailyLogsList.aspx')

    # Find JobList div
    job_list = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "JobList")]')))

    # TODO: scroll to bottom of the JobList so that all jobs list items are visible

    # Get all JobListItem elements
    job_list_items = job_list.find_elements(By.CSS_SELECTOR, 'li.JobListItem:not(.AllJobs)')
    # Get all JobListItem job names
    job_names = []
    for job_list_item in job_list_items:
        job_name = job_list_item.find_element(By.CSS_SELECTOR, 'div.ItemRowJobName').text
        job_names.append(job_name)

    # Iterate through all JobListItems
    i = 0  # TODO: Remove after dev
    for job_list_item in job_list_items:
        print(job_names[i])  # TODO: Remove after dev
        
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(job_list_item)).click()
        except selenium.common.exceptions.ElementClickInterceptedException:  # If job button not visible, scroll to it and click
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(job_list_item)).click()
        except selenium.common.exceptions.StaleElementReferenceException:  # If job button element is stale, attempt to refind it
            job_name = job_names[job_list_items.index(job_list_item)]
            job_list_item = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[text() = "' + job_name + '"]')))

        time.sleep(1)  # TODO: This is a pause to let the daily logs load, look into other ways to confirm that new daily logs have loaded in
        setFilter(number_of_days)  # Set the filter to day range
        if dailyLogsPresent():
            downloadDailyLogsImages()  # Download all images from all daily logs


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
    downloadAllImages(7)
    time.sleep(5)
    quit()