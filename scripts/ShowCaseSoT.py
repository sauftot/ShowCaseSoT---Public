import obspython as OBS
import requests, pickle, threading, os, json
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchWindowException, NoSuchElementException

"""
    OBS-Python Script by vp to post sea of thieves reaper faction wins on twitch channel.
    Requires everything above and a valid nightbot api token in chromedriver.exe's directory.
"""

data = lambda: ...

# THE EMPTY STRINGS NEED TO BE FILLED OUT BY YOU USING YOUR NIGHTBOT API INFORMATION AND COMMAND ID
data.client_ID = ''
data.client_secret = ''
data.winsID = ''
data.levelID = ''

# INTERNAL DATA, DO NOT FILL !!!
data.run = False
data.setup = False
data.setupRunning = False
data.token = ''
data.faction = 0

  
def worker_thread():
    sleep(2)
    while not data.setup:
        print("ERROR: Stats Synchronization was toggled on before setup was complete! Complete setup to start sync'ing.")
        if not data.run:
            print("INFO: Cancelling Sync...")
            return
        sleep(3)
    
    print("INFO: Worker reached and set up.")
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(chrome_options=options)
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
    
    while data.run:
        if data.faction == 0:
            driver.get("https://www.seaofthieves.com/de/profile/reputation/Flameheart")
        else:
            driver.get("https://www.seaofthieves.com/de/profile/reputation/PirateLord")
        sleep(5)
        try:
            element = driver.find_element(By.XPATH, "/html/body/div/div/div/main/div/div[3]/div/div[2]/div[1]/div[2]/div/div/div[1]/div/div/div[3]")
        except NoSuchElementException:
            print("ERROR: Can't find element. Cookies invalid or website layout changed. Reload Script.")
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
        driver.get("https://www.seaofthieves.com/de/profile/reputation/")
        sleep(5)
        try:
            if data.faction == 0:
                element = driver.find_element(By.XPATH, "/html/body/div/div/div/main/div/div[3]/div/div[2]/button[12]/div/div/div/div[2]/div/div/div/div/div")
            else:
                element = driver.find_element(By.XPATH, "/html/body/div/div/div/main/div/div[3]/div/div[2]/button[11]/div/div/div/div[2]/div/div/div/div/div")
        except NoSuchElementException:
            print("ERROR: Can't find element. Cookies invalid or website layout changed. Reload Script.")
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
    print("INFO: Stopped sync'ing.")
    driver.close()
    return
      
def setup():
    driver = webdriver.Chrome()
    sleep(2)
    try:
        try:
            driver.get("https://www.seaofthieves.com/de/profile/reputation/")
        except TimeoutException:
            print("ERROR: Timeout received. Internet Connection stable?")
            data.setup = False
            data.setupRunning = False
            driver.close()
            return
        try:
            WebDriverWait(driver, timeout=120).until(lambda d: d.get_cookie('rat'))['value']
        except TimeoutException:
            data.setup = False
            data.setupRunning = False
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
            data.setupRunning = False
            return
        print("INFO: NightBot Token received.")
        data.setup = True
        data.setupRunning = False
        return
    except NoSuchWindowException:
        print("ERROR: The Window was unexpectedly closed.")
        data.setup = False
        data.setupRunning = False
        return
    
    
### OBS Functions

def script_load(settings):
    print("INFO: Script Initialized")
        
def script_unload():
    data.run = False
    dire = os.path.expandvars(r'%LOCALAPPDATA%')
    if data.setup:
        os.remove(dire + '/DO_NOT_CHANGE.txt')
    revokeToken(data.token)
    print("INFO: Script unloaded.")
    
def script_properties():
    props = OBS.obs_properties_create()
    setupButton = OBS.obs_properties_add_button(props, 'Setup', 'Setup', cb_setupButton)
    OBS.obs_property_set_visible(setupButton, True)
    toggleButton = OBS.obs_properties_add_button(props, 'Start', 'Start', cb_toggleButton)
    OBS.obs_property_set_visible(toggleButton, True)
    factionButton = OBS.obs_properties_add_button(props, 'Toggle Faction', 'Faction: Reaper', cb_factionButton)
    return props
    
    
def script_description():
    return "Make sure to update the DATA values inside the script with the information retrieved from executing the getNightBotCommands.py script!"
  
    
## Callbacks

def cb_setupButton(props, prop, *args, **kwargs):
    if not data.setupRunning:
        if data.setup:
            data.setup = False
        data.setupRunning = True
        starterThread = threading.Thread(target=setup)
        starterThread.start()
        print("INFO: Starting Setup Thread...")
    else:
        print("INFO: Setup is already running, please reload script.")

def cb_toggleButton(props, prop, *args, **kwargs):
    p = OBS.obs_properties_get(props, "Start")
    if data.run == False:
        OBS.obs_property_set_description(p, "Stop")
        t = threading.Thread(target=worker_thread)
        data.run = True
        t.start()
        return True
    data.run = False
    OBS.obs_property_set_description(p, "Start")
    return True
    
def cb_factionButton(props, prop, *args, **kwargs):
    p = OBS.obs_properties_get(props, "Toggle Faction")
    if data.faction == 0:
        OBS.obs_property_set_description(p, "Faction: Athena")
        data.faction = 1
        print("INFO: Faction set to Athena")
    else:
        OBS.obs_property_set_description(p, "Faction: Reaper")
        data.faction = 0
        print("INFO: Faction set to Reaper")
    return True


#### Helper Functions ####

def save_cookie(driver):
    dire = os.path.expandvars(r'%LOCALAPPDATA%')
    with open(dire + '/DO_NOT_CHANGE.txt', 'wb') as filehandler:
        pickle.dump(driver.get_cookies(), filehandler)
    filehandler.close()

def load_cookie(driver):
    dire = os.path.expandvars(r'%LOCALAPPDATA%')
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