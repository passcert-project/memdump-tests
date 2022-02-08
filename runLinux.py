import logging
import pyautogui
import time
import sys
import psutil
import re
import configparser

'''
Before typing MP
Mid typing Master Password
After finishing typing MP
After unlocking
After task
After terminating the session
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
'''

#region Global Variables

#Stages of mem dumps
MEMDUMP_BEFORE_TYPING = '0-before-typing-MP'
MEMDUMP_MID_TYPING_MP = '1-mid-typing-MP'
MEMDUMP_FINISH_TYPING_MP = '2-finish-typing-NP'
MEMDUMP_ON_UNLOCK = '3-on-unlock'


#File locations for the Icons
COMMAND_PROMPT = "/home/vagrant/passcert/memdump-tests/icons/Command_Prompt.png"
EXTENSIONS_BUTTON = "/home/vagrant/passcert/memdump-tests/icons/Extensions_Icon.png"
E_MAIL_PROMPT_BLINK = "/home/vagrant/passcert/memdump-tests/icons/E-mail_prompt_blink.png"
E_MAIL_PROMPT_NO_BLINK = "/home/vagrant/passcert/memdump-tests/icons/E-mail_prompt_no_blink.png"
E_MAIL_TEXT = "/home/vagrant/passcert/memdump-tests/icons/E-mail_text.png"
OPTIONS_BUTTON = "/home/vagrant/passcert/memdump-tests/icons/Options.png"
#endregion

#region Functions
def pause(secs_to_pause=1):
    time.sleep(secs_to_pause)

def memdump(pid, iteration):
    # maps contains the mapping of memory of a specific project
    map_file = f"/proc/{pid}/maps"
    mem_file = f"/proc/{pid}/mem"

    # output file
    out_file = f'{pid}-{iteration}.dump'

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
            logging.info("Image %s not found.", imageFile)
            return buttonLocation
        else:
            logging.info('Image %s found at x=%d, y=%d.', imageFile, buttonLocation.left, buttonLocation.top)
            return buttonLocation
    except pyautogui.ImageNotFoundException:
        #NOTE: Even though the documentation says locateOnScreen should send this exception, I've never actually seen it raise it. Still, for precaution
        logging.info("Image %s not found.", imageFile)
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
        logging.info("Waiting for image %s. Pausing for 1 second and rechecking...", imageFile)
        pause()
    pause(addedDelay)
    return location

def waitForImageAndClick(imageFile, delayBeforeClicking=0):
    while not findAndClick(imageFile, delayBeforeClicking):
        logging.info("Waiting for image %s. Pausing for 1 second and rechecking...", imageFile)
        pause()
#endregion

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

# Open chrome with the defined command
pyautogui.hotkey('alt', 'f2')
waitForImage(COMMAND_PROMPT, 1)
#For reference: 
pyautogui.write(cmd)
pause(1)
pyautogui.press('enter')

# Locate and click the extensions icon
waitForImageAndClick(EXTENSIONS_BUTTON, 3)

# Get PID of Bitwarden browser extension
chrome_extensions = [proc for proc in psutil.process_iter() if proc.name() == 'chrome' and ('--extension-process' in proc.cmdline())]
if len(chrome_extensions) != 1:
    sys.exit("ERROR: Could not get PID of Bitwarden Chrome extension")

pid = chrome_extensions[0].pid
logging.info('PID of Bitwarden Chrome extension: %d', pid)

# Select and click the bitwarden extension
pause(1)
pyautogui.press('tab')
pyautogui.press('tab')
pyautogui.press('enter')

# Select and click Login
pause(4)
pyautogui.press('tab')
pyautogui.press('enter')

#E-mail
#TODO: Instead of looking for an image, just double click the e-mail address part, delete it and then type in the e-mail
#If there's no e-mail then nothing happens, if there is an e-mail then it's automatically deleted and pasted again which doesn't really matter for our purposes
#Consistency. How? Find the e-mail address part and move a few pixels below probably or do some math based on the size of the screen
pause(3)
email_text = waitForImage(E_MAIL_TEXT)
pyautogui.click(email_text.left, email_text.top + 10)
pyautogui.hotkey('ctrl', 'a')

#Type the e-mail address and replace the old one if there was
pause()
pyautogui.write(configFile['DEFAULT']['username'])
pyautogui.press('tab')

#Perform first memory dump (control mem dump)
memdump(pid, MEMDUMP_BEFORE_TYPING)
pause(1)

#Password details
secret_password = configFile['DEFAULT']['password']
firstpart, secondpart = secret_password[:len(secret_password)//2], secret_password[len(secret_password)//2:]

#Write half the password first, mem-dump after
pyautogui.write(firstpart, interval=0.15)
memdump(pid, MEMDUMP_MID_TYPING_MP)

#Write the second half of the MP, mem-dump
pyautogui.write(secondpart, interval=0.15)
memdump(pid, MEMDUMP_FINISH_TYPING_MP)

#Perform login
#4 tabs + enter
pyautogui.press('tab', presses=4, interval=0.15)
pyautogui.press('enter')

pause(3)
#Perform memdump after a bit (let the vault open)
memdump(pid, MEMDUMP_ON_UNLOCK)
pause(1)

#TODO: Simulate task


#Click the settings button
#NOTE: It's better to keep the locate button since there could be multiple entries in the password vault
waitForImageAndClick(OPTIONS_BUTTON)
#Terminate session button
pause(1)
pyautogui.press('tab', presses=14, interval=0.15)
pyautogui.press('enter')

#And terminate session
pyautogui.press('enter')

# Close chrome
pause(2)
pyautogui.hotkey('alt', 'f4')

# Print final message
print("ALL TESTS DONE.")
