import pyautogui
import time
import sys
import os

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
    print("ERROR: Extensions button not found!")

pyautogui.click(extensions_button)

# Select and click the bitwarden extension
pause(1)
pyautogui.press('tab')
pyautogui.press('tab')
pyautogui.press('enter')

# Select and click Login
pause(1)
pyautogui.press('tab')
pyautogui.press('enter')

# Close chrome
pause(2)
pyautogui.hotkey('alt', 'f4')

# Print final message
pause(3)
print("ALL TESTS DONE.")
