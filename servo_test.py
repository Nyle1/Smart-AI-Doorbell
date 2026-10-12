import time
from gpiozero import Servo
from config import SERVO_PIN

servo = Servo(SERVO_PIN)
try:
    print("Opening cardboard door prototype")
    servo.max()
    time.sleep(0.8)
    servo.detach()
    time.sleep(3)
    print("Closing")
    servo.min()
    time.sleep(0.8)
    servo.detach()
finally:
    servo.close()
