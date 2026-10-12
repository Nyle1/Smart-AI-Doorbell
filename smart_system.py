"""Raspberry Pi smart doorbell demo: local photos, dashboard, LBPH, servo."""
import subprocess
import threading
import time
from datetime import datetime
import cv2
from flask import Flask, Response, jsonify, render_template, send_from_directory
from flask_socketio import SocketIO
from gpiozero import Button, Servo
from camera_utils import start_camera, camera_lock
from config import (
    PHOTO_DIR, MODEL_PATH, SOUND_PATH, CASCADE_PATH, BUTTON_PIN,
    SERVO_PIN, RESIDENTS, UNKNOWN_THRESHOLD, REQUIRED_MATCHES,
    OPEN_SECONDS, COOLDOWN_SECONDS
)

PHOTO_DIR.mkdir(parents=True, exist_ok=True)
app = Flask(__name__)
socketio = SocketIO(app, async_mode="threading")
camera = start_camera()
detector = cv2.CascadeClassifier(CASCADE_PATH)
if detector.empty():
    raise RuntimeError("Face cascade missing: " + CASCADE_PATH)
model = None
if MODEL_PATH.exists():
    model = cv2.face.LBPHFaceRecognizer_create()
    model.read(str(MODEL_PATH))

servo = Servo(SERVO_PIN)
button = Button(BUTTON_PIN, pull_up=True, bounce_time=0.15)
state_lock = threading.Lock()
state = {"detected": "NONE", "access": "WAITING", "door": "CLOSED",
         "distance": None, "confirmation": 0}
last_open = 0.0
consecutive = 0
last_label = None
door_busy = False

def set_state(**kwargs):
    with state_lock:
        state.update(kwargs)

def open_cardboard_door():
    global door_busy
    try:
        set_state(door="OPEN")
        servo.max()
        time.sleep(0.8)
        servo.detach()
        time.sleep(OPEN_SECONDS)
        servo.min()
        time.sleep(0.8)
        servo.detach()
        set_state(door="CLOSED")
    finally:
        door_busy = False

def doorbell_pressed():
    if SOUND_PATH.exists():
        subprocess.Popen(["pw-play", str(SOUND_PATH)],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    filename = "visitor_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f") + ".jpg"
    try:
        with camera_lock:
            frame = camera.capture_array()
        # Picamera2 RGB888 frames: convert to BGR for OpenCV image saving.
        bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        if cv2.imwrite(str(PHOTO_DIR / filename), bgr):
            socketio.emit("new_visitor", {"filename": filename,
                           "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            print("Saved visitor:", filename)
    except Exception as exc:
        print("Photo capture error:", exc)

button.when_pressed = doorbell_pressed

def frames():
    global last_open, consecutive, last_label, door_busy
    while True:
        with camera_lock:
            frame = camera.capture_array()
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        faces = detector.detectMultiScale(gray, 1.2, 5, minSize=(60, 60))
        label = None
        distance = None
        name = "NONE" if len(faces) == 0 else "UNKNOWN"
        if len(faces) == 1 and model is not None:
            x, y, w, h = faces[0]
            face = cv2.resize(gray[y:y+h, x:x+w], (160, 160))
            predicted, distance = model.predict(face)
            if distance < UNKNOWN_THRESHOLD and predicted in RESIDENTS:
                label = predicted
                name = RESIDENTS[predicted]
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        if label is not None and label == last_label:
            consecutive += 1
        elif label is not None:
            consecutive = 1
        else:
            consecutive = 0
        last_label = label
        authorized = label is not None
        set_state(detected=name, access="AUTHORIZED" if authorized else "DENIED",
                  distance=round(float(distance), 1) if distance is not None else None,
                  confirmation=min(consecutive, REQUIRED_MATCHES))
        if (authorized and consecutive >= REQUIRED_MATCHES and not door_busy
                and time.monotonic() - last_open >= COOLDOWN_SECONDS):
            last_open = time.monotonic()
            door_busy = True
            threading.Thread(target=open_cardboard_door, daemon=True).start()
            consecutive = 0
        cv2.putText(frame, name, (15, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (255, 255, 255), 2)
        ok, encoded = cv2.imencode(".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        if ok:
            yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" +
                   encoded.tobytes() + b"\r\n")
        time.sleep(0.08)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/video_feed")
def video_feed():
    return Response(frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/status")
def status():
    with state_lock:
        return jsonify(dict(state))

@app.route("/visitor_history")
def visitor_history():
    files = sorted(PHOTO_DIR.glob("visitor_*.jpg"),
                   key=lambda p: p.stat().st_mtime, reverse=True)[:10]
    return jsonify([{"filename": p.name,
                     "timestamp": datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")}
                    for p in files])

@app.route("/photos/<path:filename>")
def photo(filename):
    return send_from_directory(PHOTO_DIR, filename)

if __name__ == "__main__":
    try:
        socketio.run(app, host="0.0.0.0", port=5000,
                     debug=False, use_reloader=False,
                     allow_unsafe_werkzeug=True)
    finally:
        button.close()
        servo.close()
        camera.stop()
