import subprocess
import time
from gpiozero import Button
from config import BUTTON_PIN, SOUND_PATH

def ring():
    print("Ding-dong!")
    if SOUND_PATH.exists():
        subprocess.Popen(["pw-play", str(SOUND_PATH)],
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)

button = Button(BUTTON_PIN, pull_up=True, bounce_time=0.1)
button.when_pressed = ring
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    button.close()
