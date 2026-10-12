from gpiozero import Button, Servo
from time import sleep

button = Button(17, pull_up=True, bounce_time=0.2)
servo = Servo(18)

def open_door():
    print("Door opening...")
    servo.max()

    sleep(3)

    print("Door closing...")
    servo.min()

button.when_pressed = open_door

print("Cardboard door system ready.")

while True:
    sleep(1)
