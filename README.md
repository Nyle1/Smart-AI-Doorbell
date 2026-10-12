# Smart AI Doorbell

**Nyle Farhan Ul Haq and Shivank Chhaya**

A Raspberry Pi 3 Model B+ classroom prototype combining a physical
doorbell button, visitor photos, local LBPH face recognition, a
servo-operated **cardboard demo door**, Bluetooth chime and Flask dashboard.

> **Reconstructed source:** These files were recreated from our development
> conversation while the original Raspberry Pi was unavailable. They have
> **not been tested on the actual Pi** and may differ from the final working
> files. Replace them with the originals when available.

## Hardware

- Raspberry Pi 3 Model B+ and OV5647 camera
- Push button: GPIO17 to GND (internal pull-up)
- Servo signal: GPIO18; use a suitable separate 5V servo supply and common ground
- Breadboard and jumper wires
- Optional Bluetooth headphones/speaker for the chime

**No keypad software is included:** the keypad appeared in the initial
materials list but was not part of the verified working setup.

## Install on Raspberry Pi OS

```bash
sudo apt update
sudo apt install -y python3-flask python3-flask-socketio \
    python3-opencv opencv-data python3-picamera2 \
    python3-gpiozero python3-numpy
```

Check that `cv2.face.LBPHFaceRecognizer_create()` is available:

```bash
python3 -c "import cv2; print(cv2.face.LBPHFaceRecognizer_create())"
```

If the installed OpenCV build lacks `cv2.face`, install a compatible
OpenCV contrib build for your Raspberry Pi OS environment.

## Training

With consent from both residents, collect their photos **locally**:

```bash
python3 collect_faces.py resident1 --count 100
python3 collect_faces.py resident2 --count 100
python3 train_faces.py
python3 recognize_test.py
```

`faces/`, `photos/` and `face_model.yml` are excluded from Git.

## Run

```bash
cd ~/smart-doorbell
python3 smart_system.py
```

Visit `http://<raspberry-pi-local-ip>:5000` on your local network.
`doorbell.wav` is played using `pw-play` on the Pi's default audio output.

## Components

| File | Purpose |
| --- | --- |
| `smart_system.py` | Integrated camera, button, recognition, servo and dashboard |
| `templates/index.html` | Live feed, status and visitor history |
| `config.py` | Pins, thresholds and paths |
| `collect_faces.py` | Collect local training images |
| `train_faces.py` | Train LBPH model |
| `recognize_test.py` | Print recognition results |
| `face_test.py` | Check face detection |
| `servo_test.py` | Test cardboard door servo |
| `button.py` | Test push button |
| `doorbell.py` | Button and Bluetooth chime |
| `app.py`, `dashboard.py`, `recognize_servo_WORKING.py` | Convenience entry points to combined system |

## Privacy and limitations

Do not commit identifiable visitor photos, face datasets, credentials
or face model files. The Flask development server is for a trusted
local network only; do not expose port 5000 publicly. LBPH recognition
is **not secure enough to control a real exterior door lock**.
The generated wiring illustration in the documentation is conceptual,
not a verified electrical wiring schematic.
