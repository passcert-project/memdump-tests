import logging
import os
import pyautogui
import time
import sys
import psutil
import re
import configparser

'''
Before typing MP - Done
Mid typing Master Password - Done
After finishing typing MP - Done
After unlocking - Done
After task
After terminating the session - Done
'''

'''
Dependencies (so far)
python
pyautogui
pillow
opencv
psutil
'''

'''
TODO:
    - Code refactoring (make the script easier to read/go through)
    - Continue to use waitForImage for other problem areas that might manifest
    - Document new functions
    - Switch extensions (git pull, compiliing)
    - Results/name of extensions
    - Config (put a directory for the results)
'''

#region Global Variables
#Stages of mem dumps
MEMDUMP_BEFORE_TYPING = '0-before-typing-MP'
MEMDUMP_MID_TYPING_MP = '1-mid-typing-MP'
MEMDUMP_FINISH_TYPING_MP = '2-finish-typing-NP'
MEMDUMP_ON_UNLOCK = '3-on-unlock'
MEMDUMP_ON_TASK_FINISHED = '4-on-task-finished'
MEMDUMP_SESSION_TERMINATED = '5-session-terminated'

#File locations for the Icons
COMMAND_PROMPT = "/home/vagrant/passcert/memdump-tests/icons/Command_Prompt.png"
BITWARDEN_PAGE_ICON = "/home/vagrant/passcert/memdump-tests/icons/BitWarden_Page_Icon.png"
EXTENSIONS_BUTTON = "/home/vagrant/passcert/memdump-tests/icons/Extensions_Icon.png"
BITWARDEN_BUTTON = "/home/vagrant/passcert/memdump-tests/icons/BitWarden_Icon.png"
LOGIN_BUTTON = "/home/vagrant/passcert/memdump-tests/icons/Log_In_Button.png"
E_MAIL_TEXT = "/home/vagrant/passcert/memdump-tests/icons/E-mail_Text.png"
GOOGLE = "/home/vagrant/passcert/memdump-tests/icons/Google.png"
PLAY_BUTTON = "/home/vagrant/passcert/memdump-tests/icons/Play_Button.png"
BITWARDEN_BLUE_BUTTON = "/home/vagrant/passcert/memdump-tests/icons/BitWarden_Icon_Logged_In.png"
OPTIONS_BUTTON = "/home/vagrant/passcert/memdump-tests/icons/Options.png"
YES_BUTTON = "/home/vagrant/passcert/memdump-tests/icons/Yes_Button.png"
#endregion

#region Functions
def pause(secs_to_pause=1):
    time.sleep(secs_to_pause)

def memdump(pid, nthTest, iteration):
    # maps contains the mapping of memory of a specific project
    map_file = f"/proc/{pid}/maps"
    mem_file = f"/proc/{pid}/mem"

    # output file
    out_file = f'{nthTest}-{iteration}.dump'

    logging.info('Starting mem dump on PID %d...', pid)
    # iterate over regions
    with open(map_file, 'r') as map_f, open(mem_file, 'rb', 0) as mem_f, open(out_file, 'wb') as out_f:
        for line in map_f.readlines():  # for each mapped region
            m = re.match(r'([0-9A-Fa-f]+)-([0-9A-Fa-f]+) ([-r])', line)
            if m.group(3) == 'r':  # readable region
                start = int(m.group(1), 16)
                end = int(m.group(2), 16)
                mem_f.seek(start)  # seek to region start
                #print(hex(start), '-', hex(end))
                try:
                    chunk = mem_f.read(end - start)  # read region contents
                    out_f.write(chunk)  # dump contents to standard output
                except OSError:
                    print(hex(start), '-', hex(end), '[error,skipped]', file=sys.stderr)
                    continue
    logging.info('Memory dump saved to %s', out_file)

def findImage(imageFile):
    try:
        buttonLocation = pyautogui.locateOnScreen(imageFile, confidence=0.9)

        if not buttonLocation:
            logging.info("Image %s not found.", os.path.basename(imageFile))
            return buttonLocation
        else:
            logging.info('Image %s found at x=%d, y=%d.', os.path.basename(imageFile), buttonLocation.left, buttonLocation.top)
            return buttonLocation
    except pyautogui.ImageNotFoundException:
        #NOTE: Even though the documentation says locateOnScreen should send this exception, I've never actually seen it raise it. Still, for precaution
        logging.info("Image %s not found.", os.path.basename(imageFile))
        return None

def findAndClick(imageFile, delayBeforeClicking=0):
    buttonLocation = findImage(imageFile)
    if buttonLocation != None:
        pause(delayBeforeClicking)
        pyautogui.click(buttonLocation.left, buttonLocation.top)
        return True
    else:
        return False

def waitForImage(imageFile, addedDelay=0):

    while not (location := findImage(imageFile)):
        logging.info("Waiting for image %s. Pausing for 1 second and rechecking...", os.path.basename(imageFile))
        pause()
    pause(addedDelay)
    return location

def waitForImageAndClick(imageFile, delayBeforeClicking=0):
    while not findAndClick(imageFile, delayBeforeClicking):
        logging.info("Waiting for image %s. Pausing for 1 second and rechecking...", os.path.basename(imageFile))
        pause()
