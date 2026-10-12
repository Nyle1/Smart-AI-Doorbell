from flask import Flask, Response, send_from_directory
from flask_socketio import SocketIO
from picamera2 import Picamera2
from gpiozero import Servo, Button
from datetime import datetime

import cv2
import threading
import subprocess
import time
import os


# ============================================================
# FLASK + SOCKET.IO
# ============================================================

app = Flask(__name__)

socketio = SocketIO(
    app,
    async_mode="threading",
    cors_allowed_origins="*"
)


# ============================================================
# SETTINGS
# ============================================================

PHOTO_DIR = os.path.expanduser(
    "~/smart-doorbell/photos"
)

CASCADE = (
    "/usr/share/opencv4/haarcascades/"
    "haarcascade_frontalface_default.xml"
)

MODEL = os.path.expanduser(
    "~/smart-doorbell/face_model.yml"
)

DOORBELL_SOUND = os.path.expanduser(
    "~/smart-doorbell/doorbell.wav"
)

SERVO_PIN = 18
BUTTON_PIN = 17

UNKNOWN_THRESHOLD = 55

REQUIRED_MATCHES = 5

DOOR_OPEN_TIME = 3

COOLDOWN = 10

MAX_VISITOR_CARDS = 10


os.makedirs(
    PHOTO_DIR,
    exist_ok=True
)


# ============================================================
# FACE RECOGNITION
# ============================================================

face_detector = cv2.CascadeClassifier(
    CASCADE
)

recognizer = cv2.face.LBPHFaceRecognizer_create()

recognizer.read(
    MODEL
)

names = {
    1: "RESIDENT 1",
    2: "RESIDENT 2"
}


# ============================================================
# CAMERA
# ============================================================

camera = Picamera2()

config = camera.create_video_configuration(
    main={
        "size": (640, 480),
        "format": "RGB888"
    }
)

camera.configure(
    config
)

camera.start()

time.sleep(2)

camera_lock = threading.Lock()


# ============================================================
# SERVO
# ============================================================

servo = Servo(
    SERVO_PIN
)

servo.min()

time.sleep(1)

servo.detach()

door_lock = threading.Lock()


# ============================================================
# BUTTON
# ============================================================

button = Button(
    BUTTON_PIN,
    pull_up=True,
    bounce_time=0.2
)


# ============================================================
# SHARED STATUS
# ============================================================

current_name = "NO FACE"

current_distance = None

current_confirmation = 0

last_person = None

match_count = 0

last_open_time = 0

door_status = "CLOSED"

status_lock = threading.Lock()


# ============================================================
# DOORBELL SOUND
# ============================================================

