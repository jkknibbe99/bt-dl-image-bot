import os, sys, time, shutil
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import WebDriverException, NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException, TimeoutException, ElementNotInteractableException
from win32com.client import Dispatch
from config import getDataValue, login_data, chromedriver_data
from bot_status import newStatus
from chromedrivers.install_latest_chromedriver import installLatestChromedriver
import chromedriver_autoinstaller

# Actions
raise_error = False  #Production: False
pause_on_error = False  # Production: False
send_emails = True  # Production: True

# Initialize globals
driver = None
chrome_version = None
chrome_options = None
actionChains = None
reaching_images = False
start_job_num = -1  # For testing purposes. Lets you start mid-way through the job-list TODO: Make sure it is set to < 0 for production

# Browser to be used
BROWSER = 'Chrome'  # Options: 'Chrome', 'Undetected Chrome'

use_chromedriver_autoinstaller = True

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

# Find the current chrome version
def get_version_via_com(filename):
    parser = Dispatch("Scripting.FileSystemObject")
    try:
        version = parser.GetFileVersion(filename)
    except Exception:
        return None
    return version


# Set the chrome version global
def set_chrome_version_global():
    paths = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
             r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
             r"C:\Users\jordan\AppData\Local\Google\Chrome\Application\chrome.exe"]
    version = list(filter(None, [get_version_via_com(p) for p in paths]))[0]
    version = version[:version.find('.')]  # Grab just the first number
    # Set to global
    global chrome_version
    chrome_version = version


# Sets the path to download images to
def setDownloadsPath():
    downloads_path = getDataValue('user_data', 'Downloads Directory') + '\\temp'
    if downloads_path is not None:
        global chrome_options
        chrome_options = webdriver.ChromeOptions()
        prefs = {'download.default_directory' : downloads_path}
        chrome_options.add_experimental_option('prefs', prefs)


# Initialize chrome driver
def initDriver():
    # Declare driver
    global driver
    # Get latest chromedriver
    if use_chromedriver_autoinstaller:
        chromedriver_autoinstaller.install()    # Check if the current version of chromedriver exists
                                                # and if it doesn't exist, download it automatically,
                                                # then add chromedriver to path
        if BROWSER == 'Undetected Chrome':
            #Removes navigator.webdriver flag to allow fully undetected
            option = webdriver.ChromeOptions()
            option.add_argument('--disable-blink-features=AutomationControlled')
            #Open Browser
            driver = webdriver.Chrome(options=option)
        else:
            if chrome_options is None:
                driver = webdriver.Chrome()
            else:
                driver = webdriver.Chrome(options=chrome_options)
    else:
        # Download and install latest chromedriver
        installLatestChromedriver()
        # Try identified version
        set_chrome_version_global()
        directory = chromedriver_data['directory'].replace('/', '\\')
        chromedriver_path = (os.path.realpath(__file__)[::-1][(os.path.realpath(__file__)[::-1].find('\\')+1):])[::-1] + directory + 'chromedriver_' + str(chrome_version) + '_win.exe'
        try:
            driver = webdriver.Chrome(executable_path=chromedriver_path)
        except WebDriverException:
            # Try latest chromedriver
            latest = 0
            for filename in os.listdir('chromedrivers'):
                if filename.startswith('chromedriver_'): 
                    if int(filename[13:16]) > latest: latest = int(filename[13:16])
            chromedriver_path = (os.path.realpath(__file__)[::-1][(os.path.realpath(__file__)[::-1].find('\\')+1):])[::-1] + directory + 'chromedriver_' + str(latest) + '_win.exe'
            try:
                if chrome_options is None:
                    driver = webdriver.Chrome(executable_path=chromedriver_path)
                else:
                    driver = webdriver.Chrome(executable_path=chromedriver_path,options=chrome_options)
            except WebDriverException:
                raise ValueError('Could not open chrome with given chromedriver.\nChrome version: ' + str(latest) + '\nChromeDriver path: ' + chromedriver_path)
    driver.maximize_window()


# Initialize actionChains. This is used to perform actions like scroling elements into view
def initActionChains():
    global actionChains
    actionChains = ActionChains(driver)


