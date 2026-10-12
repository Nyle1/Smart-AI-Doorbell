import time
from gpiozero import Button
from config import BUTTON_PIN

button = Button(BUTTON_PIN, pull_up=True, bounce_time=0.1)
print("Press button on GPIO17; Ctrl+C to quit")
button.when_pressed = lambda: print("Doorbell pressed!")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    button.close()
