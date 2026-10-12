import cv2
import time
from camera_utils import start_camera
from config import CASCADE_PATH, MODEL_PATH, RESIDENTS, UNKNOWN_THRESHOLD

model = cv2.face.LBPHFaceRecognizer_create()
model.read(str(MODEL_PATH))
detector = cv2.CascadeClassifier(CASCADE_PATH)
camera = start_camera()
try:
    for _ in range(200):
        frame = camera.capture_array()
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        faces = detector.detectMultiScale(gray, 1.2, 5)
        if len(faces) == 1:
            x, y, w, h = faces[0]
            face = cv2.resize(gray[y:y+h, x:x+w], (160, 160))
            label, distance = model.predict(face)
            name = RESIDENTS.get(label, "UNKNOWN") if distance < UNKNOWN_THRESHOLD else "UNKNOWN"
            print(f"{name} | LBPH distance: {distance:.1f}")
        time.sleep(0.15)
finally:
    camera.stop()
