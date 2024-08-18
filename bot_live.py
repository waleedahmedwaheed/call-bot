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
from element_actions import perform_element_action,send_keys_to_element,wait_for_element_and_click

nltk.downloader.download('vader_lexicon')

url = URL

# Initialize the recognizer
r = get_recognizer()
sia = SentimentIntensityAnalyzer()


    
   
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
        
        # Locate the specific <a> element within the span using XPath
        #active_button = driver.find_element(By.XPATH, "//span[@id='DiaLControl']/a[@onclick=\"AutoDial_ReSume_PauSe('VDADready','','','','','','','YES');\"]")

        # Click the located <a> element
        #active_button.click()

        
    except TimeoutException:
        print("Timeout waiting for the link agentActive to be clickable")

    except NoAlertPresentException:
        pass  # No alert present, continue with the script
    
def playPromptGetReply(promptPart,driver):
    try:
        # use the microphone as a source for input.
        with sr.Microphone() as source2:
            if promptPart == 1:
                playPrompts()
            elif promptPart == 2:
                playPrompts2()
                
            # wait for a second to let the recognizer
            # adjust the energy threshold based on
            # the surrounding noise level 
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
                
                # if text in ["yes", "yeah", "yup", "sure", "affirmative"]:
                    # print("User response: Yes (Affirmative)")
                    # return 1
                    # # Handle affirmative response
                # elif text in ["no", "nope", "nah", "negative", "not"]:
                    # print("User response: No (Negative)")
                    # try:
                        # alert_after_hangup = driver.switch_to.alert
                        # alert_after_hangup.dismiss()
                        # print("Alert after 'Hangup Customer' dismissed.")

                        # # If there's a need to interact with elements inside the alert,
                        # # you need to switch back to the default content first
                        # driver.switch_to.default_content()
                        
                        # a_link = driver.find_element(By.XPATH,'//a[@onclick="DispoSelectContent_create(\'A\',\'ADD\',\'YES\');return false;"]')        
                        # a_link.click()
                    
                        # # Double-click the "A - Answering Machine" link
                        # answering_machine_link = driver.find_element(By.XPATH,'//a[@onclick="DispoSelect_submit(\'\',\'\',\'YES\');return false;"]')    
                        # action_chain = ActionChains(driver)
                        # action_chain.double_click(answering_machine_link).perform()

                    # except NoAlertPresentException:
                        # pass  # No alert after "Hangup Customer" present
                        
                    # return 0  # Negative sentiment, return 0
                    
            #engine.say(text) 
            
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


def detectCallDisconnection():
    try:
        # Locate the image element that shows the call status
        # image_element = WebDriverWait(driver, 60).until(
            # EC.presence_of_element_located((By.XPATH, '//img[@name="livecall"]'))
        # )
        
        image_element = wait_for_element_and_click(driver, By.XPATH, '//img[@name="livecall"]', None, timeout=60)
        
        # Get the current source of the image
        current_image_source = image_element.get_attribute("src")
        
        # Check if the call is dead by comparing the image source URL
        if current_image_source == CALLDEAD:
            print("Live call is DEAD. Clicking 'Hangup Customer 1'...")
                
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
            
        print("Live call is still active.")

    except TimeoutException:
        print("Timeout while waiting for the call status image.")
        return True  # Assuming a timeout could indicate a disconnection

    except Exception as e:
        print(f"An error occurred while detecting call disconnection: {e}")
        return True  # Returning True on error as a fail-safe