# Log into BuilderTrend
def login():
    # Go to the login url
    driver.get(login_data['login_url'])
    
    # Log in
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#username'))).send_keys(getDataValue('user_data', 'BuilderTrend Username'))  # Enter username  TODO: Check for invalid username
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#password'))).send_keys(getDataValue('user_data', 'BuilderTrend Password'))  # Enter password  TODO: Check for invalid password
    # Click login button
    login_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#reactLoginListDiv button.Login-Form-SubmitButton')))
    actionChains.move_to_element(login_btn).click().perform()

    # Wait for main dashboard to load in
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#reactMainNavigation')))


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
                actionChains.move_to_element(job_list_item).perform()  # Scroll to job button
            except Exception as e:
                pass
            try:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(job_list_item)).click()
            except ElementClickInterceptedException:  # If job button not visible, scroll to it and click
                while True:
                    try:
                        driver.execute_script("arguments[0].scrollIntoView();", job_list_item)
                        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(job_list_item)).click()
                        break
                    except ElementClickInterceptedException:
                        pass
            except StaleElementReferenceException:  # If job button element is stale, attempt to refind it
                job_name = job_names[job_list_items.index(job_list_item)]
                job_list_item = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[text() = "' + job_name + '"]')))
            except Exception:
                continue
            setFilter(number_of_days)  # Set the filter to day range
            try:
                WebDriverWait(driver, 0.5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.BTLoading')))  # Look for loading div
            except TimeoutException:
                pass
            WebDriverWait(driver, 5).until_not(EC.presence_of_element_located((By.CSS_SELECTOR, '.BTLoading')))  # Wait for loading div to hide
            if dailyLogsExist(job_names[job_name_itr]):
                job_folder_name = job_names[job_name_itr].replace('/','-').replace('?','_') 
                downloadDailyLogsImages(max_imgs_per_dl=getDataValue('user_data', 'Qty Images Per Daily Log'), job_folder_name=job_folder_name)  # Download set number of images from all daily logs
                # Tries moving images multiple times (waiting for the images to finish downloading)
                move_imgs_tries = 10
                try_count = 0
                while True:
                    try:
                        moveImgsToFolder(job_folder_name)
                        break
                    except PermissionError:
                        time.sleep(1)
                        try_count += 1
                        if try_count >= move_imgs_tries: break
                # Clear the temporary directory contents
                clearTempDir()
            else:
                print('No Daily Logs')
        job_name_itr += 1        


# Set filter for daily logs
def setFilter(num_days):
    driver.switch_to.default_content()
    # Find open filter button
    open_filter_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.FilterDrawerButton')))
    # Open filter sidebar
    while True:
        try:
            open_filter_btn.click()
        except ElementClickInterceptedException:
            # Wait for page load
            WebDriverWait(driver, 10).until_not(EC.presence_of_element_located((By.CSS_SELECTOR, '.loadingBackground')))
        else:
            break
    # Check if filter already set correclty
    if WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.FilterDateRange span.ant-select-selection-item'))).text != FILTER_OPTIONS[num_days]:
        # Set filter
        # Send keys to date range input
        date_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.FilterDateRange input')))
        date_input.send_keys(FILTER_OPTIONS[num_days])
        date_input.send_keys(Keys.ENTER)
    # Click apply changes button
    applyBtn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="applyFilters"]')))
    actionChains.move_to_element(applyBtn).move_by_offset(-10, 0).click().perform()
    # Close Filter
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@data-testid="closeFilter"]'))).click()


# Checks if dailyLogsExist on the current page
def dailyLogsExist(job_name: str):
    # Check for emptyState
    try:
        driver.find_element(By.CSS_SELECTOR, '#reactDailyLogsListDiv .EmptyState')
    except NoSuchElementException:
        return True
    except Exception as e:
        raise e
    else:
        # No daily logs
        return False


