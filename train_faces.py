import cv2
import os
import numpy as np

BASE_DIR = os.path.expanduser("~/smart-doorbell/faces")
MODEL_PATH = os.path.expanduser("~/smart-doorbell/face_model.yml")

people = {
    "resident1": 1,
    "resident2": 2
}

faces = []
labels = []

print("Loading training images...")

for person, label in people.items():

    folder = os.path.join(BASE_DIR, person)

    for filename in os.listdir(folder):

        if not filename.lower().endswith(".jpg"):
            continue

        path = os.path.join(folder, filename)

        image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

        if image is None:
            continue

        image = cv2.resize(image, (200, 200))

        faces.append(image)
        labels.append(label)

    print(f"{person}: loaded training images")

print(f"Total images: {len(faces)}")

recognizer = cv2.face.LBPHFaceRecognizer_create()

recognizer.train(
    faces,
    np.array(labels)
)

recognizer.write(MODEL_PATH)

print("Training complete!")
print(f"Model saved to: {MODEL_PATH}")
