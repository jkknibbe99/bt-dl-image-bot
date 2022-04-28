import os, sys, time, shutil
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import WebDriverException, NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException
from config import getDataValue, login_data, chromedriver_data

# Initialize globals
driver = None
actionChains = None
reaching_images = False
start_job_num = -1  # For testing purposes. Lets you start mid-way through the job-list TODO: Make sure it is set to > -1 for production

STATUS_LOG_FILEPATH = os.path.join(Path(os.path.dirname(__file__)).parent.absolute(), 'status_log.txt')
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
        chromedriver_path = (os.path.realpath(__file__)[::-1][(os.path.realpath(__file__)[::-1].find('\\')+1):])[::-1] + directory + 'chromedriver_' + str(getDataValue('chromedriver_data', 'version')) + '_win.exe'
    else:  # Mac
        chromedriver_path = (os.path.realpath(__file__)[::-1][(os.path.realpath(__file__)[::-1].find('/')+1):])[::-1] + chromedriver_data['directory'] + 'chromedriver_100_mac'
    # Declare chromedriver
    global driver
    chrome_options = None
    downloads_path = getDataValue('user_data', 'Downloads Directory') + '\\temp'
    if downloads_path is not None:
        chrome_options = webdriver.ChromeOptions()
        prefs = {'download.default_directory' : downloads_path}
        chrome_options.add_experimental_option('prefs', prefs)
    try:
        if chrome_options is None:
            driver = webdriver.Chrome(executable_path=chromedriver_path)
        else:
            # TODO: executable_path is depricated. Use service object (see info here: https://stackoverflow.com/questions/64717302/deprecationwarning-executable-path-has-been-deprecated-selenium-python)
            driver = webdriver.Chrome(executable_path=chromedriver_path,options=chrome_options)
    except WebDriverException as e:
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
    driver.find_element(By.XPATH, '//*[@id="username"]').send_keys(getDataValue('user_data', 'BuilderTrend Username'))  # Enter username
    driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(getDataValue('user_data', 'BuilderTrend Password'))  # Enter password
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
    except NoSuchElementException:  # If date input is not visible, try opening the filter options pane
        # Click to open Filter options
        filter_options = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'form.FilterContainer span.ant-collapse-arrow')))
        while True:
            try:
                driver.find_element(By.CSS_SELECTOR, 'div.loadingBackground')
            except NoSuchElementException:
                filter_options.click()
                break
        # Find the date input box
        date_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="8"]')))
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
        while True:
            try:
                driver.find_element(By.CSS_SELECTOR, 'div.loadingBackground')
            except NoSuchElementException:
                # Click Update Results button
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="reactDailyLogsListDiv"]/div/section/div[2]/form/div/div/div[2]/div/div[2]/button[1]/span'))).click()
                break


# Checks if dailyLogsExist on the current page
def dailyLogsExist(job_name: str):
    # Wait until new dailyLogs page loads
    driver.switch_to.default_content()
    itr = 0
    while True:
        dailyLogs_container = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@id="reactDailyLogsListDiv"]/div/section/div[@class="ListSection react"][3]')))    
        try:
            dailyLogs_container.find_element(By.XPATH, '//div[contains(@class, "BTLoading")]')        
            break
        except NoSuchElementException:
            pass
        clearTerminal()
        print('Waiting for loading div...')
        itr += 1
        if itr > 100:  # TODO: look into average number of iterations it takes to see the loading div. This will let me determine a more efficiant max itr
            break
    while True:
        dailyLogs_container = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@id="reactDailyLogsListDiv"]/div/section/div[@class="ListSection react"][3]')))    
        try:
            dailyLogs_container.find_element(By.XPATH, '//div[contains(@class, "BTLoading")]')        
        except NoSuchElementException:
            break
        clearTerminal()
        print('Loading Daily Logs...')
    print('Loading Complete\n', job_name, '\nAccessing Daily Logs...')
    # Check if there are any daily logs
    dailyLogs_container = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[@id="reactDailyLogsListDiv"]/div/section/div[@class="ListSection react"][3]')))
    try:
        dailyLogs_container.find_element(By.CSS_SELECTOR, 'div.EmptyState')
    except NoSuchElementException:
        return True
    else:
        return False


