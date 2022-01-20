import pyautogui
import time
import sys

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
#Variables
time_to_sleep = 1

monitor_size = pyautogui.size()

#1 - Open Chrome
pyautogui.hotkey('win', 'r')
pyautogui.write('chrome --window-position=0,0 --window-size={:d},{:d}'.format(int(monitor_size.width / 2), monitor_size.height))
pyautogui.press('enter')

time.sleep(time_to_sleep + 3)
#2 - Locate the bitwarden app on the chrome tray
bitwardenButtonTrayLocation = pyautogui.locateOnScreen('icons/BitWarden Task Icon.png', confidence=0.9)

print ('Button coords: x:', bitwardenButtonTrayLocation.left, ' y:', bitwardenButtonTrayLocation.top)
pyautogui.click('icons/BitWarden Task Icon.png')

#Iniciar sessão
time.sleep(time_to_sleep)
pyautogui.press('tab')
pyautogui.press('enter')

#Write password
pyautogui.write(sys.argv[1])

#Press login button
time.sleep(time_to_sleep)
pyautogui.press('tab', presses=4, interval=0.15)
pyautogui.press('enter')

#Click the settings button
#NOTE: It's better to keep the locate button for now since there could be multiple entries
time.sleep(time_to_sleep + 1)
pyautogui.click('icons/Options.png')

#Terminate session button
time.sleep(time_to_sleep)
pyautogui.press('tab', presses=14, interval=0.15)
pyautogui.press('enter')

#And terminate session
pyautogui.press('enter')

#Close browser
pyautogui.hotkey('alt', 'f4')
