from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, ElementNotInteractableException, NoSuchElementException
import time
from element_actions import perform_element_action

def login(driver,url): 

    driver.get(url)

    VD_login_input = perform_element_action(driver,By.NAME,'phone_login')
    VD_login_input.send_keys('8001')

    VD_pass_input = perform_element_action(driver,By.NAME,'phone_pass')
    VD_pass_input.send_keys('vici500')
    
    submit_button = perform_element_action(driver,By.NAME, 'login_sub')
    submit_button.click()
    
    time.sleep(2)
    
    VD_login_input = perform_element_action(driver,By.NAME,'VD_login')
    VD_login_input.send_keys('8001')

    VD_pass_input = perform_element_action(driver,By.NAME,'VD_pass')
    VD_pass_input.send_keys('vici500')    

    # Click on the VD_campaign select element to trigger the loading of options
    vd_campaign_select = perform_element_action(driver,By.NAME, 'VD_campaign')
    vd_campaign_select.click()

    # Wait for a short duration after clicking to allow options to load
    time.sleep(2)

    # Select the first option after it loads
    vd_campaign_select = Select(perform_element_action(driver,By.NAME,'VD_campaign'))
    vd_campaign_select.select_by_index(2)

    submit_button2 = perform_element_action(driver,By.NAME,'login_sub')
    submit_button2.click()
    time.sleep(2)
    
    try:
        link = WebDriverWait(driver, 6).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "OK"))
        )
        link.click()
    except TimeoutException:
        print("Timeout waiting for the link to be clickable")
    
    try:
        ok_button = perform_element_action(driver,By.XPATH, '//a[@onclick="hideDiv(\'DeactivateDOlDSessioNSpan\');return false;"]')
        ok_button.click()
        time.sleep(2)
            
    except StaleElementReferenceException:
        print("StaleElementReferenceException. Skipping...")

    except ElementNotInteractableException:
        # Handle the case where the element is not interactable
        print("Element not interactable. Skipping...")
        
    except NoSuchElementException:
        # Handle the case where the element is not found
        print("Element not found. Skipping...")