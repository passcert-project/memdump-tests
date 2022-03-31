import logging
import os
import pyautogui
import time
import sys
import psutil
import re
import configparser

'''
Dependencies (so far)
python
pyautogui
pillow
opencv
psutil
'''

#region Global Variables
#Stages of mem dumps
MEMDUMP_BEFORE_TYPING = '0-before-typing-MP'
MEMDUMP_MID_TYPING_MP = '1-mid-typing-MP'
MEMDUMP_FINISH_TYPING_MP = '2-finish-typing-MP'
MEMDUMP_ON_UNLOCK = '3-on-unlock'
MEMDUMP_ON_TASK_FINISHED = '4-on-task-finished'
MEMDUMP_SESSION_TERMINATED = '5-session-terminated'

#File locations for the Icons
COMMAND_PROMPT = "/home/vagrant/passcert/memdump-tests/icons/Command_Prompt.png"
EXTENSIONS_BUTTON = "/home/vagrant/passcert/memdump-tests/icons/Extensions_Icon.png"
BITWARDEN_BUTTON = "/home/vagrant/passcert/memdump-tests/icons/BitWarden_Icon.png"
LOGIN_BUTTON = "/home/vagrant/passcert/memdump-tests/icons/Log_In_Button.png"
E_MAIL_TEXT = "/home/vagrant/passcert/memdump-tests/icons/E-mail_Text.png"
GOOGLE = "/home/vagrant/passcert/memdump-tests/icons/Google.png"
PLAY_BUTTON = "/home/vagrant/passcert/memdump-tests/icons/Play_Button.png"
BITWARDEN_BLUE_BUTTON = "/home/vagrant/passcert/memdump-tests/icons/BitWarden_Icon_Logged_In.png"
OPTIONS_BUTTON = "/home/vagrant/passcert/memdump-tests/icons/Options.png"
YES_BUTTON = "/home/vagrant/passcert/memdump-tests/icons/Yes_Button.png"
BITWARDEN_ENV_SETTINGS = "/home/vagrant/passcert/memdump-tests/icons/BitWarden_Env_Settings_Button.png"

#Task time
TASK_TIME = 60
#endregion

#region Functions
def pause(secs_to_pause=1):
    """Pauses the script for secs_to_pause seconds. 
    """

    time.sleep(secs_to_pause)

def getExtensionName(extensionDir):
    head,_ = os.path.split(extensionDir)
    _, extensionName = os.path.split(head)

    return extensionName

def memdump(pid, nthTest, iteration, dumpSaveLocation, extensionName):
    # maps contains the mapping of memory of a specific project
    map_file = f"/proc/{pid}/maps"
    mem_file = f"/proc/{pid}/mem"

    # output directory
    out_dir = os.path.join(dumpSaveLocation, extensionName)
    # output file
    out_file = os.path.join(out_dir, f'{nthTest}-{iteration}.dump')
    #Make sure the directory exists, and if not create it
    os.makedirs(out_dir, exist_ok=True)

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
    """Scans the screen to find a section equal to the imageFile. Returns a box with the position of the match in screen coordinates if successful,
    None otherwise.

    The function matches a section of the screen if 90% of its' pixels match the given imageFile.
    """

    try:
        match = pyautogui.locateOnScreen(imageFile, confidence=0.9)

        if not match:
            logging.info("Image %s not found.", os.path.basename(imageFile))
            return match
        else:
            logging.info('Image %s found at x=%d, y=%d.', os.path.basename(imageFile), match.left, match.top)
            return match
    except pyautogui.ImageNotFoundException:
        #NOTE: Even though the documentation says locateOnScreen should send this exception, I've never actually seen it raise it. Still, for precaution
        logging.info("Image %s not found.", os.path.basename(imageFile))
        return None

def findAndClick(imageFile, delayBeforeClicking=0):
    """Scans the screen to find a section equal to the imageFile and clicks the center of the section if found, after the specified delay in seconds
    (by default it has no delay).
    Returns True if the image was located and clicked, False otherwise.

    The function matches a section of the screen if 90% of its' pixels match the given imageFile.
    """

    buttonLocation = findImage(imageFile)
    if buttonLocation != None:
        pause(delayBeforeClicking)
        pyautogui.click(buttonLocation.left, buttonLocation.top)
        return True
    else:
        return False

def waitForImage(imageFile, addedDelay=0):
    """Continously scans the screen every second to find a section equal to the imageFile until a match is found 
    and then pauses for the specified time in addedDelay.
    Returns a box with the position of the match in screen coordinates.

    This function can loop forever if a match is never found.
    """

    while not (location := findImage(imageFile)):
        logging.info("Waiting for image %s. Pausing for 1 second and rechecking...", os.path.basename(imageFile))
        pause()
    pause(addedDelay)
    return location

