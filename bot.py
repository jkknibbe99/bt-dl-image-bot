from config import login_data
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

def login(ld):
    driver = webdriver.Chrome('chromedriver')
    driver.get(ld['login_url'])

    # Login
    driver.find_element_by_xpath('//*[@id="username"]').send_keys(ld['username'])  # Enter username
    driver.find_element_by_xpath('//*[@id="password"]').send_keys(ld['password'])  # Enter password
    driver.find_element_by_xpath('//*[@id="reactLoginListDiv"]/div/div/div/div/div[3]/div/div/div/form/button').click()  # Click login button

    # Wait for main dashboard to load in
    for i in range(10):
        time.sleep(1)
        if check_exists('//*[@id="reactMainNavigation"]/div[1]/div/ul/li[2]', driver):
            break

    driver.get('https://buildertrend.net/DailyLogs/DailyLogsList.aspx')  # Go to daily logs page

    # Select all listed jobs
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="reactJobPicker"]/div/div[2]/div/div/div[1]/div/div/li[1]/div/div'))).click()

    # Set # items per page to 20 for testing purposes
    # TODO: Remove this for production.
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
        tn_id = tn.get_dom_attribute('id')
        xpath = '//div[@id="' + tn_id + '"]/a[2]'
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath))).click()

    time.sleep(5)
    driver.quit()

'//*[@id="ctl00_ctl00_bodyTagControl"]/div[13]'

'//*[@id="ctl00_ctl00_bodyTagControl"]/div[9]/div[1]/button' # 50 page 1st one
'//*[@id="ctl00_ctl00_bodyTagControl"]/div[9]/div[1]/button'
'//*[@id="ctl00_ctl00_bodyTagControl"]/div[9]/div[1]/button'
'//*[@id="ctl00_ctl00_bodyTagControl"]/div[9]/div[1]/button'
'//*[@id="ctl00_ctl00_bodyTagControl"]/div[11]/div[1]/button'
'//*[@id="ctl00_ctl00_bodyTagControl"]/div[10]/div[1]/button'
'//*[@id="ctl00_ctl00_bodyTagControl"]/div[12]/div[1]/button'
'//*[@id="ctl00_ctl00_bodyTagControl"]/div[13]/div[1]/button'


# Checks if the given xpath is visible to the given driver
def check_exists(xpath, driver):
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True

if __name__ == '__main__':
    login(login_data)