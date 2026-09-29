import cv2
import os

# --- UPDATE THESE TWO PATHS ---
# 1. Pick one specific image from your folder
IMG_FILENAME = "frame_168_jpg.rf.67bdbd5ca7036cef1d2d34a78d4e2390.jpg" 
BASE_DIR = r"C:\Users\admin\Desktop\Simon\Simon (2)\IS Dissertation\Data Collection\datasets\logging_data_v2\train"

img_path = os.path.join(BASE_DIR, "images", IMG_FILENAME)
lbl_path = os.path.join(BASE_DIR, "labels", IMG_FILENAME.replace(".jpg", ".txt"))

# Check if file exists before reading
if not os.path.exists(img_path):
    print(f"ERROR: Image not found at {img_path}")
    exit()

img = cv2.imread(img_path)

if img is None:
    print("ERROR: OpenCV could not load the image. Check the file format.")
    exit()

h, w = img.shape[:2]

# ... (Rest of the script from before)
with open(lbl_path, 'r') as f:
    for line in f.readlines():
        cls, xc, yc, bw, bh = map(float, line.split())
        
        # Draw the box
        x1 = int((xc - bw/2) * w)
        y1 = int((yc - bh/2) * h)
        x2 = int((xc + bw/2) * w)
        y2 = int((yc + bh/2) * h)
        
        # Label according to our NEW Master IDs
        if cls == 0: color, name = (0, 0, 255), "Logger"
        elif cls == 1: color, name = (0, 255, 0), "Axe"
        elif cls == 2: color, name = (255, 255, 0), "Chainsaw"
        else: color, name = (255, 255, 255), "Unknown"

        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        cv2.putText(img, name, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

cv2.imshow("Post-Remap Verify", img)
cv2.waitKey(0)
cv2.destroyAllWindows()