# On the current screen, downloads all images from daily logs
def downloadDailyLogsImages(max_imgs_per_dl):
    # Wait until daily logs load in
    driver.switch_to.default_content()
    driver.execute_script("window.scrollTo(0,0)")  # Scroll to top of page
    dailyLogs_container = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[@id="reactDailyLogsListDiv"]/div/section/div[@class="ListSection react"][3]')))
    dailyLog_qty_elem = WebDriverWait(dailyLogs_container, 10).until(EC.presence_of_element_located((By.XPATH, '//div/div/div/span/span[3]')))
    while True:
        try:
            dailyLog_qty_elem.click()
            break
        except ElementClickInterceptedException:
            pass
    num_dailyLogs = int(dailyLog_qty_elem.text)
    # Iterate through each daily log
    for i in range(num_dailyLogs):
        dailyLog_container = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "DailyLogListItem")][' + str(i+1) + ']')))
        try:
            bt_file_wrapper = WebDriverWait(dailyLog_container, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.bt-file-wrapper')))
        except NoSuchElementException:
            # Daily log has no images attached
            pass
        else:
            bt_file_wrapper_id = bt_file_wrapper.get_dom_attribute('id')  # Get the ID of the file wrapper element
            view_files_btn_xpath = '//*[@id="' + bt_file_wrapper_id + '"]/div/div/button[2]'  # Create Xpath to the view files button
            driver.switch_to.default_content()
            view_files_btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, view_files_btn_xpath)))
            while True:
                try:
                    actionChains.move_to_element(view_files_btn).click().perform()  # Click the view files button
                    break
                except ElementClickInterceptedException as e:
                    print(e)
            # Should now be within the Daily Log List Attachments Dialog box
            # Grab all the dialog boxes
            img_dialogs = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "bt-file-wrapper--dialog")]')))
            # Try to find the displayed dialog box
            # We need this because every time a view all attachments dialog box is opened, it creates the html code dynamically
            img_dialog = None
            if img_dialogs[-1].is_displayed():  # Check the last dialog box (typically this is the displayed one)
                img_dialog = img_dialogs[-1]
            else:  # Look through all dialog boxes
                for dialog in img_dialogs:
                    if dialog.is_displayed():
                        img_dialog = dialog
            if img_dialog is None:  # If active dialog box could not be found
                raise ValueError('Could not find the open image dialog box')
            # Grab list of all image containers
            img_containers = WebDriverWait(img_dialog, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.bt-file-viewer-grid--item')))
            actionChains.move_to_element(img_dialog.find_element(By.XPATH, '//div')).click().perform()  # Click the titlebar of the dialog box to make the pane active
            # Click on all image download buttons
            if isinstance(max_imgs_per_dl, int):
                if isinstance(img_containers, WebElement) and max_imgs_per_dl > 0:  # If only one image found
                    # Click single image download button
                    dnld_btn = WebDriverWait(img_containers, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.bt-file-viewer-grid--download')))
                    # TODO: have program check to see if image exists in the file already. If so, do not perform click.
                    actionChains.move_to_element(dnld_btn).click().perform()
                elif len(img_containers) > 0:  # If multiple images
                    num_to_download = len(img_containers) if len(img_containers) < max_imgs_per_dl else max_imgs_per_dl
                    for i in range(num_to_download):
                        # Click on each image's download button
                        img_container = img_containers[i]
                        dnld_btn = WebDriverWait(img_container, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.bt-file-viewer-grid--download')))
                        # TODO: have program check to see if image exists in the file already. If so, do not perform click.
                        actionChains.move_to_element(dnld_btn).click().perform()
                else:  # If unrecognized type returned
                    raise ValueError('The img_containers variable is of type ' + str(type(img_containers)) + '. This type cannot be handled by this program')
            # Click X to close out of the attachements dialog
            img_dialog_close = img_dialog.find_element(By.CSS_SELECTOR, 'button.ui-dialog-titlebar-close')
            img_dialog_close = WebDriverWait(driver, 10).until(EC.visibility_of(img_dialog_close))
            while img_dialog.is_displayed():
                actionChains.move_to_element(img_dialog_close).click().perform()
            # Confirm that images were reached
            global reaching_images
            reaching_images = True


# Download all the daily logs images
def downloadAllImages(number_of_days):
    # Create 'temp' folder for temporarily storing images
    createDir('temp')

    # Go to daily logs page
    driver.get('https://buildertrend.net/DailyLogs/DailyLogsList.aspx')

    # Find JobList div
    job_list = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "JobList")]')))

    # Get all JobListItem elements
    job_list_items = job_list.find_elements(By.CSS_SELECTOR, 'li.JobListItem:not(.AllJobs)')
    # Get all JobListItem job names
    job_names = []
    for job_list_item in job_list_items:
        job_name = job_list_item.find_element(By.CSS_SELECTOR, 'div.ItemRowJobName').text
        job_names.append(job_name)

    # Iterate through all JobListItems
    job_name_itr = 0
    for job_list_item in job_list_items:
        if job_name_itr > start_job_num:
            try:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(job_list_item)).click()
            except ElementClickInterceptedException:  # If job button not visible, scroll to it and click
                driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
                while True:
                    try:
                        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(job_list_item)).click()
                    except ElementClickInterceptedException:
                        pass
            except StaleElementReferenceException:  # If job button element is stale, attempt to refind it
                job_name = job_names[job_list_items.index(job_list_item)]
                job_list_item = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[text() = "' + job_name + '"]')))
            setFilter(number_of_days)  # Set the filter to day range
            if dailyLogsExist(job_names[job_name_itr]):
                downloadDailyLogsImages(max_imgs_per_dl=getDataValue('user_data', 'Qty Images Per Daily Log'))  # Download set number of images from all daily logs
                moveImgsToFolder(job_names[job_name_itr].replace('/','-').replace('?','_'))
                clearTempDir()
        job_name_itr += 1        


