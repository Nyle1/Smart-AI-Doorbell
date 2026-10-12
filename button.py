from gpiozero import Button
from signal import pause

button = Button(17, pull_up=True, bounce_time=0.1)

print("Doorbell ready. Press the button.")

def pressed():
    print("DING DONG! Button pressed.")

button.when_pressed = pressed

pause()


