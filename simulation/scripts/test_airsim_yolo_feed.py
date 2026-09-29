import airsim
import cv2
import numpy as np
from ultralytics import YOLO

# 1. Load the YOLOv8 model
# change 'yolov8s.pt' to your custom file name!
print("Loading YOLOv8 model...")
model = YOLO('yolov8s.pt') 

# 2. Connect to the AirSim Drone
print("Connecting to Unreal Engine...")
client = airsim.MultirotorClient()
client.confirmConnection()

print("Connection established! Opening camera feed. Press 'q' in the window to quit.")

while True:
    # 3. Grab the front camera image from the drone (Camera ID "0")
    # We request it as a compressed image (True) so OpenCV can easily decode it
    responses = client.simGetImages([
        airsim.ImageRequest("0", airsim.ImageType.Scene, False, True)
    ])
    response = responses[0]
    
    # 4. Convert the AirSim image into a format OpenCV and YOLO understand
    if not response.image_data_uint8:
        continue
        
    img1d = np.frombuffer(response.image_data_uint8, dtype=np.uint8)
    frame = cv2.imdecode(img1d, cv2.IMREAD_COLOR)
    
    if frame is None:
        continue

    # 5. Run YOLOv8 inference on the frame
    # We set conf=0.5 to only show confident detections, reducing false positives in the noisy forest
    results = model(frame, conf=0.5, verbose=False)
    
    # 6. Draw the bounding boxes on the frame
    annotated_frame = results[0].plot()
    
    # 7. Show the video feed on your screen
    cv2.imshow("AirSim Drone View - YOLOv8", annotated_frame)
    
    # Press 'q' to break the loop and close the window
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()