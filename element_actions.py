from selenium.webdriver.common.by import By

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
