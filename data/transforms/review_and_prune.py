import cv2
import os

# --- SET THE FOLDER YOU WANT TO REVIEW ---
FOLDER = r"c:\Users\admin\Desktop\Simon\Simon (2)\IS Dissertation\Data Collection\simulation\sim_training_data\chainsaw_down_sunny"

images_path = os.path.join(FOLDER, "images")
labels_path = os.path.join(FOLDER, "labels")

# Get list of images
image_files = [f for f in os.listdir(images_path) if f.endswith(".jpg")]
image_files.sort()

index = 0
print("--- CONTROLS ---")
print("Space/D: Next Image | A: Previous Image")
print("X: DELETE IMAGE & LABEL (Permanent)")
print("Q: Quit")

while index < len(image_files):
    filename = image_files[index]
    img_full_path = os.path.join(images_path, filename)
    
    # Check if file exists (might have been deleted in this session)
    if not os.path.exists(img_full_path):
        image_files.pop(index)
        continue

    img = cv2.imread(img_full_path)
    if img is None:
        index += 1
        continue
        
    h, w = img.shape[:2]
    label_file = os.path.join(labels_path, filename.replace(".jpg", ".txt"))
    current_labels = []
    
    if os.path.exists(label_file):
        with open(label_file, 'r') as f:
            current_labels = f.readlines()

    # Draw Boxes for Review
    display_img = img.copy()
    for line in current_labels:
        parts = line.split()
        if len(parts) < 5: continue
        
        cls, xc, yc, bw, bh = map(float, parts)
        x1 = int((xc - bw/2) * w)
        y1 = int((yc - bh/2) * h)
        x2 = int((xc + bw/2) * w)
        y2 = int((yc + bh/2) * h)
        
        # Color Coding
        if cls == 0: color, name = (0, 0, 255), "Logger"    # Red
        elif cls == 1: color, name = (0, 255, 0), "Axe"     # Green
        elif cls == 2: color, name = (255, 255, 0), "Saw"   # Cyan
        else: color, name = (255, 255, 255), "Unknown"

        cv2.rectangle(display_img, (x1, y1), (x2, y2), color, 2)
        cv2.putText(display_img, name, (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    cv2.imshow(f"Reviewing: {filename} ({index+1}/{len(image_files)})", display_img)
    
    key = cv2.waitKey(0) & 0xFF

    if key == ord('d') or key == 32: # Space or D for Next
        index += 1
    elif key == ord('a'): # A for Previous
        index = max(0, index - 1)
    elif key == ord('x'): # X to DELETE EVERYTHING
        # Delete Image
        if os.path.exists(img_full_path):
            os.remove(img_full_path)
        # Delete Label
        if os.path.exists(label_file):
            os.remove(label_file)
            
        print(f"DELETED: {filename}")
        # Remove from list and don't increment index (next image slides into current index)
        image_files.pop(index)
    elif key == ord('q'):
        break

cv2.destroyAllWindows()
print("Review Session Finished.")