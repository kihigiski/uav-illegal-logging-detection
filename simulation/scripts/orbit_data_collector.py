import airsim
import cv2
import numpy as np
import math
import os
import time
from ultralytics import YOLO

# --- 1. SETUP ---
dataset_dir = "logger_dataset"
os.makedirs(dataset_dir, exist_ok=True)
print(f"Saving dataset to: {dataset_dir}")

print("Loading YOLO...")
model = YOLO('logger_detector.pt')

print("Connecting to AirSim...")
client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)

# Turn on the motors and hover so gravity doesn't pull the drone down
print("Starting motors to stabilize camera...")
client.armDisarm(True)
client.takeoffAsync().join()

# Tilt the camera gimbal down just slightly (-5 degrees) since we lowered the altitude
pitch_down = math.radians(-5) 
client.simSetCameraPose("0", airsim.Pose(airsim.Vector3r(0, 0, 0), airsim.to_quaternion(pitch_down, 0, 0)))

TARGET_NAME = "BP_LoggerCharacter_2"
print(f"Locating {TARGET_NAME}...")
target_pose = client.simGetObjectPose(TARGET_NAME)

if math.isnan(target_pose.position.x_val):
    print(f"ERROR: Cannot find {TARGET_NAME}.")
    exit()

tx = target_pose.position.x_val
ty = target_pose.position.y_val

# --- 2. PHOTOSHOOT CONFIG ---
# YOUR ADJUSTMENTS: Reversing the drone and dropping the altitude
radius = 6.0      # Moved back to 6 meters
height = -1.0     # Lowered altitude to 1 meter high (-Z is UP)
images_saved = 0

print("\n--- STARTING DATA COLLECTION ---")

# --- 3. TELEPORT & SNAP LOOP ---
for angle_deg in np.arange(0, 360, 0.5):
    angle_rad = math.radians(angle_deg)
    
    # Calculate circle coordinates around the target
    cam_x = tx + radius * math.cos(angle_rad)
    cam_y = ty + radius * math.sin(angle_rad)
    
    # Calculate the exact yaw (rotation) needed to look AT the target
    yaw = math.atan2(ty - cam_y, tx - cam_x)
    
    # Teleport the drone
    pose = airsim.Pose(airsim.Vector3r(cam_x, cam_y, height), airsim.to_quaternion(0, 0, yaw))
    client.simSetVehiclePose(pose, True)
    
    # Wait 0.03s (approx 30 FPS) to capture the fast axe animation
    time.sleep(0.03)
    
    # Capture the image from Camera "0"
    responses = client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.Scene, False, True)])
    
    if responses and responses[0].image_data_uint8:
        img1d = np.frombuffer(responses[0].image_data_uint8, dtype=np.uint8)
        frame = cv2.imdecode(img1d, cv2.IMREAD_COLOR)
        
        # Draw a crosshair in the exact center of the screen to verify aim
        h, w, _ = frame.shape
        cv2.drawMarker(frame, (w//2, h//2), (0, 0, 255), cv2.MARKER_CROSS, 20, 2)
        
        # FPS Timing added around YOLO Inference
        start_time = time.time()
        results = model(frame, conf=0.5, verbose=False)
        end_time = time.time()
        
        inference_time = end_time - start_time
        fps = 1.0 / inference_time if inference_time > 0 else 0.0
        
        annotated_frame = results[0].plot()
        
        # Draw the FPS label onto the frame
        cv2.putText(annotated_frame, f"FPS: {fps:.1f}", (15, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
        
        # Save it
        if len(results[0].boxes) > 0:
            filename = os.path.join(dataset_dir, f"logger_detect_{images_saved:04d}.jpg")
            cv2.imwrite(filename, annotated_frame)
            print(f"[{angle_deg:.1f}°] Success: Saved {filename} (FPS: {fps:.1f})")
            images_saved += 1
        else:
            print(f"[{angle_deg:.1f}°] Missed: Target out of frame or obscured.")
            
        # Show what the drone sees
        cv2.imshow("Photoshoot Feed - Press Q to abort", annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

print("\n--- DATA COLLECTION COMPLETE ---")
print(f"Total images saved: {images_saved}")

client.enableApiControl(False)
cv2.destroyAllWindows()