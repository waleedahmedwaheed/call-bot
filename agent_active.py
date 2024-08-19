from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException,NoAlertPresentException
from element_actions import perform_element_action,wait_for_element_and_click
import time

def agentActive(driver):
    try:
        time.sleep(2)
                
        agent_active_link = driver.find_element(By.ID, 'NoneInSessionLink')
        driver.execute_script("arguments[0].style.visibility = 'visible';", agent_active_link)
        driver.execute_script("arguments[0].click();", agent_active_link)
        
        wait_for_element_and_click(driver, By.LINK_TEXT, "Call Agent Again", "click", timeout=60)
        
        alert = driver.switch_to.alert
        # Dismiss the alert
        alert.dismiss()
        print("Alert dismissed. Clicking 'Call Agent Again'.")
        
        perform_element_action(driver,By.XPATH, '//a[@onclick="NoneInSessionCalL();return false;"]', None, 'click')
        
        time.sleep(2)
    
        active_link = driver.find_element(By.XPATH, '//a[@onclick="AutoDial_ReSume_PauSe(\'VDADready\',\'\',\'\',\'\',\'\',\'\',\'\',\'YES\');"]')
        ActionChains(driver).move_to_element(active_link).click().perform()
        
    except TimeoutException:
        print("Timeout waiting for the link agentActive to be clickable")

    except NoAlertPresentException:
        pass  # No alert present, continue with the script