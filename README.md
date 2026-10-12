# Smart AI Doorbell

A Raspberry Pi-powered smart doorbell system featuring real-time facial recognition, automated door control, visitor detection, Bluetooth audio notifications, and a live web dashboard.

Developed by **Nyle Farhan Ul Haq** and **Shivank Chhaya**.

---

## Project Overview

The Smart AI Doorbell combines computer vision, embedded hardware, and web development to demonstrate an intelligent home entry system.

The system uses a Raspberry Pi camera to detect and recognize registered residents. When a recognized resident is confirmed, the Raspberry Pi activates a servo motor to open a miniature cardboard door.

Visitors can press a physical doorbell button to trigger an audio notification and capture a photograph. The system also provides a browser-based dashboard for monitoring activity.

This project is a functional classroom prototype designed to demonstrate the integration of hardware and software.

## Features

### Facial Recognition
- Detects faces using OpenCV's Haar Cascade classifier.
- Recognizes registered residents using Local Binary Patterns Histograms (LBPH).
- Uses multiple consecutive recognition matches to reduce accidental activations.
- Activates a servo motor when an authorized resident is recognized.
- Uses a cooldown period to prevent repeated door activations.

### Smart Doorbell
- Physical push-button connected to the Raspberry Pi.
- Captures visitor photographs with timestamps.
- Plays a doorbell sound through a connected audio device.
- Supports Bluetooth audio output.

### Web Dashboard
- Live camera feed.
- Door and recognition status.
- Visitor activity monitoring.
- Access to recently captured visitor photographs.
- Flask-based web interface with Socket.IO support.

### Automated Door
- Servo motor connected to the Raspberry Pi.
- Opens a miniature cardboard demonstration door.
- Integrates with the facial recognition system.

---

## Hardware

| Component | Purpose |
|---|---|
| Raspberry Pi 3 Model B+ | Main computing device |
| Raspberry Pi Camera Module | Captures video and photographs |
| Push Button | Triggers the doorbell |
| Servo Motor | Controls the demonstration door |
| Breadboard | Supports circuit connections |
| Jumper Wires | Connects hardware components |
| External 5V Power Supply | Powers the servo motor |
| Bluetooth Audio Device | Plays doorbell notifications |
| Cardboard Door Model | Demonstrates automated access |

### GPIO Connections

| Component | Raspberry Pi Connection |
|---|---|
| Doorbell Button | GPIO 17 |
| Button Ground | GND |
| Servo Signal | GPIO 18 |
| Servo Power | External 5V supply |
| Servo Ground | Common ground with Raspberry Pi |
| Camera | Raspberry Pi CSI camera connector |

**Important:** The servo motor should use an appropriate external power supply. The Raspberry Pi and servo power supply must share a common ground.

---

## Technologies Used

- Python
- Raspberry Pi OS
- OpenCV
- OpenCV LBPH Face Recognizer
- Picamera2
- Flask
- Flask-SocketIO
- GPIO Zero
- HTML, CSS, and JavaScript
- Git and GitHub

---

## Repository Structure

```text
Smart-AI-Doorbell/
│
├── smart_system.py
├── collect_faces.py
├── train_faces.py
├── recognize_test.py
├── recognize_servo_WORKING.py
├── face_test.py
├── servo_test.py
├── button.py
├── doorbell.py
├── dashboard.py
├── app.py
│
├── templates/
│   └── index.html
│
├── docs/
│   └── Project documentation
│
├── doorbell.wav
├── requirements.txt
├── .gitignore
└── README.md
```

### Main Files

| File | Description |
|---|---|
| `smart_system.py` | Main integrated smart doorbell application |
| `collect_faces.py` | Collects facial images for resident enrollment |
| `train_faces.py` | Trains the LBPH facial recognition model |
| `recognize_test.py` | Tests facial recognition |
| `recognize_servo_WORKING.py` | Tests recognition with servo activation |
| `face_test.py` | Tests face detection |
| `servo_test.py` | Tests servo motor operation |
| `button.py` | Tests the physical doorbell button |
| `doorbell.py` | Doorbell functionality |
| `dashboard.py` | Dashboard-related functionality |
| `app.py` | Flask application development file |
| `templates/index.html` | Web dashboard interface |
| `doorbell.wav` | Doorbell notification sound |

