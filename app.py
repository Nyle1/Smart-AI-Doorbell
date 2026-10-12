from flask import Flask, Response, send_from_directory
from picamera2 import Picamera2
from gpiozero import Button
from datetime import datetime
from signal import pause
import threading
import time
import os
import cv2

app = Flask(__name__)

PHOTO_DIR = os.path.expanduser("~/smart-doorbell/photos")
os.makedirs(PHOTO_DIR, exist_ok=True)

# ---------------- CAMERA ----------------

camera = Picamera2()

config = camera.create_video_configuration(
    main={"size": (640, 480), "format": "RGB888"}
)

camera.configure(config)
camera.start()

time.sleep(2)

camera_lock = threading.Lock()

# ---------------- BUTTON ----------------

button = Button(17, pull_up=True, bounce_time=0.2)


def take_visitor_photo():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"visitor_{timestamp}.jpg"
    filepath = os.path.join(PHOTO_DIR, filename)

    print("DING DONG!")
    print("Taking visitor photo...")

    with camera_lock:
        frame = camera.capture_array()

    cv2.imwrite(filepath, frame)

    print(f"Saved: {filepath}")


button.when_pressed = take_visitor_photo

# ---------------- LIVE VIDEO ----------------

def generate_frames():

    while True:

        with camera_lock:
            frame = camera.capture_array()

        success, buffer = cv2.imencode(".jpg", frame)

        if not success:
            continue

        frame_bytes = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            frame_bytes +
            b"\r\n"
        )

        # About 10 FPS - easier on Pi 3
        time.sleep(0.1)


@app.route("/video_feed")
def video_feed():

    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# ---------------- SAVED PHOTOS ----------------

@app.route("/photos/<path:filename>")
def photos(filename):

    return send_from_directory(PHOTO_DIR, filename)


# ---------------- DASHBOARD ----------------

@app.route("/")
def home():

    photos = [
        f for f in os.listdir(PHOTO_DIR)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    photos.sort(
        key=lambda f: os.path.getmtime(
            os.path.join(PHOTO_DIR, f)
        ),
        reverse=True
    )

    cards = ""

    for photo in photos:

        path = os.path.join(PHOTO_DIR, photo)

        timestamp = datetime.fromtimestamp(
            os.path.getmtime(path)
        ).strftime("%B %d, %Y at %I:%M:%S %p")

        cards += f"""
        <div class="visitor">
            <img src="/photos/{photo}">
            <div class="info">
                <strong>{timestamp}</strong>
                <br>
                {photo}
            </div>
        </div>
        """

    return f"""
    <!DOCTYPE html>

    <html>

    <head>

        <title>Smart Doorbell</title>

        <meta http-equiv="refresh" content="10">

        <style>

        body {{
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f4f4f4;
        }}

        header {{
            background: #202020;
            color: white;
            padding: 25px;
            text-align: center;
        }}

        .container {{
            max-width: 900px;
            margin: auto;
            padding: 25px;
        }}

        .status {{
            background: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}

        .online {{
            color: green;
            font-weight: bold;
        }}

        .live {{
            background: white;
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 30px;
        }}

        .live img {{
            width: 100%;
            max-width: 640px;
            display: block;
            margin: auto;
            border-radius: 8px;
        }}

        .visitor {{
            background: white;
            margin-bottom: 25px;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,.15);
        }}

        .visitor img {{
            width: 100%;
            display: block;
        }}

        .info {{
            padding: 15px;
        }}

        </style>

    </head>

    <body>

        <header>

            <h1>Smart Doorbell</h1>
            <p>Raspberry Pi Visitor Monitor</p>

        </header>

        <div class="container">

            <div class="status">

                System:
                <span class="online">● ONLINE</span>

                <br><br>

                Visitors recorded: {len(photos)}

            </div>

            <div class="live">

                <h2>Live Camera</h2>

                <img src="/video_feed">

            </div>

            <h2>Visitor History</h2>

            {cards}

        </div>

    </body>

    </html>
    """


# ---------------- START SERVER ----------------

if __name__ == "__main__":

    print("Starting Smart Doorbell...")
    print("Press the physical button to capture a visitor.")

    app.run(
        host="0.0.0.0",
        port=5000,
        threaded=True
    )
