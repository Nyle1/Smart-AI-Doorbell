from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PHOTO_DIR = BASE_DIR / "photos"
FACE_DIR = BASE_DIR / "faces"
MODEL_PATH = BASE_DIR / "face_model.yml"
SOUND_PATH = BASE_DIR / "doorbell.wav"
CASCADE_PATH = "/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml"

BUTTON_PIN = 17
SERVO_PIN = 18
RESIDENTS = {1: "RESIDENT 1", 2: "RESIDENT 2"}
UNKNOWN_THRESHOLD = 55
REQUIRED_MATCHES = 5
OPEN_SECONDS = 3
COOLDOWN_SECONDS = 10
CAMERA_SIZE = (640, 480)
