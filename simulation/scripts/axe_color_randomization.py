import airsim
import cv2
import numpy as np
import os
import time
import math
import random 

# --- CONFIGURATION ---
SCENARIO = "chainsaw_color_randomized"
BASE_PATH = r"C:\Users\admin\Desktop\Simon\Simon (2)\IS Dissertation\Data Collection\simulation\sim_training_data\chainsaw_color_randomized"
IMG_DIR = os.path.join(BASE_PATH, "images")
LBL_DIR = os.path.join(BASE_PATH, "labels")

# Ensure directories exist
os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(LBL_DIR, exist_ok=True)

CHARACTER_NAME = "BP_Logger_Chainsaw_3"

client = airsim.VehicleClient()
client.confirmConnection()

# --- WEATHER SETUP: CLEAR ---
client.simEnableWeather(False) 
print(f"Weather set to Sunny. Scenario: {SCENARIO}")

ID_MAP = {} 

# --- THE PERFECT ORBIT (LOCKED) ---
target_pos = client.simGetObjectPose(CHARACTER_NAME).position
current_pose = client.simGetVehiclePose()
cam_pos = current_pose.position

radius = math.sqrt((cam_pos.x_val - target_pos.x_val)**2 + (cam_pos.y_val - target_pos.y_val)**2)
height = cam_pos.z_val 
base_pitch, base_roll, _ = airsim.to_eularian_angles(current_pose.orientation)
start_angle = math.atan2(cam_pos.y_val - target_pos.y_val, cam_pos.x_val - target_pos.x_val)

for degree in range(360):
    angle = start_angle + math.radians(degree)
    x = target_pos.x_val + radius * math.cos(angle)
    y = target_pos.y_val + radius * math.sin(angle)
    yaw = angle + math.pi 
    
    new_orientation = airsim.to_quaternion(base_pitch, base_roll, yaw)
    client.simSetVehiclePose(airsim.Pose(airsim.Vector3r(x, y, height), new_orientation), True)
    
    time.sleep(0.1)

    responses = client.simGetImages([
        airsim.ImageRequest("0", airsim.ImageType.Scene, False, False),
        airsim.ImageRequest("0", airsim.ImageType.Segmentation, False, False)
    ])

    # =========================================================
    # --- FIX 1: THE FRAME-DROP SAFETY NET ---
    # =========================================================
    if not responses or len(responses) < 2: 
        continue

    # Check if AirSim handed us an empty/broken image buffer
    if len(responses[0].image_data_uint8) == 0 or len(responses[1].image_data_uint8) == 0:
        print(f"Warning: Dropped frame at degree {degree}. Skipping safely...")
        continue
    # =========================================================

    img_rgb = np.frombuffer(responses[0].image_data_uint8, dtype=np.uint8).reshape(responses[0].height, responses[0].width, 3)
    img_seg = np.frombuffer(responses[1].image_data_uint8, dtype=np.uint8).reshape(responses[1].height, responses[1].width, 3)
    mask = img_seg[:,:,0].astype(np.uint32) + (img_seg[:,:,1].astype(np.uint32) << 8) + (img_seg[:,:,2].astype(np.uint32) << 16)

    # --- AUTO-DISCOVERY ---
    if not ID_MAP:
        unique_ids, counts = np.unique(mask, return_counts=True)
        sorted_indices = np.argsort(counts)[::-1] 
        valid_ids = [unique_ids[i] for i in sorted_indices if unique_ids[i] != 0]
        
        if len(valid_ids) >= 2:
            ID_MAP[valid_ids[0]] = 0 # Logger
            ID_MAP[valid_ids[1]] = 1 # Axe
            print(f"IDs Locked -> Logger: {valid_ids[0]}, Axe: {valid_ids[1]}")
        else:
            print("Waiting for Axe to enter frame...")
            continue

    # =========================================================
    # --- FIX 2: FULL-SPECTRUM DOMAIN RANDOMIZATION (H, S, and V) ---
    # =========================================================
    # Convert to HSV, but upgrade to int16 to prevent math wrap-around errors
    hsv_hacked = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2HSV).astype(np.int16)
    
    for actual_id, yolo_class in ID_MAP.items():
        object_mask = (mask == actual_id)
        
        # 1. Random Hue (0 to 179) - Changes the base pigment
        hue_shift = random.randint(0, 179)
        
        # 2. Random Saturation (-100 to +100) - Negative = grey/faded, Positive = neon
        sat_shift = random.randint(-100, 100)
        
        # 3. Random Value/Brightness (-100 to +100) - Negative = dark (BROWN/BLACK!), Positive = bright
        val_shift = random.randint(-100, 100)
        
        # Apply the shifts safely
        # Hue loops back around at 180
        hsv_hacked[:, :, 0] = np.where(object_mask, (hsv_hacked[:, :, 0] + hue_shift) % 180, hsv_hacked[:, :, 0])
        
        # Saturation and Value must be capped strictly between 0 and 255
        hsv_hacked[:, :, 1] = np.where(object_mask, np.clip(hsv_hacked[:, :, 1] + sat_shift, 0, 255), hsv_hacked[:, :, 1])
        hsv_hacked[:, :, 2] = np.where(object_mask, np.clip(hsv_hacked[:, :, 2] + val_shift, 0, 255), hsv_hacked[:, :, 2])
        
    # Convert back to standard 8-bit RGB image
    img_rgb = cv2.cvtColor(hsv_hacked.astype(np.uint8), cv2.COLOR_HSV2BGR)
    # =========================================================

    preview_img = img_rgb.copy()
    labels_to_save = []

    for actual_id, yolo_class in ID_MAP.items():
        coords = np.column_stack(np.where(mask == actual_id))
        if coords.size > 0:
            y_min, x_min = coords.min(axis=0)
            y_max, x_max = coords.max(axis=0)
            
            if (x_max - x_min) < 4 or (y_max - y_min) < 4:
                continue 

            color = (0, 0, 255) if yolo_class == 0 else (0, 255, 0)
            cv2.rectangle(preview_img, (x_min, y_min), (x_max, y_max), color, 2)
            
            h, w = img_rgb.shape[:2]
            box_w, box_h = (x_max - x_min) / w, (y_max - y_min) / h
            xc, x_min_norm = (x_min + (x_max - x_min)/2) / w, x_min / w
            yc = (y_min + (y_max - y_min)/2) / h
            labels_to_save.append(f"{yolo_class} {xc:.6f} {yc:.6f} {box_w:.6f} {box_h:.6f}")

    cv2.imshow("CV CAPTURE: FULL-SPECTRUM RANDOMIZATION ACTIVE", preview_img)
    
    if labels_to_save:
        filename = f"deg_{degree:03d}"
        cv2.imwrite(os.path.join(IMG_DIR, f"{filename}.jpg"), img_rgb)
        with open(os.path.join(LBL_DIR, f"{filename}.txt"), "w") as f:
            f.write("\n".join(labels_to_save))

    if cv2.waitKey(1) & 0xFF == ord('q'): break

cv2.destroyAllWindows()
print(f"Scenario {SCENARIO} Complete.")