---

## Installation

### 1. Connect to the Raspberry Pi

Connect your computer and Raspberry Pi to the same network.

Open PowerShell or another terminal and connect using SSH:

```bash
ssh pi@raspberrypi.local
```

If hostname resolution is unavailable, use the Raspberry Pi's current IP address:

```bash
ssh pi@YOUR_PI_IP_ADDRESS
```

### 2. Update the Raspberry Pi

```bash
sudo apt update
sudo apt upgrade -y
```

### 3. Clone the Repository

```bash
cd ~
git clone https://github.com/Nyle1/Smart-AI-Doorbell.git
```

The original application uses paths associated with `~/smart-doorbell`, so place the repository in that directory before running the main program.

For a fresh installation:

```bash
mv ~/Smart-AI-Doorbell ~/smart-doorbell
cd ~/smart-doorbell
```

**Do not run the `mv` command if you already have a working `~/smart-doorbell` directory.** The directory instructions above are intended for fresh installations.

### 4. Install Dependencies

The project requires Python packages and Raspberry Pi system libraries, including:

- OpenCV with facial recognition support
- Picamera2
- Flask
- Flask-SocketIO
- GPIO Zero

See `requirements.txt` and the project documentation for dependency information.

Package availability and installation methods depend on the Raspberry Pi OS version.

### 5. Connect Hardware

Connect the camera, button, and servo according to the hardware configuration above.

Verify the camera and GPIO devices before running the complete system.

### 6. Collect Resident Images

```bash
python3 collect_faces.py
```

Follow the script's enrollment instructions to capture facial images.

### 7. Train the Recognition Model

```bash
python3 train_faces.py
```

The trained model is stored locally and is not included in this public repository.

### 8. Run the Smart Doorbell

```bash
python3 smart_system.py
```

The main application integrates facial recognition, visitor detection, door control, and the dashboard.

### 9. Access the Dashboard

From another device on the same network, open:

```text
http://YOUR_PI_IP_ADDRESS:5000
```

Replace `YOUR_PI_IP_ADDRESS` with the Raspberry Pi's current IP address.

---

## How the System Works

### Resident Recognition

1. The Raspberry Pi camera captures video.
2. OpenCV detects faces in the video stream.
3. The LBPH model compares detected faces against enrolled residents.
4. The system checks for consecutive successful matches.
5. When an authorized resident is confirmed, the servo activates.
6. A cooldown period prevents immediate repeated activation.

### Visitor Doorbell

1. A visitor presses the physical doorbell button.
2. The Raspberry Pi captures a photograph.
3. The photograph is saved locally with a timestamp.
4. The system plays the doorbell notification.
5. Visitor activity becomes available through the dashboard.

---

## Privacy and Security

The project processes facial images and visitor photographs locally on the Raspberry Pi.

The following files and directories should not be uploaded to a public repository:

- `faces/` — Resident training photographs
- `photos/` — Visitor photographs
- `face_model.yml` — Trained facial recognition model
- `face_model_OLD.yml` — Previous recognition model

The facial recognition system is intended for demonstration purposes and should not be treated as a production-grade security or authentication solution.

The web dashboard is intended for use on a trusted local network.

---

## Limitations

- Recognition performance depends on lighting, camera position, and image quality.
- LBPH facial recognition may produce incorrect matches.
- The system uses a miniature cardboard door rather than a real door lock.
- Camera performance is limited by Raspberry Pi hardware resources.
- The prototype has not been security-hardened for internet exposure.

---

## Documentation

Detailed project documentation is available in the [`docs/`](docs/) directory.

The documentation covers the development process, hardware setup, software configuration, and system operation.

---

## Source Code

This repository contains the original Python source code and dashboard files developed and used on the Raspberry Pi.

The project was developed and tested as a classroom prototype. Reproducing the setup on another Raspberry Pi may require adjustments to dependencies, hardware connections, file paths, and audio configuration.

---

## Authors

**Nyle Farhan Ul Haq**  
**Shivank Chhaya**

Smart AI Doorbell — Raspberry Pi Computer Vision and Embedded Systems Project
