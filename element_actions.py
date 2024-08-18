from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def perform_element_action(driver, locator_type, locator_value, script_action=None, action=None, additional_actions=None):
    """
    Perform actions on a web element.

    :param driver: The WebDriver instance.
    :param locator_type: The type of locator (e.g., By.ID, By.XPATH).
    :param locator_value: The value of the locator (e.g., 'NoneInSessionLink', '//a[@onclick="..."]').
    :param script_action: Optional JavaScript action to execute on the element.
    :param action: Optional Selenium action to perform on the element (e.g., 'click').
    :param additional_actions: Optional additional actions to perform (e.g., using ActionChains).
    :return: The web element if an action is performed; None otherwise.
    """
    # Find the element
    element = driver.find_element(locator_type, locator_value)
    
    # Execute JavaScript action if provided
    if script_action:
        driver.execute_script(script_action, element)
    
    # Perform Selenium action if provided
    if action == 'click':
        element.click()
    
    # Perform additional actions if provided
    if additional_actions:
        for additional_action in additional_actions:
            additional_action(element)
            
    return element

def send_keys_to_element(element, keys):
    """
    Send keys to a web element.
    
    :param element: The WebElement instance.
    :param keys: The keys to send to the element.
    """
    element.send_keys(keys)
    
def wait_for_element_and_click(driver, locator_type, locator_value, timeout=10):
    """
    Wait for an element to be clickable and then click it.

    :param driver: The WebDriver instance.
    :param locator_type: The type of locator (e.g., By.ID, By.XPATH, By.LINK_TEXT).
    :param locator_value: The value of the locator (e.g., 'OK', '//a[@onclick="..."]').
    :param timeout: The maximum time to wait for the element to be clickable (default is 10 seconds).
    :return: The WebElement that was clicked, or None if the click was not successful.
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((locator_type, locator_value))
        )
        element.click()
        return element
    except TimeoutException:
        print(f"Timeout waiting for the element located by {locator_type}='{locator_value}' to be clickable.")
        return None