def run(driver):
    previous_image_source = ""
    while True:
        try:
            
            print('current url')         
            print(driver.current_url)  
            
                
            try:
                print('image_element')
                image_element = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.XPATH, '//img[@name="livecall"]'))
                )

                # Get the source attribute of the image element
                current_image_source = image_element.get_attribute("src")

                # Check if the image source has changed since the last iteration
                if current_image_source != previous_image_source:
                    print("Image source class has changed. New source:", current_image_source)
                    
                    if current_image_source == CALLON:
                        # Perform specific actions when the image source is a certain URL
                        print("Live call is ON firstss. Performing additional actions...")                    

                         
                        replyValue = playPromptGetReply(1,driver)
                        print('replyValue')
                        print(replyValue)
                        if replyValue == 1:
                            print('ok')
                            replyValue2 = playPromptGetReply(2,driver)
                            if replyValue2 == 1:
                                print('ok2')
                                playPrompts3()
                                        
                                transfer_link = driver.find_element(By.XPATH,'//a[@onclick="ShoWTransferMain(\'ON\',\'\',\'YES\');"]')        
                                transfer_link.click()
                                
                                
                                a_element = WebDriverWait(driver, 6).until(
                                    EC.element_to_be_clickable((By.XPATH, '//span[@id="LocalCloser"]/a'))
                                )
                                a_element.click()
                                
                                # closer_link = driver.find_element(By.XPATH,'//a[@onclick="mainxfer_send_redirect(\'XfeRLOCAL\',\'SIP/DLabVoIP-0000daea\',\'\',\'\',\'\',\'\',\'YES\');return false;"]')        
                                # closer_link.click()
                                
                                
                    # Update the previous_image_source variable
                    previous_image_source = current_image_source

                else:
                    print("Image call source has not changed.")
                    
                if current_image_source == CALLDEAD:
                    print("Live call is DEAD. Clicking 'Hangup Customer 2'...")
                    
                    hangup_customer_link = driver.find_element(By.XPATH,'//a[@onclick="hangup_customer_button_click(\'\',\'\',\'\',\'\',\'YES\');"]')        
                    hangup_customer_link.click()
                    
                    try:
                        alert_after_hangup = driver.switch_to.alert
                        alert_after_hangup.dismiss()
                        print("Alert after 'Hangup Customer' dismissed.")

                        # If there's a need to interact with elements inside the alert,
                        # you need to switch back to the default content first
                        driver.switch_to.default_content()
                        
                        a_link = driver.find_element(By.XPATH,'//a[@onclick="DispoSelectContent_create(\'A\',\'ADD\',\'YES\');return false;"]')        
                        a_link.click()
                    
                        # Double-click the "A - Answering Machine" link
                        answering_machine_link = driver.find_element(By.XPATH,'//a[@onclick="DispoSelect_submit(\'\',\'\',\'YES\');return false;"]')    
                        action_chain = ActionChains(driver)
                        action_chain.double_click(answering_machine_link).perform()

                    except NoAlertPresentException:
                        pass  # No alert after "Hangup Customer" present
                        
                    previous_image_source = current_image_source
                    
                if current_image_source == CALLOFF:
                    print("Live call is OFF. Clicking 'OFF Customer'...")
                    
                    hangup_customer_link = driver.find_element(By.XPATH,'//a[@onclick="DispoSelectContent_create(\'A\',\'ADD\',\'YES\');return false;"]')        
                    hangup_customer_link.click()
                    
                    hangup_submit_link = driver.find_element(By.XPATH,'//a[@onclick="DispoSelect_submit(\'\',\'\',\'YES\');return false;"]')        
                    hangup_submit_link.click()
                    
                    previous_image_source = current_image_source
                    
            except TimeoutException:
                print("Timed out waiting for the image class element. Retrying...")
                
            
        
        except WebDriverException as e:
            print(f"WebDriverException: {e}")
            
            try:
                alert = driver.switch_to.alert
                # Dismiss the alert
                alert.dismiss()
                print("Alert dismissed. Clicking 'Go Back'.")
                
                # Click the "Go Back" button
                go_back_button = driver.find_element(By.XPATH,'//a[@onclick="NoneInSessionOK();return false;"]')
                go_back_button.click()
                
                # Continue to the next iteration without checking the div text
                continue

            except NoAlertPresentException:
                pass  # No alert present, continue with the script
                
            
            image_element = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.XPATH, '//img[@name="livecall"]'))
                )

            # Get the source attribute of the image element
            current_image_source = image_element.get_attribute("src")
            
            # Check if the image source has changed since the last iteration
            if current_image_source != previous_image_source:
                print("Image source has changed. New source:", current_image_source)
                
                if current_image_source == CALLON:
                    # Perform specific actions when the image source is a certain URL
                    print("Live call is ON. Performing additional actions...")

                     
                    playPrompts()
                    
                    nextPart = 0
                    
                    
                    
                    if nextPart == 1:
                        try:
                            with sr.Microphone() as source2:
                                r.adjust_for_ambient_noise(source2, duration=0.3)                
                                audio2 = r.listen(source2)
                                
                                try:
                                    text2 = r.recognize_google(audio2)
                                    text2 = text2.lower()
                                    print("Did you say (Google):", text2)
                                    
                                except sr.UnknownValueError:
                                    # If Google recognizer couldn't understand the audio, try using Sphinx
                                    text2 = r.recognize_sphinx(audio2)
                                    print("You said (Sphinx):", text2)
                                    
                                sentiment_scores = sia.polarity_scores(text2) 
                                if sentiment_scores["compound"] > 0.2:
                                    print('positive2')
                                    sound_file7 = "prompts/ok-great.wav" 
                                    playsound(sound_file7)
                                    sound_file8 = "prompts/transfer.wav" 
                                    playsound(sound_file8)
                                else:
                                    print("in google neg")
                                    # hangup_customer_link = driver.find_element(By.XPATH,'//a[@onclick="dialedcall_send_hangup(\'\',\'\',\'\',\'\',\'YES\');"]')        
                                    # hangup_customer_link.click()
                        except sr.RequestError as e:
                            print("Could not request results; {0}".format(e))
                        except sr.UnknownValueError:
                            print("Unknown error occurred")
                    

                    
                    
                if current_image_source == CALLDEAD:
                    print("Live call is DEAD. Clicking 'Hangup Customer 3'...")
                    
                    hangup_customer_link = driver.find_element(By.XPATH,'//a[@onclick="hangup_customer_button_click(\'\',\'\',\'\',\'\',\'YES\');"]')        
                    hangup_customer_link.click()
                    
                    try:
                        alert_after_hangup = driver.switch_to.alert
                        alert_after_hangup.dismiss()
                        print("Alert after 'Hangup Customer' dismissed.")

                        # If there's a need to interact with elements inside the alert,
                        # you need to switch back to the default content first
                        driver.switch_to.default_content()

                        # Double-click the "A - Answering Machine" link
                        answering_machine_link = driver.find_element(By.XPATH,'//a[@onclick="DispoSelect_submit(\'\',\'\',\'YES\');return false;"]')    
                        action_chain = ActionChains(driver)
                        action_chain.double_click(answering_machine_link).perform()

                    except NoAlertPresentException:
                        pass  # No alert after "Hangup Customer" present
                        
                if current_image_source == CALLOFF:
                    print("Live call is OFF. Clicking 'OFF Customer'...")
                    
                    hangup_customer_link = driver.find_element(By.XPATH,'//a[@onclick="DispoSelect_submit(\'\',\'\',\'YES\');return false;"]')        
                    hangup_customer_link.click()
                    
                    hangup_submit_link = driver.find_element(By.XPATH,'//a[@onclick="DispoSelect_submit(\'\',\'\',\'YES\');return false;"]')        
                    hangup_submit_link.click()
                    
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
    
    
 