# Creates a folder for the given job in the specified download dest dir
def createDir(dir_name: str):
    dnlds_path = getDataValue('user_data', 'Downloads Directory')
    dir_name = dir_name.replace('/', '-')
    new_path = dnlds_path + '\\' + dir_name
    try:
        os.mkdir(new_path)
    except FileExistsError:
        pass
    return new_path


# Moves all images from temp into the given folder
def moveImgsToFolder(folder_name: str):
    dnlds_path = getDataValue('user_data', 'Downloads Directory')
    tmp_path = dnlds_path + '\\temp'
    imgs = os.listdir(tmp_path)
    if imgs:
        createDir(folder_name)
        for img in imgs:
            src = tmp_path + '\\' + img
            dst = dnlds_path + '\\' + folder_name
            try:
                shutil.move(src, dst)
            except shutil.Error as e:
                if str(e).find('already exists') > -1:
                    pass
                else:
                    raise e


# Delete the temp directory
def deleteTempDir():
    clearTempDir()
    try:
        os.rmdir(getDataValue('user_data', 'Downloads Directory') + '\\temp')  # Remove the temp directory
    except FileNotFoundError:
        pass  # No temp directory exists


# Removes all files from the temp directory
def clearTempDir():
    dnlds_path = getDataValue('user_data', 'Downloads Directory')
    tmp_path = dnlds_path + '\\temp'
    try:
        imgs = os.listdir(tmp_path)
    except FileNotFoundError:
        pass  # No temp directory exists
    else:
        # Remove all images
        for img in imgs:
            while True:
                # Wait for file to finish downloading
                try:
                    os.remove(tmp_path + '\\' + img)
                    break
                except PermissionError:
                    pass


# Checks if the given xpath is visible to the given driver
def check_exists(xpath, driver):
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True


# Clear terminal
def clearTerminal():
    os.system('cls' if os.name == 'nt' else 'clear')


def newStatus(message: str):
    message = message[:message.find('Backtrace:')] if message.find('Backtrace:') > -1 else message  # Remove Backtrace from error message
    with open(STATUS_LOG_FILEPATH, 'a') as f:
        f.write('\n' + str(message))


# Close chrome driver bot
def quit():
    deleteTempDir()
    clearTerminal()
    print('\n\nProgram Finished\n')
    driver.quit()


# Main method
if __name__ == '__main__':
    num_retries = 3  # This is the number of times the program will rerun if no images were downloaded
    itr = 0
    while not reaching_images:
        try:
            deleteTempDir()  # Just in case it still exists
            initDriver()
            initActionChains()
            login()
            downloadAllImages(7)
        except Exception as e:
            deleteTempDir()
            newStatus(str(e))
            raise e
        itr += 1
        if itr == num_retries:
            newStatus('ERROR: Could not download images after ' + num_retries + ' tries.')
            break
            # TODO: Sometimes, the site gets stuck on a loading page. Set an overall timeout for the program (say if it ran for more than 5 mins, quit)
    time.sleep(1)
    quit()