# On the current screen, downloads all images from daily logs
def downloadDailyLogsImages(max_imgs_per_dl, job_folder_name):
    # Get qty of daily logs
    driver.switch_to.default_content()
    driver.execute_script("window.scrollTo(0,0)")  # Scroll to top of page
    dailyLogs_container = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#root .ListSection')))    
    try:
        dailyLog_qty_elem = WebDriverWait(driver, 2).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.BTPagination .range span')))[2]
    except TimeoutException:
        return
    while True:
        try:
            dailyLog_qty_elem.click()
            break
        except ElementClickInterceptedException:
            pass
    num_dailyLogs = int(dailyLog_qty_elem.text)
    if num_dailyLogs > 50: num_dailyLogs = 50
    # Iterate through each daily log
    for i in range(num_dailyLogs):
        dailyLog_container = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "DailyLogListItem")][' + str(i+1) + ']')))
        try:
            bt_file_wrapper = WebDriverWait(dailyLog_container, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.bt-file-wrapper')))
        except (NoSuchElementException, TimeoutException):
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
                # Could not find the open image dialog box
                continue
            # Grab list of all image containers
            img_containers = WebDriverWait(img_dialog, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.bt-file-viewer-grid--item')))
            actionChains.move_to_element(img_dialog.find_element(By.XPATH, '//div')).click().perform()  # Click the titlebar of the dialog box to make the pane active
            # Click on all image download buttons
            if isinstance(max_imgs_per_dl, int):
                vid_ext = ('.MOV', '.mov', '.MP4', '.mp4', '.WMV', '.wmv', '.AVI', '.avi')
                if isinstance(img_containers, WebElement) and max_imgs_per_dl > 0:  # If only one image found
                    img_name = WebDriverWait(img_containers, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.bt-file-viewer-grid--title'))).text
                    # Check if file is a video. If so, do not download
                    if not img_name.endswith(vid_ext):
                        img_filepath = os.path.join(getDataValue('user_data', 'Downloads Directory'), job_folder_name, img_name)
                        # Checks to see if image exists in the folder already. If so, do not download.
                        if not os.path.isfile(img_filepath):
                            # Click single image download button
                            dnld_btn = WebDriverWait(img_containers, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.bt-file-viewer-grid--download')))
                            actionChains.move_to_element(dnld_btn).click().perform()
                elif len(img_containers) > 0:  # If multiple images
                    num_to_download = len(img_containers) if len(img_containers) < max_imgs_per_dl else max_imgs_per_dl
                    for i in range(num_to_download):
                        # Checks to see if image exists in the folder already. If so, do not download.
                        img_container = img_containers[i]
                        img_name = WebDriverWait(img_container, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.bt-file-viewer-grid--title'))).text
                        # Check if file is a video. If so, do not download
                        if not img_name.endswith(vid_ext):
                            img_filepath = os.path.join(getDataValue('user_data', 'Downloads Directory'), job_folder_name, img_name)
                            if not os.path.isfile(img_filepath):
                                # Click on each image's download button
                                dnld_btn = WebDriverWait(img_container, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.bt-file-viewer-grid--download')))
                                try:
                                    actionChains.move_to_element(dnld_btn).click().perform()
                                except ElementNotInteractableException:
                                    pass
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


# Close chrome driver bot
def quit():
    deleteTempDir()
    # clearTerminal()
    if driver is not None:
        driver.quit()
    print('\n\nProgram Finished\n')
    sys.exit()


# Main method
if __name__ == '__main__':
    num_retries = 3  # This is the number of times the program will rerun if no images were downloaded
    itr = 0
    while not reaching_images:
        try:
            deleteTempDir()  # Just in case it still exists
            setDownloadsPath()
            initDriver()
            initActionChains()
            login()
            downloadAllImages(number_of_days=7)  # TODO: have number_of_days be a user_data value
        except Exception as e:
            deleteTempDir()
            if pause_on_error: 
                print(e)
                input('Press ENTER...')
            if raise_error: raise e
            if send_emails: newStatus('ERROR: ' + str(e), True)
            quit()
        itr += 1
        if itr == num_retries:
            if send_emails: newStatus('ERROR: Could not download images after ' + num_retries + ' tries.', True)
            quit()
            # TODO: Sometimes, the site gets stuck on a loading page. Set an overall timeout for the program (say if it ran for more than 5 mins, quit)
    time.sleep(1)
    newStatus('Progam finished successfully', False)
    quit()