# Smart AI Doorbell

**Nyle Farhan Ul Haq and Shivank Chhaya**

A Raspberry Pi 3 Model B+ smart doorbell prototype that combines facial recognition, automatic visitor photography, a physical doorbell button, a servo-operated cardboard demonstration door, Bluetooth audio, and a live web dashboard.

This project demonstrates how computer vision, artificial intelligence, and hardware components can work together to create an automated doorbell system.

> **Source Status:** The code in this repository was reconstructed from our development process while the original Raspberry Pi was unavailable. Although the original prototype worked successfully, the reconstructed GitHub files have not yet been fully tested against the original working version.

## Features

- **Facial Recognition:** Uses OpenCV Haar Cascade face detection and LBPH facial recognition to identify registered residents.
- **Automatic Door Opening:** When a registered resident is recognized for five consecutive frames, the servo opens the cardboard demonstration door.
- **Visitor Photography:** Captures and stores timestamped photographs when the doorbell button is pressed.
- **Physical Doorbell:** A push button connected to the Raspberry Pi triggers the doorbell system.
- **Bluetooth Doorbell Chime:** Plays a custom two-tone doorbell sound through a connected Bluetooth audio device.
- **Live Camera Feed:** Streams video from the Raspberry Pi camera to a web dashboard.
- **Web Dashboard:** Displays the camera feed, recognition status, door status, and recent visitor photographs.
- **Real-Time Updates:** Uses Flask-SocketIO to automatically display new visitor photographs without manually refreshing the dashboard.

## Hardware

The project uses the following components:

- Raspberry Pi 3 Model B+
- Raspberry Pi OV5647 Camera Module
- Push button
- Servo motor
- Breadboard
- Jumper wires
- Cardboard demonstration door
- Bluetooth headphones or speaker (optional)

### GPIO Connections

| Component | Raspberry Pi Connection |
| --- | --- |
| Push Button | GPIO17 and GND |
| Servo Signal | GPIO18 |
| Camera | Raspberry Pi CSI Camera Port |
| Servo Power | Suitable separate 5V supply with common ground |

The push button uses the Raspberry Pi's internal pull-up resistor.

**Note:** A keypad was included in the original materials list but was not integrated into the final working prototype. Therefore, no keypad software is included in this repository.

## Project Documentation

Complete step-by-step documentation is available in the repository's documentation folder.

**[View Project Documentation](docs/)**

The documentation includes:

- Project overview and materials
- Raspberry Pi setup
- Hardware connections and wiring illustration
- SSH setup and terminal commands
- Python program setup
- Facial recognition training
- Servo motor configuration
- Bluetooth audio configuration
- Flask web dashboard setup
- Testing procedures and expected outputs
- Troubleshooting

The wiring illustration is intended to demonstrate the general hardware arrangement and should not be treated as a verified electrical schematic.

## Installation

### Step 1: Connect to the Raspberry Pi

Connect to your Raspberry Pi through SSH from another computer.

```bash
ssh pi@raspberrypi.local
```

Enter the Raspberry Pi password when prompted.

### Step 2: Update the Raspberry Pi

```bash
sudo apt update
sudo apt upgrade -y
```

### Step 3: Install Required Packages

```bash
sudo apt install -y git python3-flask python3-flask-socketio \
    python3-opencv opencv-data python3-picamera2 \
    python3-gpiozero python3-numpy
```

These packages provide the libraries needed for:

- Camera access
- Facial recognition
- GPIO control
- Web dashboard functionality
- Real-time visitor updates

### Step 4: Download the GitHub Repository

Clone the repository directly onto the Raspberry Pi.

```bash
cd ~
git clone https://github.com/Nyle1/Smart-AI-Doorbell.git
cd Smart-AI-Doorbell
```

This downloads the project files and opens the project directory.

### Step 5: Verify OpenCV

Check that the facial recognition module is available.

```bash
python3 -c "import cv2; print(cv2.face.LBPHFaceRecognizer_create())"
```

