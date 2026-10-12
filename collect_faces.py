import argparse
import time
import cv2
from camera_utils import start_camera
from config import FACE_DIR, CASCADE_PATH

parser = argparse.ArgumentParser()
parser.add_argument("resident", choices=["resident1", "resident2"])
parser.add_argument("--count", type=int, default=100)
args = parser.parse_args()

folder = FACE_DIR / args.resident
folder.mkdir(parents=True, exist_ok=True)
detector = cv2.CascadeClassifier(CASCADE_PATH)
if detector.empty():
    raise RuntimeError("OpenCV face cascade not found")
camera = start_camera()
saved = 0
try:
    time.sleep(1)
    while saved < args.count:
        frame = camera.capture_array()
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        faces = detector.detectMultiScale(gray, 1.2, 5, minSize=(60, 60))
        if len(faces) == 1:
            x, y, w, h = faces[0]
            face = cv2.resize(gray[y:y+h, x:x+w], (160, 160))
            filename = folder / f"face_{time.time_ns()}.jpg"
            cv2.imwrite(str(filename), face)
            saved += 1
            print(f"{args.resident}: {saved}/{args.count}")
        time.sleep(0.12)
finally:
    camera.stop()
