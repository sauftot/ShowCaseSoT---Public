import obspython as OBS
import requests, pickle, threading, os, json
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchWindowException

"""
    OBS-Python Script by vp to post sea of thieves reaper faction wins on twitch channel.
    Requires everything above and a valid nightbot api token in chromedriver.exe's directory.
"""

# THE EMPTY STRINGS NEED TO BE FILLED OUT BY YOU, YOU CAN GET THIS INFO FROM YOUR NIGHTBOT PANNEL, APPLICATION SETTINGS
data = lambda: ...
data.streaming = False
data.setup = False
data.client_ID = ''
data.client_secret = ''
# RUN THE INCLUDED SCRIPT getNightBotCommands.py AND FIND THE ID IF YOUR CUSTOM !WINS AND !LEVEL COMMAND, THEN FILL THIS
data.winsID = ''
data.levelID = ''
# THIS WILL BE GENERATED DONT FILL!
data.token = ''



    
def worker_thread():
    sleep(2)
    while not data.setup:
        sleep(2) 
        if not data.streaming:
            print("INFO: Streaming was cancelled before setup was complete. You can close all windows")
            return 
    if not data.streaming:
        print("INFO: Streaming was cancelled before setup was complete. You can close all windows")
        return
    
    print("INFO: Worker reached.")
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(executable_path='../chromedriver.exe', chrome_options=options)
    wins = 0
    levels = 0
    try:
        driver.get("https://www.seaofthieves.com/de/profile/reputation/")
    except TimeoutException:
        print("ERROR: Timeout received. Internet Connection stable?")
        driver.close()
        return
    sleep(4)
    load_cookie(driver)
    
    while data.streaming:
        driver.get("https://www.seaofthieves.com/de/profile/reputation/FactionB")
        sleep(5)
        try:
            element = driver.find_element(By.XPATH, "/html/body/div/div/div/main/div/div[3]/div/div[2]/div[1]/div[2]/div/div/div[1]/div/div/div[3]")
        except NoSuchElementException:
            print("ERROR: Finding Element. Cookies most likely invalid. Reload Script.")
            driver.close()
            return
        if element.text != wins:
            s = requests.Session()
            s.headers.update({'Authorization' : 'Bearer ' + data.token})
            payload = {
                'count': element.text,
                'message': element.text + ' Wins.'
            }
            s.put('https://api.nightbot.tv/1/commands/' + data.winsID, data=payload)
            print("INFO: Wins Updated")
            s.close()
            wins = element.text
        # push to nightbot _id:638f6b04cb154ffa1a28aa4e
        driver.get("https://www.seaofthieves.com/de/profile/reputation/")
        sleep(5)
        try:
            element = driver.find_element(By.XPATH, "/html/body/div/div/div/main/div/div[3]/div/div[2]/button[12]/div/div/div/div[2]/div/div/div/div/div")
        except NoSuchElementException:
            print("ERROR: Finding Element. Cookies most likely invalid. Reload Script.")
            driver.close()
            return
        if element.text != levels:
            s = requests.Session()
            s.headers.update({'Authorization' : 'Bearer ' + data.token})
            payload = {
                'count': element.text,
                'message': 'Level ' + element.text
            }
            s.put('https://api.nightbot.tv/1/commands/' + data.levelID, data=payload)
            print("INFO: Level Updated")
            s.close()
            levels = element.text
        # push to nightbot _id:638f8ece1d5766902edb13ec
        
    print("INFO: Stopped streaming.")
    driver.close()
    return
        
        
def setup():
    driver = webdriver.Chrome(executable_path='../chromedriver.exe')
    sleep(2)
    try:
        try:
            driver.get("https://www.seaofthieves.com/de/profile/reputation/")
        except TimeoutException:
            print("ERROR: Timeout received. Internet Connection stable?")
            data.setup = False
            driver.close()
            return
        try:
            WebDriverWait(driver, timeout=120).until(lambda d: d.get_cookie('rat'))['value']
        except TimeoutException:
            data.setup = False
            driver.close()
            print("ERROR: SoT Login Timeout!")
            return
        print("INFO: Cookie received!.")
        save_cookie(driver)
        driver.close()
        print("INFO: Getting NightBot Token...")
        data.token = getToken()[0]
        if data.token == '':
            print("ERROR: NightBot Token void.")
            data.setup = False
            return
        print("INFO: NightBot Token received.")
        data.setup = True
        return
    except NoSuchWindowException:
        print("ERROR: The Window was unexpectedly closed.")
        data.setup = False
        return
    

def script_load(settings):
    starterThread = threading.Thread(target=setup)
    starterThread.start()
    OBS.obs_frontend_add_event_callback(on_streaming)
    print("INFO: Script Initialized")
    if OBS.obs_frontend_recording_active():
        t = threading.Thread(target=worker_thread)
        data.streaming = True
        t.start()
        
def script_unload():
    data.streaming = False
    dire = os.path.expandvars(r'%APPDATA%')
    if data.setup:
        os.remove(dire + '/DO_NOT_CHANGE.txt')
    revokeToken(data.token)
    print("INFO: Script unloaded.")
        


def on_streaming(event):
    t = threading.Thread(target=worker_thread)
    if event == OBS.OBS_FRONTEND_EVENT_RECORDING_STARTED:
        if data.setup == True:
            data.streaming = True
            t.start()
        else:
            print("ERROR: Setup is not completed!, please reload the script.")
    if event == OBS.OBS_FRONTEND_EVENT_RECORDING_STOPPED:
        data.streaming = False



#### Helper Functions ####

def save_cookie(driver):
    dire = os.path.expandvars(r'%APPDATA%')
    with open(dire + '/DO_NOT_CHANGE.txt', 'wb') as filehandler:
        pickle.dump(driver.get_cookies(), filehandler)
    filehandler.close()

def load_cookie(driver):
    dire = os.path.expandvars(r'%APPDATA%')
    with open(dire + '/DO_NOT_CHANGE.txt', 'rb') as cookiesfile:
        cookies = pickle.load(cookiesfile)
        for cookie in cookies:
            driver.add_cookie(cookie)
    cookiesfile.close()
    
def getToken():
    payload = {
                'client_id': '{0}'.format(data.client_ID),
                'client_secret': '{0}'.format(data.client_secret),
                'grant_type': 'client_credentials',
                'scope': 'commands'
            }
    response = requests.post('https://api.nightbot.tv/oauth2/token', data=payload)

    pure = json.loads(response.text)
    token = [pure['access_token']]
    return token

def revokeToken(k):
    payload = {
                'token':k
            }
    
    response = requests.post('https://api.nightbot.tv/oauth2/token/revoke', data=payload)
    
    print("INFO: NightBot Token deleted")