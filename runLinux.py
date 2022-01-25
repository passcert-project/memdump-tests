import pyautogui
import time
import sys
import os
import psutil
import re

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
'''

'''
TODO: General
    - Launch powershell or smth
    - Launch procdump
    - Find the process ID for bitwarden (How????)
        - Chrome.process (Dev mode only feature on chrome) - Problem: Seems to be a command you can type in the actual console of chrome itself but no way to communicate with it
                                                                I assume it's going to be harder than just OCR'ing but it's still ass
        - OCR if the above doesn't work (scuffed tho)
        - Test dev build of chrome and chrome.processes + write to file
    - How to align windows properly?
        - Alt Tab VS Moving relevant windows to a corner of the screen (Half/Half)???
            Chrome:
                --window-position	Specify the initial window position using --window-position=x,y
                --window-size	Specify the initial window size using --window-size=x,y


1 - Open chrome
    TODO:
        - See if you can specify the chrome user 
        - Replace clicks with tabs
2 - Locate the bitwarden app on the chrome tray
'''
def pause(secs_to_pause=1):
    time.sleep(secs_to_pause)

def memdump(pid, iteration):
    # maps contains the mapping of memory of a specific project
    map_file = f"/proc/{pid}/maps"
    mem_file = f"/proc/{pid}/mem"

    # output file
    out_file = f'{pid}-{iteration}.dump'

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

# Define the chrome command
size_opts = f"--window-position=0,0 --window-size={int(monitor_size.width/2)},{monitor_size.height}"
other_opts = "--password-store=basic"
ext_opts = "--load-extension=/home/vagrant/passcert/bw-browser-v1.55/build"
cmd = f"google-chrome {size_opts} {other_opts} {ext_opts}"

# Open chrome with the defined command
pyautogui.hotkey('alt', 'f2')
pause(1)
pyautogui.write(cmd)
pause(1)
pyautogui.press('enter')

# Locate and click the extensions icon
pause(3)
extensions_button = "/home/vagrant/passcert/memdump-tests/icons/Extensions_Icon.png"
if not pyautogui.locateOnScreen(extensions_button, confidence=0.9):
    sys.exit("ERROR: Extensions button not found!")

pyautogui.click(extensions_button)

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
pause(1)
pyautogui.press('tab')
pyautogui.press('enter')

# Enter email address and password
pause(1)
pyautogui.write("test@testemail.com")
pyautogui.press('tab')
secret_password = 'thisisatest456231'
pyautogui.write(secret_password)

# First memdump
memdump(pid, '0-before-login')

# Close chrome
pause(2)
pyautogui.hotkey('alt', 'f4')

# Print final message
pause(3)
print("ALL TESTS DONE.")
