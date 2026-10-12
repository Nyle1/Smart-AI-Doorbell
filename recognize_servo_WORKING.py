from picamera2 import Picamera2
from gpiozero import Servo
import cv2
import time
import os

CASCADE = "/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml"
MODEL = os.path.expanduser("~/smart-doorbell/face_model.yml")

# ---------- SETTINGS ----------

UNKNOWN_THRESHOLD = 55

REQUIRED_MATCHES = 5

SERVO_PIN = 18

DOOR_OPEN_TIME = 3

# Prevent repeated opening while someone stands there
COOLDOWN = 10


# ---------- FACE RECOGNITION ----------

face_detector = cv2.CascadeClassifier(CASCADE)

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read(MODEL)

names = {
    1: "RESIDENT 1",
    2: "RESIDENT 2"
}


# ---------- SERVO ----------

servo = Servo(SERVO_PIN)

# Start with cardboard door closed
servo.min()

time.sleep(1)

servo.detach()


def open_door(name):

    print()
    print("============================")
    print(f"AUTHORIZED: {name}")
    print("OPENING CARDBOARD DOOR")
    print("============================")

    servo.max()

    time.sleep(DOOR_OPEN_TIME)

    print("Closing door...")

    servo.min()

    time.sleep(1)

    servo.detach()

    print("Door closed.")
    print()


# ---------- CAMERA ----------

camera = Picamera2()

config = camera.create_video_configuration(
    main={
        "size": (640, 480),
        "format": "RGB888"
    }
)

camera.configure(config)
camera.start()

time.sleep(2)


# ---------- CONFIRMATION ----------

last_person = None
match_count = 0
last_open_time = 0


print("Smart Face Door started!")
print(f"Recognition threshold: {UNKNOWN_THRESHOLD}")
print(f"Required matches: {REQUIRED_MATCHES}")
print("Press Ctrl+C to stop.")


try:

    while True:

        frame = camera.capture_array()

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_RGB2GRAY
        )

        faces = face_detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(80, 80)
        )

        # For this prototype, only recognize when
        # exactly one face is visible.
        if len(faces) != 1:

            last_person = None
            match_count = 0

            if len(faces) == 0:
                print("No face")
            else:
                print("Multiple faces detected - not unlocking")

            time.sleep(0.25)
            continue


        x, y, w, h = faces[0]

        face = gray[y:y+h, x:x+w]

        face = cv2.resize(
            face,
            (200, 200)
        )

        label, distance = recognizer.predict(face)


        # ---------- CHECK IDENTITY ----------

        if distance < UNKNOWN_THRESHOLD:

            name = names.get(label, "UNKNOWN")

        else:

            name = "UNKNOWN"


        # ---------- UNKNOWN ----------

        if name == "UNKNOWN":

            print(
                f"UNKNOWN | distance: {distance:.1f}"
            )

            last_person = None
            match_count = 0

            time.sleep(0.25)
            continue


        # ---------- RESIDENT ----------

        if name == last_person:

            match_count += 1

        else:

            last_person = name
            match_count = 1


        print(
            f"{name} | "
            f"distance: {distance:.1f} | "
            f"confirmation: {match_count}/{REQUIRED_MATCHES}"
        )


        # ---------- OPEN DOOR ----------

        if match_count >= REQUIRED_MATCHES:

            current_time = time.time()

            if current_time - last_open_time >= COOLDOWN:

                open_door(name)

                last_open_time = time.time()

            # Require recognition sequence again
            match_count = 0
            last_person = None


        time.sleep(0.25)


except KeyboardInterrupt:

    print("\nStopping system...")


finally:

    camera.stop()
    servo.detach()

    print("Camera stopped.")
    print("Servo disabled.")
