print("Initiating Threat Verification Test (FT-03)")

# 1. This is the custom memory structure from your drone_brain
# It tracks how many consecutive frames an object has been seen.
detection_history = {"axe": 0, "logger": 0, "chainsaw": 0}
ALERT_THRESHOLD = 5

def simulate_frame(frame_number, detected_objects):
    print(f"\n Processing Frame {frame_number} ")
    print(f"AI Detected: {detected_objects}")
    
    alerts_generated = []
    
    # 2. Your Custom Logic: Update history and check threshold
    for obj in detection_history.keys():
        if obj in detected_objects:
            detection_history[obj] += 1
            print(f"   Tracking '{obj}'... (Count: {detection_history[obj]}/{ALERT_THRESHOLD})")
        else:
            if detection_history[obj] > 0:
                print(f"   Lost track of '{obj}'. Resetting count to 0.")
            detection_history[obj] = 0
            
        # Trigger alert ONLY on the exact threshold frame
        if detection_history[obj] == ALERT_THRESHOLD:
            alerts_generated.append(obj)
            
    return alerts_generated

# 3. Defensible Proof: Simulating a flight past an object
# Frames 1-3: We see an Axe
simulate_frame(1, ["axe", "logger"])
simulate_frame(2, ["axe", "logger"])
simulate_frame(3, ["axe"])

# Frame 4: We lose the Axe (maybe a tree blocked it). 
# PROOF: It should reset to 0 and NOT alert.
simulate_frame(4, ["logger"])

# Frames 5-9: We see the Axe clearly for 5 frames straight
simulate_frame(5, ["axe"])
simulate_frame(6, ["axe"])
simulate_frame(7, ["axe"])
simulate_frame(8, ["axe"])
alerts = simulate_frame(9, ["axe"]) # <--- THIS IS THE 5TH CONSECUTIVE FRAME

# 4. Final Verification
if "axe" in alerts:
    print("\n PROOF: THREAT ALERT TRIGGERED EXACTLY ON THE 5TH CONSECUTIVE FRAME!")
else:
    print("\n ERROR: Alert filter failed.")