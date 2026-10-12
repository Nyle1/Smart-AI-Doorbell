import threading
from picamera2 import Picamera2
from config import CAMERA_SIZE

camera_lock = threading.Lock()

def start_camera():
    camera = Picamera2()
    config = camera.create_video_configuration(
        main={"size": CAMERA_SIZE, "format": "RGB888"}
    )
    camera.configure(config)
    camera.start()
    return camera