#endregion

def performTest(googleChromeCmd, nthTest):
    logging.info("Starting test %d.", nthTest)

    # Open chrome with the defined command
    pyautogui.hotkey('alt', 'f2')
    waitForImage(COMMAND_PROMPT, 1)
    #For reference: 
    pyautogui.write(googleChromeCmd)
    pause(1)
    pyautogui.press('enter')

    #Wait for the BitWarden tab to open
    waitForImage(BITWARDEN_PAGE_ICON)

    # Locate and click the extensions icon
    waitForImageAndClick(EXTENSIONS_BUTTON)

    # Select and click the bitwarden extension
    waitForImageAndClick(BITWARDEN_BUTTON)

    # Select and click Login
    waitForImageAndClick(LOGIN_BUTTON)

    # Get PID of Bitwarden browser extension
    chrome_extensions = [proc for proc in psutil.process_iter() if proc.name() == 'chrome' and ('--extension-process' in proc.cmdline())]
    if len(chrome_extensions) != 1:
        sys.exit("ERROR: Could not get PID of Bitwarden Chrome extension")

    pid = chrome_extensions[0].pid
    logging.info('PID of Bitwarden Chrome extension: %d', pid)

    #E-mail
    #TODO: This works but check if there's issues depending on screen size
    email_text = waitForImage(E_MAIL_TEXT)
    pyautogui.click(email_text.left, email_text.top + 10)
    pyautogui.hotkey('ctrl', 'a')

    #Type the e-mail address and replace the old one if there was
    pause()
    pyautogui.write(configFile['DEFAULT']['username'])
    pyautogui.press('tab')

    #Perform first memory dump (control mem dump)
    memdump(pid, nthTest, MEMDUMP_BEFORE_TYPING)
    pause()

    #Password details
    secret_password = configFile['DEFAULT']['password']
    firstpart, secondpart = secret_password[:len(secret_password)//2], secret_password[len(secret_password)//2:]

    #Write half the password first, mem-dump after
    pyautogui.write(firstpart, interval=0.15)
    memdump(pid, nthTest, MEMDUMP_MID_TYPING_MP)

    #Write the second half of the MP, mem-dump
    pyautogui.write(secondpart, interval=0.15)
    memdump(pid, nthTest, MEMDUMP_FINISH_TYPING_MP)

    #Perform login
    #4 tabs + enter
    pyautogui.press('tab', presses=4, interval=0.15)
    pyautogui.press('enter')

    #Perform memdump after the vault opens (Check when the options button is up)
    waitForImage(OPTIONS_BUTTON)
    memdump(pid, nthTest, MEMDUMP_ON_UNLOCK)
    pause(1)

    #Simulate task
    #https://player.vimeo.com/video/604015327
    pyautogui.hotkey('ctrl', 't')
    waitForImage(GOOGLE)
    pyautogui.write('https://player.vimeo.com/video/604015327')
    pyautogui.press('enter')
    waitForImageAndClick(PLAY_BUTTON, 1)
    logging.info('Playing video for 60 seconds.')

    Task_time = 60
    pause(Task_time)

    logging.info('Simulation of task ended.')
    memdump(pid, nthTest, MEMDUMP_ON_TASK_FINISHED)

    # Locate and click the extensions icon
    waitForImageAndClick(EXTENSIONS_BUTTON)
    
    #Click the (now blue because we're logged in) BitWarden Button
    waitForImageAndClick(BITWARDEN_BLUE_BUTTON)

    #Click the settings button
    #NOTE: It's better to keep the locate button since there could be multiple entries in the password vault
    waitForImageAndClick(OPTIONS_BUTTON)
    #Terminate session button
    pause(3)
    pyautogui.press('tab', presses=14, interval=0.15)
    pyautogui.press('enter')

    #And terminate session
    waitForImageAndClick(YES_BUTTON)

    #Mem-dump after exiting the session
    memdump(pid, nthTest, MEMDUMP_SESSION_TERMINATED)

    # Close chrome
    pause(2)
    pyautogui.hotkey('alt', 'f4')


#Set up the logger
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

# Obtain monitor size
monitor_size = pyautogui.size()

#Config file
configFile = configparser.ConfigParser()
configFile.read('/home/vagrant/passcert/memdump-tests/config.ini')

if not configFile.defaults():
    sys.exit("ERROR: Please follow the instructions in the sampleconfig.ini before starting the tests")

# Define the chrome command
size_opts = f"--window-position=0,0 --window-size={int(monitor_size.width/2)},{monitor_size.height}"
other_opts = "--password-store=basic"
ext_opts = "--load-extension=/home/vagrant/passcert/bw-browser-v1.55/build"
cmd = f"google-chrome {size_opts} {other_opts} {ext_opts}"

numberOfTests = configFile['DEFAULT'].getint('numberOfTests', 0)

logging.info("Perfoming %d tests.", numberOfTests)

for i in range(numberOfTests):
    performTest(cmd, i)
    logging.info("Percentage of tests completed: %f%%.", i / numberOfTests * 100)

# Print final message
logging.info("ALL TESTS DONE.")