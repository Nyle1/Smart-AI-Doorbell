from picamera2 import Picamera2
import cv2
import os
import sys
import time

# ============================================================
# SETTINGS
# ============================================================

CASCADE = (
    "/usr/share/opencv4/haarcascades/"
    "haarcascade_frontalface_default.xml"
)

IMAGES_TO_ADD = 70
IMAGE_SIZE = (200, 200)

# ============================================================
# CHOOSE RESIDENT
# ============================================================

if len(sys.argv) != 2:
    print("Usage:")
    print("python3 collect_faces.py resident1")
    print("or")
    print("python3 collect_faces.py resident2")
    sys.exit()

resident = sys.argv[1].lower()

if resident not in ["resident1", "resident2"]:
    print("Resident must be resident1 or resident2")
    sys.exit()

folder = os.path.expanduser(
    f"~/smart-doorbell/faces/{resident}"
)

os.makedirs(folder, exist_ok=True)

# ============================================================
# FIND WHERE TO START
# ============================================================

existing = [
    f for f in os.listdir(folder)
    if f.lower().endswith(
        (".jpg", ".jpeg", ".png")
    )
]

start_number = len(existing) + 1
end_number = len(existing) + IMAGES_TO_ADD

print()
print("==============================")
print(f"Collecting images for {resident}")
print("==============================")
print(f"Existing images: {len(existing)}")
print(f"Adding: {IMAGES_TO_ADD}")
print(f"Final total: {end_number}")
print()
print("Move your face around naturally:")
print("- Look straight ahead")
print("- Slightly left")
print("- Slightly right")
print("- Slightly up")
print("- Slightly down")
print("- Move a little closer/farther")
print()
print("Press Ctrl+C to stop.")
print()

# ============================================================
# CAMERA + FACE DETECTOR
# ============================================================

detector = cv2.CascadeClassifier(CASCADE)

camera = Picamera2()

config = camera.create_video_configuration(
    main={
        "size": (640, 480),
        "format": "RGB888"
    }
)

camera.configure(config)
camera.start()

time.sleep(2)

count = start_number

try:

    while count <= end_number:

        frame = camera.capture_array()

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_RGB2GRAY
        )

        faces = detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(80, 80)
        )

        # Only save when exactly one face is visible
        if len(faces) == 1:

            x, y, w, h = faces[0]

            face = gray[
                y:y+h,
                x:x+w
            ]

            face = cv2.resize(
                face,
                IMAGE_SIZE
            )

            filename = os.path.join(
                folder,
                f"face_{count:03d}.jpg"
            )

            cv2.imwrite(
                filename,
                face
            )

            print(
                f"Saved {resident}: "
                f"{count}/{end_number}"
            )

            count += 1

            # Prevent collecting 70 nearly identical
            # frames instantly.
            time.sleep(0.25)

        else:

            time.sleep(0.05)

finally:

    camera.stop()

    print()
    print("Camera stopped.")

print()
print("==============================")
print("COLLECTION COMPLETE")
print("==============================")
print(f"{resident} now has {end_number} images.")
