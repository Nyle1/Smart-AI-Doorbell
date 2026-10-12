from gpiozero import Button
from signal import pause
from datetime import datetime
import subprocess
import os

button = Button(17, pull_up=True, bounce_time=0.2)

photo_dir = os.path.expanduser("~/smart-doorbell/photos")
os.makedirs(photo_dir, exist_ok=True)

def doorbell_pressed():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{photo_dir}/visitor_{timestamp}.jpg"

    print("DING DONG!")
    print("Taking visitor photo...")

    subprocess.run([
        "rpicam-still",
        "-o", filename,
        "--width", "1296",
        "--height", "972",
        "--nopreview",
        "-t", "1000"
    ])

    print(f"Photo saved: {filename}")

button.when_pressed = doorbell_pressed

print("Smart Doorbell ready!")
print("Press the button to take a visitor photo.")

pause()

