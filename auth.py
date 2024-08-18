from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, ElementNotInteractableException, NoSuchElementException
import time
from element_actions import perform_element_action,send_keys_to_element,wait_for_element_and_click
from config.config import USERNAME,PASSWORD

def login(driver,url): 

    driver.get(url)

    VD_login_input = perform_element_action(driver,By.NAME,'phone_login')
    send_keys_to_element(VD_login_input, USERNAME)
    
    VD_pass_input = perform_element_action(driver,By.NAME,'phone_pass')
    send_keys_to_element(VD_pass_input, PASSWORD)
    
    perform_element_action(driver,By.NAME, 'login_sub', None, 'click')
    
    time.sleep(2)
    
    VD_login_input = perform_element_action(driver,By.NAME,'VD_login')
    send_keys_to_element(VD_login_input, USERNAME)
    
    VD_pass_input = perform_element_action(driver,By.NAME,'VD_pass')
    send_keys_to_element(VD_pass_input, PASSWORD)

    perform_element_action(driver,By.NAME, 'VD_campaign', None, 'click')

    # Wait for a short duration after clicking to allow options to load
    time.sleep(2)

    # Select the first option after it loads
    vd_campaign_select = Select(perform_element_action(driver,By.NAME,'VD_campaign'))
    vd_campaign_select.select_by_index(2)

    perform_element_action(driver,By.NAME, 'login_sub', None, 'click')
    
    time.sleep(2)
    
    try:
        wait_for_element_and_click(driver, By.LINK_TEXT, "OK", "click", timeout=6)
    except TimeoutException:
        print("Timeout waiting for the link to be clickable")
    
    try:
        perform_element_action(driver,By.XPATH, '//a[@onclick="hideDiv(\'DeactivateDOlDSessioNSpan\');return false;"]',None, 'click')
        time.sleep(2)
            
    except StaleElementReferenceException:
        print("StaleElementReferenceException. Skipping...")

    except ElementNotInteractableException:
        # Handle the case where the element is not interactable
        print("Element not interactable. Skipping...")
        
    except NoSuchElementException:
        # Handle the case where the element is not found
        print("Element not found. Skipping...")