def play_doorbell_sound():

    try:

        subprocess.Popen(
            [
                "pw-play",
                DOORBELL_SOUND
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        print(
            "Doorbell sound playing."
        )

    except Exception as error:

        print(
            f"Doorbell sound error: {error}"
        )


# ============================================================
# DOORBELL BUTTON PRESS
# ============================================================

def doorbell_pressed():

    print()
    print("==============================")
    print("DING DONG!")
    print("==============================")

    # Play sound immediately
    play_doorbell_sound()


    # --------------------------------------------------------
    # CREATE UNIQUE FILE
    # --------------------------------------------------------

    timestamp = datetime.now()

    filename = (
        "visitor_"
        + timestamp.strftime(
            "%Y-%m-%d_%H-%M-%S-%f"
        )
        + ".jpg"
    )

    filepath = os.path.join(
        PHOTO_DIR,
        filename
    )


    # --------------------------------------------------------
    # TAKE PHOTO
    # --------------------------------------------------------

    print(
        "Taking visitor photo..."
    )

    try:

        with camera_lock:

            frame = camera.capture_array()


        success = cv2.imwrite(
            filepath,
            frame
        )


        if not success:

            print(
                "Photo could not be saved."
            )

            return


        print(
            f"Photo saved: {filepath}"
        )


        # ----------------------------------------------------
        # SEND NEW VISITOR THROUGH WEBSOCKET
        # ----------------------------------------------------

        visitor_data = {

            "filename": filename,

            "timestamp": timestamp.strftime(
                "%B %d, %Y at %I:%M:%S %p"
            )
        }


        socketio.emit(
            "new_visitor",
            visitor_data
        )


        print(
            "New visitor sent to dashboard."
        )


    except Exception as error:

        print(
            f"Photo error: {error}"
        )


button.when_pressed = doorbell_pressed


# ============================================================
# OPEN CARDBOARD DOOR
# ============================================================

def open_door(name):

    global door_status
    global last_open_time


    if not door_lock.acquire(
        blocking=False
    ):

        return


    try:

        print()
        print("==============================")
        print(
            f"AUTHORIZED: {name}"
        )
        print(
            "OPENING CARDBOARD DOOR"
        )
        print("==============================")


        with status_lock:

            door_status = "OPENING"


        servo.max()

        time.sleep(0.8)

        servo.detach()


        with status_lock:

            door_status = "OPEN"


        time.sleep(
            DOOR_OPEN_TIME
        )


        print(
            "Closing cardboard door..."
        )


        with status_lock:

            door_status = "CLOSING"


        servo.min()

        time.sleep(0.8)

        servo.detach()


        with status_lock:

            door_status = "CLOSED"


        last_open_time = time.time()


        print(
            "Door closed."
        )


    finally:

        door_lock.release()


# ============================================================
# PROCESS CAMERA FRAME
# ============================================================

def process_frame(frame):

    global current_name
    global current_distance
    global current_confirmation

    global last_person
    global match_count
    global last_open_time


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


    # --------------------------------------------------------
    # NO FACE
    # --------------------------------------------------------

    if len(faces) == 0:

        last_person = None
        match_count = 0


        with status_lock:

            current_name = "NO FACE"

            current_distance = None

            current_confirmation = 0


        return frame


    # --------------------------------------------------------
    # MULTIPLE FACES
    # --------------------------------------------------------

    if len(faces) != 1:

        last_person = None
        match_count = 0


        with status_lock:

            current_name = "MULTIPLE FACES"

            current_distance = None

            current_confirmation = 0


        return frame


    # --------------------------------------------------------
    # EXACTLY ONE FACE
    # --------------------------------------------------------

    x, y, w, h = faces[0]


    face = gray[
        y:y + h,
        x:x + w
    ]


    face = cv2.resize(
        face,
        (200, 200)
    )


    label, distance = recognizer.predict(
        face
    )


    # --------------------------------------------------------
    # THRESHOLD
    # --------------------------------------------------------

    if distance < UNKNOWN_THRESHOLD:

        name = names.get(
            label,
            "UNKNOWN"
        )

    else:

        name = "UNKNOWN"


    # --------------------------------------------------------
    # UNKNOWN
    # --------------------------------------------------------

    if name == "UNKNOWN":

        last_person = None
        match_count = 0


        with status_lock:

            current_name = "UNKNOWN"

            current_distance = distance

            current_confirmation = 0


    # --------------------------------------------------------
    # RESIDENT
    # --------------------------------------------------------

    else:

        if name == last_person:

            match_count += 1

        else:

            last_person = name

            match_count = 1


        with status_lock:

            current_name = name

            current_distance = distance

            current_confirmation = min(
                match_count,
                REQUIRED_MATCHES
            )


        # ----------------------------------------------------
        # OPEN AFTER REQUIRED MATCHES
        # ----------------------------------------------------

        if match_count >= REQUIRED_MATCHES:

            now = time.time()


            if (
                now - last_open_time >= COOLDOWN
                and not door_lock.locked()
            ):

                threading.Thread(
                    target=open_door,
                    args=(name,),
                    daemon=True
                ).start()


            match_count = 0

            last_person = None


    # --------------------------------------------------------
    # DRAW FACE BOX
    # --------------------------------------------------------

    if name == "UNKNOWN":

        text = (
            f"UNKNOWN ({distance:.1f})"
        )

    else:

        text = (
            f"{name} ({distance:.1f})"
        )


    cv2.rectangle(
        frame,
        (x, y),
        (x + w, y + h),
        (255, 255, 255),
        2
    )


    cv2.putText(
        frame,
        text,
        (
            x,
            max(y - 10, 20)
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )


    return frame


# ============================================================
# LIVE VIDEO
# ============================================================

def generate_frames():

    while True:

        with camera_lock:

            frame = camera.capture_array()


        frame = process_frame(
            frame
        )


        success, buffer = cv2.imencode(
            ".jpg",
            frame
        )


        if not success:

            continue


        frame_bytes = buffer.tobytes()


        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + frame_bytes
            + b"\r\n"
        )


        time.sleep(0.1)


# ============================================================
# VIDEO ROUTE
# ============================================================

@app.route("/video_feed")
def video_feed():

    return Response(
        generate_frames(),

        mimetype=(
            "multipart/x-mixed-replace;"
            " boundary=frame"
        )
    )


# ============================================================
# STATUS API
# ============================================================

@app.route("/status")
def status():

    with status_lock:

        name = current_name

        distance = current_distance

        confirmation = current_confirmation

        door = door_status


    if name in names.values():

        authorization = "AUTHORIZED"

    elif name == "NO FACE":

        authorization = "WAITING"

    else:

        authorization = "NOT AUTHORIZED"


    return {

        "name": name,

        "authorization": authorization,

        "door": door,

        "distance": (
            round(distance, 1)
            if distance is not None
            else None
        ),

        "confirmation": confirmation,

        "required_matches": REQUIRED_MATCHES
    }


# ============================================================
# SERVE PHOTOS
# ============================================================

@app.route("/photos/<path:filename>")
def photos(filename):

    return send_from_directory(
        PHOTO_DIR,
        filename
    )


# ============================================================
# GET EXISTING VISITORS
# Only used ONCE when page initially loads.
# ============================================================

@app.route("/visitor_history")
def visitor_history():

    photo_files = [

        f for f in os.listdir(PHOTO_DIR)

        if f.lower().endswith(
            (
                ".jpg",
                ".jpeg",
                ".png"
            )
        )
    ]


    photo_files.sort(

        key=lambda f:
            os.path.getmtime(
                os.path.join(
                    PHOTO_DIR,
                    f
                )
            ),

        reverse=True
    )


    visitors = []


    for photo in photo_files[
        :MAX_VISITOR_CARDS
    ]:

        path = os.path.join(
            PHOTO_DIR,
            photo
        )


        timestamp = datetime.fromtimestamp(
            os.path.getmtime(path)
        ).strftime(
            "%B %d, %Y at %I:%M:%S %p"
        )


        visitors.append({

            "filename": photo,

            "timestamp": timestamp

        })


    return {
        "visitors": visitors
    }


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/")
def home():

    return """
<!DOCTYPE html>

<html>

<head>

    <title>Smart Doorbell</title>

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1"
    >


    <style>

        body {

            margin: 0;

            font-family:
                Arial,
                sans-serif;

            background: #f4f4f4;

        }


        header {

            background: #202020;

            color: white;

            padding: 22px;

            text-align: center;

        }


        .container {

            max-width: 900px;

            margin: auto;

            padding: 20px;

        }


        .panel {

            background: white;

            padding: 18px;

            border-radius: 12px;

            margin-bottom: 20px;

            box-shadow:
                0 2px 8px rgba(0,0,0,.12);

        }


        .status-grid {

            display: grid;

            grid-template-columns:
                repeat(
                    auto-fit,
                    minmax(150px, 1fr)
                );

            gap: 12px;

        }


        .status-box {

            background: #eeeeee;

            padding: 14px;

            border-radius: 8px;

        }


        .label {

            font-size: 12px;

            text-transform: uppercase;

            color: #555555;

        }


        .value {

            font-size: 20px;

            font-weight: bold;

            margin-top: 5px;

        }


        .live img {

            width: 100%;

            max-width: 640px;

            display: block;

            margin: auto;

            border-radius: 8px;

        }


        .visitor {

            background: white;

            margin-bottom: 20px;

            border-radius: 12px;

            overflow: hidden;

            box-shadow:
                0 2px 8px rgba(0,0,0,.12);

        }


        .visitor img {

            width: 100%;

            display: block;

        }


        .info {

            padding: 14px;

        }


        #socket-status {

            font-size: 13px;

            margin-top: 5px;

            color: #bbbbbb;

        }


        .new-visitor {

            animation:
                visitorArrival 0.5s ease;

        }


        @keyframes visitorArrival {

            from {

                opacity: 0;

                transform:
                    translateY(-15px);

            }

            to {

                opacity: 1;

                transform:
                    translateY(0);

            }

        }

    </style>


    <!-- Socket.IO client served by Flask-SocketIO -->
    <script src="https://cdn.socket.io/4.8.1/socket.io.min.js"></script>

</head>


<body>


<header>

    <h1>
        Smart Doorbell
    </h1>

    <p>
        Face Recognition Access Prototype
    </p>

    <div id="socket-status">
        Connecting...
    </div>

</header>


<div class="container">


    <!-- ================================================== -->
    <!-- STATUS -->
    <!-- ================================================== -->

    <div class="panel">

        <div class="status-grid">


            <div class="status-box">

                <div class="label">
                    System
                </div>

                <div class="value">
                    ONLINE
                </div>

            </div>


            <div class="status-box">

                <div class="label">
                    Detected
                </div>

                <div
                    class="value"
                    id="detected"
                >
                    NO FACE
                </div>

            </div>


            <div class="status-box">

                <div class="label">
                    Access
                </div>

                <div
                    class="value"
                    id="access"
                >
                    WAITING
                </div>

            </div>


            <div class="status-box">

                <div class="label">
                    Door
                </div>

                <div
                    class="value"
                    id="door"
                >
                    CLOSED
                </div>

            </div>


            <div class="status-box">

                <div class="label">
                    LBPH Distance
                </div>

                <div
                    class="value"
                    id="distance"
                >
                    --
                </div>

            </div>


            <div class="status-box">

                <div class="label">
                    Confirmation
                </div>

                <div
                    class="value"
                    id="confirmation"
                >
                    0/5
                </div>

            </div>


        </div>

    </div>


    <!-- ================================================== -->
    <!-- CAMERA -->
    <!-- ================================================== -->

    <div class="panel live">

        <h2>
            Live Camera
        </h2>

        <img
            src="/video_feed"
        >

    </div>


    <!-- ================================================== -->
    <!-- VISITORS -->
    <!-- ================================================== -->

    <h2>
        Doorbell Visitor History
    </h2>


    <div id="visitor-history">

        <div class="panel">
            Loading visitor history...
        </div>

    </div>


</div>


<script>


// ==========================================================
// SOCKET.IO CONNECTION
// ==========================================================

const socket = io();


socket.on(
    "connect",

    function() {

        console.log(
            "WebSocket connected"
        );

        document.getElementById(
            "socket-status"
        ).textContent =
            "Live connection: CONNECTED";

    }
);


socket.on(
    "disconnect",

    function() {

        console.log(
            "WebSocket disconnected"
        );

        document.getElementById(
            "socket-status"
        ).textContent =
            "Live connection: DISCONNECTED";

    }
);


// ==========================================================
// CREATE VISITOR CARD
// ==========================================================

function createVisitorCard(
    visitor,
    animate
) {

    const card =
        document.createElement(
            "div"
        );


    card.className =
        "visitor";


    if (animate) {

        card.classList.add(
            "new-visitor"
        );

    }


    const image =
        document.createElement(
            "img"
        );


    /*
       Unique filename + cache-busting parameter means
       browser cannot accidentally display an older image.
    */

    image.src =
        "/photos/"
        + encodeURIComponent(
            visitor.filename
        )
        + "?v="
        + Date.now();


    image.alt =
        "Doorbell visitor";


    const info =
        document.createElement(
            "div"
        );


    info.className =
        "info";


    const strong =
        document.createElement(
            "strong"
        );


    strong.textContent =
        visitor.timestamp;


    const br =
        document.createElement(
            "br"
        );


    const filename =
        document.createTextNode(
            visitor.filename
        );


    info.appendChild(
        strong
    );

    info.appendChild(
        br
    );

    info.appendChild(
        filename
    );


    card.appendChild(
        image
    );

    card.appendChild(
        info
    );


    return card;

}


// ==========================================================
// INITIAL VISITOR HISTORY
//
// This happens ONE TIME when the page first opens.
// It does NOT continuously refresh.
// ==========================================================

async function loadInitialVisitors() {

    try {

        const response =
            await fetch(
                "/visitor_history",
                {
                    cache: "no-store"
                }
            );


        const data =
            await response.json();


        const container =
            document.getElementById(
                "visitor-history"
            );


        container.innerHTML = "";


        if (
            data.visitors.length === 0
        ) {

            container.innerHTML = `

                <div
                    class="panel"
                    id="no-visitors"
                >

                    No visitor photos yet.

                </div>

            `;

            return;

        }


        data.visitors.forEach(
            function(visitor) {

                const card =
                    createVisitorCard(
                        visitor,
                        false
                    );


                container.appendChild(
                    card
                );

            }
        );

    }

    catch (error) {

        console.log(
            "Initial visitor history failed:",
            error
        );

    }

}


// ==========================================================
// NEW VISITOR WEBSOCKET EVENT
//
// THIS is what happens when GPIO17 is pressed.
// No history refresh.
// No rebuilding old cards.
// ==========================================================

socket.on(
    "new_visitor",

    function(visitor) {

        console.log(
            "New visitor:",
            visitor
        );


        const container =
            document.getElementById(
                "visitor-history"
            );


        const emptyMessage =
            document.getElementById(
                "no-visitors"
            );


        if (emptyMessage) {

            emptyMessage.remove();

        }


        const card =
            createVisitorCard(
                visitor,
                true
            );


        /*
           Insert ONLY the new picture at the top.
        */

        container.prepend(
            card
        );


        /*
           Keep only the newest 10 cards.
           This removes the oldest DOM element only.
           It does NOT reload the other pictures.
        */

        const cards =
            container.querySelectorAll(
                ".visitor"
            );


        if (cards.length > 10) {

            cards[
                cards.length - 1
            ].remove();

        }

    }
);


// ==========================================================
// RECOGNITION STATUS
//
// Keeping the existing lightweight status polling for now.
// Visitor photos themselves are 100% Socket.IO.
// ==========================================================

async function updateStatus() {

    try {

        const response =
            await fetch(
                "/status",
                {
                    cache: "no-store"
                }
            );


        const data =
            await response.json();


        document.getElementById(
            "detected"
        ).textContent =
            data.name;


        document.getElementById(
            "access"
        ).textContent =
            data.authorization;


        document.getElementById(
            "door"
        ).textContent =
            data.door;


        document.getElementById(
            "distance"
        ).textContent =

            data.distance === null

            ? "--"

            : data.distance;


        document.getElementById(
            "confirmation"
        ).textContent =

            data.confirmation

            + "/"

            + data.required_matches;

    }

    catch (error) {

        console.log(
            "Status update failed:",
            error
        );

    }

}


setInterval(
    updateStatus,
    500
);


updateStatus();

loadInitialVisitors();


</script>


</body>

</html>
"""


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print()
    print("==============================")
    print("SMART DOORBELL STARTING")
    print("==============================")

    print(
        f"Recognition threshold: "
        f"{UNKNOWN_THRESHOLD}"
    )

    print(
        f"Required confirmations: "
        f"{REQUIRED_MATCHES}"
    )

    print(
        "Doorbell button: GPIO17"
    )

    print(
        "Cardboard servo: GPIO18"
    )

    print(
        f"Doorbell sound: "
        f"{DOORBELL_SOUND}"
    )

    print(
        "Visitor updates: Socket.IO"
    )

    print()

    print(
        "Open http://localhost:5000"
    )

    print()


    try:

        socketio.run(
            app,

            host="0.0.0.0",

            port=5000,

            debug=False,

            use_reloader=False,

            allow_unsafe_werkzeug=True
        )


    finally:

        camera.stop()

        servo.detach()

        print(
            "System stopped."
        )
