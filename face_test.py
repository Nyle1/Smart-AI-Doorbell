from picamera2 import Picamera2
import cv2
import time

CASCADE = "/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml"

face_detector = cv2.CascadeClassifier(CASCADE)

camera = Picamera2()

config = camera.create_video_configuration(
    main={"size": (640, 480), "format": "RGB888"}
)

camera.configure(config)
camera.start()

time.sleep(2)

print("Face detection started.")
print("Stand in front of the camera.")
print("Press Ctrl+C to stop.")

try:
    while True:

        frame = camera.capture_array()

        # Convert image to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        # Search for faces
        faces = face_detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(80, 80)
        )

        if len(faces) == 0:
            print("No face")

        else:
            print(f"FACE DETECTED! Number of faces: {len(faces)}")

        time.sleep(0.25)

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    camera.stop()
