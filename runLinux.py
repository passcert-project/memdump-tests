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
TODO: - Ignore e-mail after first successful login  
    - Code refactoring (make the script easier to read/go through)
    - Use loops and check if certain conditions are met in the later versions (by locating on screen for example)

'''

#Global strings
#Stages of mem dumps
MEMDUMP_BEFORE_TYPING = '0-before-typing-MP'
MEMDUMP_MID_TYPING_MP = '1-mid-typing-MP'
MEMDUMP_FINISH_TYPING_MP = '2-finish-typing-NP'
MEMDUMP_ON_UNLOCK = '3-on-unlock'


def pause(secs_to_pause=1):
    time.sleep(secs_to_pause)

def memdump(pid, iteration):
    # maps contains the mapping of memory of a specific project
    map_file = f"/proc/{pid}/maps"
    mem_file = f"/proc/{pid}/mem"

    # output file
    out_file = f'{pid}-{iteration}.dump'

    print(f'Starting mem dump...')
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
    print(f'Memory dump saved to {out_file}')

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
pause(1)

#For reference: 
pyautogui.write(cmd)
pause(1)
pyautogui.press('enter')

#TODO: Testing if closing chrome first and then opening is good
pause(15)
pyautogui.hotkey('alt', 'f4')

#Again
pyautogui.hotkey('alt', 'f2')
pause(1)

#For reference: 
pyautogui.write(cmd)
pause(1)
pyautogui.press('enter')

# Locate and click the extensions icon
pause(3)
extensions_button = "/home/vagrant/passcert/memdump-tests/icons/Extensions_Icon.png"
extensions_buttonLoc = pyautogui.locateOnScreen(extensions_button, confidence=0.9)

if not extensions_buttonLoc:
    sys.exit("ERROR: Extensions button not found!")

print ('Extension button coords: x:', extensions_buttonLoc.left, ' y:', extensions_buttonLoc.top)
pyautogui.click(extensions_buttonLoc.left, extensions_buttonLoc.top)
pause(2)

# Get PID of Bitwarden browser extension
chrome_extensions = [proc for proc in psutil.process_iter() if proc.name() == 'chrome' and ('--extension-process' in proc.cmdline())]
if len(chrome_extensions) != 1:
    sys.exit("ERROR: Could not get PID of Bitwarden Chrome extension")

pid = chrome_extensions[0].pid
print(f"PID of Bitwarden Chrome extension: {pid}")

# Select and click the bitwarden extension
pause(1)
pyautogui.press('tab')
pyautogui.press('tab')
pyautogui.press('enter')

# Select and click Login
pause(4)
pyautogui.press('tab')
pyautogui.press('enter')

#sys.exit()
#Perform first memory dump (control mem dump)
memdump(pid, MEMDUMP_BEFORE_TYPING)

# Enter email address and password
'''
#TODO: disabled for now just for testing since bitwarden keeps track of the email
pyautogui.write(configFile['DEFAULT']['username'])
pyautogui.press('tab')
'''

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
#NOTE: It's better to keep the locate button for now since there could be multiple entries
options_button = "/home/vagrant/passcert/memdump-tests/icons/Options.png"

optionsbuttonloc = pyautogui.locateOnScreen(options_button, confidence=0.9)
if not optionsbuttonloc:
    sys.exit("ERROR: Options button not found!")

pyautogui.click(optionsbuttonloc.left, optionsbuttonloc.top)
print ('Option button coords: x:', optionsbuttonloc.left, ' y:', optionsbuttonloc.top)
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
pause(3)
print("ALL TESTS DONE.")
