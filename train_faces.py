import cv2
import numpy as np
from config import FACE_DIR, MODEL_PATH

if not hasattr(cv2, "face"):
    raise RuntimeError("Install an OpenCV build with the cv2.face module")
images, labels = [], []
for resident_id in (1, 2):
    folder = FACE_DIR / f"resident{resident_id}"
    for path in sorted(folder.glob("*.jpg")):
        image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
        if image is not None:
            images.append(cv2.resize(image, (160, 160)))
            labels.append(resident_id)
if len(set(labels)) != 2:
    raise RuntimeError("Collect training images for both residents first")
model = cv2.face.LBPHFaceRecognizer_create()
model.train(images, np.array(labels, dtype=np.int32))
model.write(str(MODEL_PATH))
print(f"Saved {MODEL_PATH} using {len(images)} images")
