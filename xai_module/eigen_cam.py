from ultralytics import YOLO
from pytorch_grad_cam import EigenCAM
from pytorch_grad_cam.utils.image import show_cam_on_image
import cv2
import numpy as np
import torch
from pathlib import Path
import matplotlib.pyplot as plt

# Load model
yolo = YOLO("best.pt")
model = yolo.model
model.eval()

# Target layer
target_layers = [model.model[-2]]

# Load test image
image_path = next(Path("data file/test/images").glob("*"))

img = cv2.imread(str(image_path))
img = cv2.resize(img, (640, 640))
rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
rgb_img = rgb_img.astype(np.float32) / 255.0

# Tensor
input_tensor = torch.from_numpy(
    np.transpose(rgb_img, (2, 0, 1))[None, :]
).float()

# EigenCAM
cam = EigenCAM(model=model, target_layers=target_layers)

grayscale_cam = cam(
    input_tensor=input_tensor,
    targets=[None]
)[0]

# Overlay heatmap
cam_image = show_cam_on_image(
    rgb_img,
    grayscale_cam,
    use_rgb=True
)

# Draw YOLO boxes on CAM
cam_with_boxes = results = yolo.predict(img, verbose=False)
cam_with_boxes = results[0].plot()

cam_with_boxes = cv2.cvtColor(
    cam_with_boxes,
    cv2.COLOR_BGR2RGB
)

# Blend CAM and detection boxes
cam_image = cv2.addWeighted(
    cam_image,
    0.7,
    cam_with_boxes,
    0.3,
    0
)

# YOLO detection
results = yolo.predict(img, verbose=False)
detection_image = results[0].plot()
detection_image = cv2.cvtColor(detection_image, cv2.COLOR_BGR2RGB)

# Comparison
plt.figure(figsize=(15, 5))

plt.subplot(1, 3, 1)
plt.imshow(rgb_img)
plt.title("Original")
plt.axis("off")

plt.subplot(1, 3, 2)
plt.imshow(detection_image)
plt.title("YOLO Detection")
plt.axis("off")

plt.subplot(1, 3, 3)
plt.imshow(cam_image)
plt.title("EigenCAM")
plt.axis("off")

plt.tight_layout()

# Save output
output_folder = Path("xai_module/output")
output_folder.mkdir(parents=True, exist_ok=True)

plt.savefig(output_folder / "comparison.jpg", dpi=150)
plt.show()

print("Saved: xai_module/output/comparison.jpg")