def waitForImageAndClick(imageFile, delayBeforeClicking=0):
    """Continously scans the screen every second to find a section equal to the imageFile until a match is found 
    and then clicks the center of the section after the specified delayBeforeClicking.

    This function can loop forever if a match is never found.
    """

    while not findAndClick(imageFile, delayBeforeClicking):
        logging.info("Waiting for image %s. Pausing for 1 second and rechecking...", os.path.basename(imageFile))
        pause()

def openBitWardenFailSafe(maxRetries = 5):
    """This functions opens the main BitWarden extension window, even if the extension window gets closed by some interruption (new tab opened, etc...).
    The function retries up to maxRetries to open the BitWarden extension and if it fails, it clicks on the extension button again and retries until
    BitWarden is open.

    Necessary because BitWarden opens a new tab to congratulate us for installing it and depending on the timing can cancel the extension window,
    so this approach is easier and more consistent.
    """

    waitForImageAndClick(EXTENSIONS_BUTTON)
    
    currRetries = 0
    found_bitwarden = None

    while currRetries < maxRetries:
        found_bitwarden = findImage(BITWARDEN_BUTTON)
        
        if found_bitwarden:
            pyautogui.click(found_bitwarden.left, found_bitwarden.top)
            return

        currRetries += 1
        logging.info("Retrying for image %s (%d out of %d).", os.path.basename(BITWARDEN_BUTTON), currRetries, maxRetries)
        pause()
    else:
        openBitWardenFailSafe()
    return
#endregion

def setEnvironmentURL(googleChromeCmd):
    """This function will properly set BitWarden's environment URL to point to the local BitWarden server. Opens Chrome with the given googleChromeCmd.

    This function closes Chrome at the end. Why? Because if we do not close Chrome after setting the env URL, there will be 4-5 different processes with
    the BitWarden tag sleeping and closing Chrome fixes that issue. We only want 1 BitWarden process so we know which one to memdump. As to why this happens?
    No clue really :(
    """

    logging.info("Environment URL setup: Start")

    # Open chrome with the defined command
    pyautogui.hotkey('alt', 'f2')
    waitForImage(COMMAND_PROMPT, 1)
    #For reference: 
    pyautogui.write(googleChromeCmd)
    pause(1)
    pyautogui.press('enter')

    openBitWardenFailSafe()

    #Click the settings button before the log-in
    waitForImageAndClick(BITWARDEN_ENV_SETTINGS)

    #Write localhost as the server URL
    pyautogui.press('tab', 3, 0.15)
    pyautogui.write("localhost")
    pyautogui.press('enter')

    #Close chrome to start the testing
    pause(2)
    pyautogui.hotkey('alt', 'f4')
    logging.info("Environment URL setup: Finished")