If the command produces an error indicating that `cv2.face` is unavailable, install a compatible OpenCV contrib build for your Raspberry Pi OS environment.

## Facial Recognition Training

The Smart AI Doorbell uses OpenCV's Local Binary Patterns Histograms (LBPH) algorithm to recognize registered residents.

### Step 1: Collect Training Images

With permission from the residents, collect facial images using the Raspberry Pi camera.

```bash
python3 collect_faces.py resident1 --count 100
python3 collect_faces.py resident2 --count 100
```

Each resident has 100 training images.

The photographs are stored locally in the `faces/` directory.

### Step 2: Train the Recognition Model

```bash
python3 train_faces.py
```

The training program creates a facial recognition model saved as:

```text
face_model.yml
```

### Step 3: Test Facial Recognition

```bash
python3 recognize_test.py
```

The system attempts to identify registered residents using the camera.

The prototype uses a recognition-distance threshold of 55, where lower LBPH distances indicate closer matches.

Five consecutive recognized frames are required before the servo opens the demonstration door.

**Privacy Note:** Training images, visitor photographs, and facial recognition models are stored locally and are excluded from this GitHub repository.

## Running the Smart AI Doorbell

### Step 1: Open the Project Directory

```bash
cd ~/Smart-AI-Doorbell
```

If your existing project uses the original `smart-doorbell` folder name, open that directory instead.

### Step 2: Start the System

```bash
python3 smart_system.py
```

The integrated program manages:

- Camera streaming
- Facial recognition
- Doorbell button detection
- Visitor photography
- Servo motor operation
- Bluetooth doorbell audio
- Web dashboard updates

### Step 3: Open the Web Dashboard

On another device connected to the same local network, open:

```text
http://<raspberry-pi-local-ip>:5000
```

Replace `<raspberry-pi-local-ip>` with your Raspberry Pi's actual IP address.

The dashboard displays the live camera feed, system status, and recent visitor photographs.

### Step 4: Stop the Program

Press:

```text
Ctrl + C
```

in the terminal running the program.

## Bluetooth Doorbell Audio

The project includes a custom two-tone doorbell sound stored in:

```text
doorbell.wav
```

The sound is played through the Raspberry Pi's selected audio output using PipeWire.

To test the audio:

```bash
pw-play doorbell.wav
```

If a Bluetooth speaker or headphones are connected and configured as the default audio output, the chime should play through that device.

## Project Files

| File | Description |
| --- | --- |
| `smart_system.py` | Main integrated Smart AI Doorbell program |
| `templates/index.html` | Web dashboard interface |
| `config.py` | GPIO pins, recognition thresholds, and file paths |
| `camera_utils.py` | Camera initialization and access management |
| `collect_faces.py` | Collects resident facial training images |
| `train_faces.py` | Trains the LBPH facial recognition model |
| `recognize_test.py` | Tests facial recognition |
| `face_test.py` | Tests face detection |
| `servo_test.py` | Tests the servo motor |
| `button.py` | Tests the physical doorbell button |
| `doorbell.py` | Tests the doorbell button and audio |
| `doorbell.wav` | Custom two-tone doorbell sound |
| `app.py` | Alternative entry point for the integrated system |
| `dashboard.py` | Alternative dashboard entry point |
| `recognize_servo_WORKING.py` | Alternative recognition and servo entry point |
| `docs/` | Complete project documentation |

## Privacy and Limitations

This project is intended as an educational prototype demonstrating the integration of artificial intelligence, computer vision, and hardware.

- Facial training images and visitor photographs should remain private.
- Facial recognition models and personal information should not be uploaded to public repositories.
- The Flask development server should only be used on a trusted local network.
- Port 5000 should not be exposed directly to the public internet.
- LBPH facial recognition is not sufficiently secure to control a real exterior door lock.
- The servo motor controls a cardboard demonstration door rather than a real door.
- The reconstructed GitHub code should be tested on the Raspberry Pi before being considered a verified reproduction of the original system.

## Authors

**Nyle Farhan Ul Haq**  
**Shivank Chhaya**
