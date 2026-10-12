import cv2
import time
from camera_utils import start_camera
from config import CASCADE_PATH

camera = start_camera()
detector = cv2.CascadeClassifier(CASCADE_PATH)
try:
    for _ in range(100):
        frame = camera.capture_array()
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        faces = detector.detectMultiScale(gray, 1.2, 5)
        print(f"Faces detected: {len(faces)}")
        time.sleep(0.15)
finally:
    camera.stop()