def performTest(googleChromeCmd, nthTest, memDumpDirectory, extensionName):
    """This function performs an entire test.
    googleChromeCmd: the command to open up Google Chrome
    nthTest: the number of the current test
    memDumpDirectory: where should the memory dumps be stored
    extensionName: the current extension name being tested
    """
    
    logging.info("Starting test %d.", nthTest)

    # Open chrome with the defined command
    pyautogui.hotkey('alt', 'f2')
    waitForImage(COMMAND_PROMPT, 1)
    #For reference: 
    pyautogui.write(googleChromeCmd)
    pause(1)
    pyautogui.press('enter')

    #Click the extension button and then BitWarden
    openBitWardenFailSafe()

    # Select and click Login
    waitForImageAndClick(LOGIN_BUTTON)

    # Get PID of Bitwarden browser extension
    chrome_extensions = [proc for proc in psutil.process_iter() if proc.name() == 'chrome' and ('--extension-process' in proc.cmdline())]
    if len(chrome_extensions) != 1:
        print(chrome_extensions)
        sys.exit("ERROR: Could not get PID of Bitwarden Chrome extension")

    pid = chrome_extensions[0].pid
    logging.info('PID of Bitwarden Chrome extension: %d', pid)

    #E-mail
    email_text = waitForImage(E_MAIL_TEXT)
    pyautogui.click(email_text.left, email_text.top + 10)
    pyautogui.hotkey('ctrl', 'a')

    #Type the e-mail address and replace the old one if there was
    pause()
    pyautogui.write(configFile['username'])
    pyautogui.press('tab')

    #Perform first memory dump (control mem dump)
    memdump(pid, nthTest, MEMDUMP_BEFORE_TYPING, memDumpDirectory, extensionName)
    pause(1)

    #Password details
    secret_password = configFile['password']
    firstpart, secondpart = secret_password[:len(secret_password)//2], secret_password[len(secret_password)//2:]

    #Write half the password first, mem-dump after
    pyautogui.write(firstpart, interval=0.15)
    memdump(pid, nthTest, MEMDUMP_MID_TYPING_MP, memDumpDirectory, extensionName)

    #Write the second half of the MP, mem-dump
    pyautogui.write(secondpart, interval=0.15)
    memdump(pid, nthTest, MEMDUMP_FINISH_TYPING_MP, memDumpDirectory, extensionName)

    #Perform login
    #NOTE: Just press enter to submit the form. This makes it universal for all scripts since the child component one does not follow the same tab order
    pyautogui.press('enter')

    #Perform memdump after the vault opens (Check when the options button is up)
    waitForImage(OPTIONS_BUTTON)
    memdump(pid, nthTest, MEMDUMP_ON_UNLOCK, memDumpDirectory, extensionName)
    pause()

    #Simulate task
    #https://player.vimeo.com/video/604015327
    pyautogui.hotkey('ctrl', 't')
    waitForImage(GOOGLE)
    pyautogui.write('https://player.vimeo.com/video/604015327')
    pyautogui.press('enter')
    waitForImageAndClick(PLAY_BUTTON, 1)
    logging.info('Playing video for %d seconds.', TASK_TIME)

    pause(TASK_TIME)

    logging.info('Simulation of task ended.')
    memdump(pid, nthTest, MEMDUMP_ON_TASK_FINISHED, memDumpDirectory, extensionName)

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
    memdump(pid, nthTest, MEMDUMP_SESSION_TERMINATED, memDumpDirectory, extensionName)

    # Close chrome
    pause(2)
    pyautogui.hotkey('alt', 'f4')

if (len(sys.argv)) == 1:
    sys.exit("ERROR: Please run the script with at least 1 extension.\nExample: python3 /home/vagrant/passcert/memdump-tests/runLinux.py /home/vagrant/passcert/bw-browser-v1.55/build/")

#Set up the logger
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

# Obtain monitor size
monitor_size = pyautogui.size()

#Config file
configFile = configparser.ConfigParser()

configFile.read('/home/vagrant/passcert/memdump-tests/config.ini')

configFile = configFile['DEFAULT']

if not configFile['username'] or not configFile['password']:
    sys.exit("ERROR: Please follow the instructions in the sampleconfig.ini before starting the tests")

#Set up the directory for the memory dumps
memDumpDirectory = os.getcwd()
if not configFile['memoryDumpDirectory']:
    logging.info('No directory set up for the memory dumps, using the current working directory instead: %s.', memDumpDirectory)
else:
    memDumpDirectory = configFile['memoryDumpDirectory']
    logging.info('Memory dump directory set to: %s.', memDumpDirectory)

numberOfTests = configFile.getint('numberOfTests', 0)

logging.info("Perfoming %d tests.", numberOfTests)

extension_list = []

for i in range(1, len(sys.argv)):
    extension_list.append(sys.argv[i])

extension_names = []
for dir in extension_list:
    extension_names.append(getExtensionName(os.path.normpath(dir)))

for i in range(len(extension_list)):
    # Define the chrome command
    size_opts = f"--window-position=0,0 --window-size={int(monitor_size.width/2)},{monitor_size.height}"
    other_opts = "--password-store=basic"
    ext_opts = "--load-extension=" + extension_list[i]
    flag_opts = "--allow-insecure-localhost"
    cmd = f"google-chrome {flag_opts} {size_opts} {other_opts} {ext_opts}"
    
    #Run tests
    for j in range(numberOfTests):

        #NOTE: Reset Chrome settings to avoid a) loading with more than 1 extension and b) Chrome might randomly disable the extension because it deems it "unsafe"
        #Also give it some time because chrome might still be writing stuff in the folder (https://unix.stackexchange.com/questions/506319/why-am-i-getting-directory-not-empty-with-rm-rf)
        pause(2)
        os.system("sudo rm -rf /home/vagrant/.config/google-chrome; sudo mkdir -p /home/vagrant/.config/google-chrome; sudo cp -rf /vagrant/data/google-chrome/* /home/vagrant/.config/google-chrome; sudo chown -R vagrant.vagrant /home/vagrant/.config/google-chrome")
        pause(2)

        setEnvironmentURL(cmd)

        performTest(cmd, j, memDumpDirectory, extension_names[i])
        logging.info("Percentage of tests completed for extension %s: %f%%.", extension_names[i], (j + 1) / numberOfTests * 100)

# Print final message
logging.info("ALL TESTS DONE.")