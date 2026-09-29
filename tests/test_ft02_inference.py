from ultralytics import YOLO
import time
import os

print("Initiating Inference Engine Test (FT-02)")

# 1. Defensible Proof 1: Model Loading
try:
    model = YOLO('best.pt')
    print(f"PROOF 1: YOLO weights loaded successfully. Classes recognized: {model.names}")
except Exception as e:
    print(f"ERROR loading model: {e}")

# 2. Defensible Proof 2: Synchronous Processing & Labeling
image_path = 'test_picture.jpg'

if os.path.exists(image_path):
    print(f"\nProcessing {image_path}...")
    
    # Run the image through the AI and time it
    start_time = time.time()
    results = model(image_path, verbose=False) 
    inference_ms = (time.time() - start_time) * 1000
    
    print(f"PROOF 2: Inference completed successfully in {inference_ms:.2f} ms.")
    
    # 3. Defensible Proof 3: Bounding Box and Class Mapping
    detections = results[0].boxes
    if len(detections) > 0:
        print(f"PROOF 3: Found {len(detections)} objects. Verifying class mapping:")
        for box in detections:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            class_name = model.names[class_id]
            print(f"   ➤ Bounding Box generated for: [ {class_name} ] at {confidence*100:.1f}% confidence.")
    else:
        print("PROOF 3: Inference ran, but no objects were detected in this specific image.")
else:
    print(f"ERROR: Please put a '{image_path}' in this folder to run the test.")