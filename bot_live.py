from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException, NoAlertPresentException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains

import ctypes
import time
from playsound import playsound
 

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from setup_browser import setup_browser
from speech_recognition_config import get_recognizer  
import speech_recognition as sr
from auth import login
from play_prompts import playPrompts, playPrompts2, playPrompts3
from config.config import CHROMEDRIVER_PATH, URL, CALLDEAD, CALLON, CALLOFF
from element_actions import perform_element_action,send_keys_to_element,wait_for_element_and_click,wait_for_element,dismiss_alert_if_present,wait_for_image_and_get_src
from agent_active import agentActive

nltk.downloader.download('vader_lexicon')

url = URL

# Initialize the recognizer
r = get_recognizer()
sia = SentimentIntensityAnalyzer()

    
def playPromptGetReply(promptPart,driver):
    try:
        # use the microphone as a source for input.
        with sr.Microphone() as source2:
            if promptPart == 1:
                playPrompts()
                detectCallDisconnection(driver)
            elif promptPart == 2:
                playPrompts2()
                detectCallDisconnection(driver)
            
            r.adjust_for_ambient_noise(source2, duration=0.2)
            
            # listens for the user's input 
            audio2 = r.listen(source2)
            
            # Try using Google to recognize audio
            try:
                text = r.recognize_google(audio2)
                text = text.lower()
                print("Did you say (Google):", text)
                
            except sr.UnknownValueError:
                # If Google recognizer couldn't understand the audio, try using Sphinx
                text = r.recognize_sphinx(audio2)
                #text = r.recognize_sphinx(audio2, language="en-US", keyword_entries=keyword_entries)
                print("You said (Sphinx):", text) 
                
                 
            sentiment_scores = sia.polarity_scores(text) 
            if sentiment_scores["compound"] > 0.2:
                print('positive')
                return 1  # Positive sentiment, return 1
            else:
                print("negative")
                perform_element_action(driver,By.XPATH, '//a[@onclick="hangup_customer_button_click(\'\',\'\',\'\',\'\',\'YES\');"]',None, 'click')
                
                try:
                    alert_after_hangup = driver.switch_to.alert
                    alert_after_hangup.dismiss()
                    print("Alert after 'Hangup Customer' dismissed.")

                    # If there's a need to interact with elements inside the alert,
                    # you need to switch back to the default content first
                    driver.switch_to.default_content()
                    
                    perform_element_action(driver,By.XPATH, '//a[@onclick="DispoSelectContent_create(\'A\',\'ADD\',\'YES\');return false;"]',None, 'click')
                
                    # Double-click the "A - Answering Machine" link
                    answering_machine_link = driver.find_element(By.XPATH,'//a[@onclick="DispoSelect_submit(\'\',\'\',\'YES\');return false;"]')    
                    action_chain = ActionChains(driver)
                    action_chain.double_click(answering_machine_link).perform()

                except NoAlertPresentException:
                    pass  # No alert after "Hangup Customer" present
                    
                return 0  # Negative sentiment, return 0
            
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))
        return None  # Handle error by returning None or an appropriate value
    except sr.UnknownValueError:
        print("Unknown error occurred")
        return None  # Handle error by returning None or an appropriate value

        
###################################################################    
def handle_call_state(driver, current_image_source):
    if current_image_source == CALLON:
        print("Live call is ON. Performing additional actions...")

        replyValue = playPromptGetReply(1, driver)
        print('replyValue:', replyValue)
        detectCallDisconnection(driver)
        if replyValue == 1:
            replyValue2 = playPromptGetReply(2, driver)
            detectCallDisconnection(driver)
            if replyValue2 == 1:
                playPrompts3()
                detectCallDisconnection(driver)
                perform_element_action(driver, By.XPATH, '//a[@onclick="ShoWTransferMain(\'ON\',\'\',\'YES\');"]', None, 'click')
                wait_for_element_and_click(driver, By.XPATH, '//span[@id="LocalCloser"]/a', None, timeout=6)

    elif current_image_source == CALLDEAD:
        print("Live call is DEAD. Clicking 'Hangup Customer'...")
        perform_element_action(driver, By.XPATH, '//a[@onclick="hangup_customer_button_click(\'\',\'\',\'\',\'\',\'YES\');"]', None, 'click')

        dismiss_alert_if_present(driver)

        perform_element_action(driver, By.XPATH, '//a[@onclick="DispoSelectContent_create(\'A\',\'ADD\',\'YES\');return false;"]', None, 'click')

        action_chain = ActionChains(driver)
        answering_machine_link = driver.find_element(By.XPATH, '//a[@onclick="DispoSelect_submit(\'\',\'\',\'YES\');return false;"]')
        action_chain.double_click(answering_machine_link).perform()

    elif current_image_source == CALLOFF:
        off_customer_link = wait_for_element_and_click(driver, By.XPATH, '//a[@onclick="DispoSelectContent_create(\'A\',\'ADD\',\'YES\');return false;"]', 'click')
        if off_customer_link:
            off_customer_link.click()

        submit_link = wait_for_element_and_click(driver, By.XPATH, '//a[@onclick="DispoSelect_submit(\'\',\'\',\'YES\');return false;"]', 'click')
        if submit_link:
            submit_link.click()


def detectCallDisconnection(driver):
    try:
        current_image_source = wait_for_image_and_get_src(driver)
        handle_call_state(driver, current_image_source)
    except TimeoutException:
        print("Timeout while waiting for the call status image.")
        return True  # Assuming a timeout could indicate a disconnection
    except Exception as e:
        print(f"An error occurred while detecting call disconnection: {e}")
        return True  # Returning True on error as a fail-safe


def run(driver):
    previous_image_source = CALLOFF
    while True:
        try:
            print(driver.current_url)  
            try:
                print('image_element')
                current_image_source = wait_for_image_and_get_src(driver)
                if current_image_source != previous_image_source:
                    print("Image source class has changed. New source:", current_image_source)
                    handle_call_state(driver, current_image_source)
                    previous_image_source = current_image_source
                else:
                    print("Image call source has not changed.")
            except TimeoutException:
                print("Timed out waiting for the image class element. Retrying...")
                
            
        except WebDriverException as e:
        
            print(f"WebDriverException: {e}")
            dismiss_alert_if_present(driver)
            current_image_source = wait_for_image_and_get_src(driver)
            
            # Check if the image source has changed since the last iteration
            if current_image_source != previous_image_source:
                print("Image source has changed. New source:", current_image_source)
                 
                handle_call_state(driver, current_image_source)    
                    
                # Update the previous_image_source variable
                previous_image_source = current_image_source

            else:
                print("Image source has not changed.")
                    
        except Exception as e:
            print(f"Unexpected Exception: {e}")
            
        finally:
            # Close or release audio resources here
            ctypes.windll.winmm.mciSendStringW("close all", None, 0, None)
       
       
        time.sleep(5)
    
def main():
    # Initialize the browser with the path from config
    driver = setup_browser(CHROMEDRIVER_PATH)

    # Call the login function with the driver and URL
    login(driver, URL)

    # Call the agentActive function
    agentActive(driver)
    
    run(driver)
    
    
 

