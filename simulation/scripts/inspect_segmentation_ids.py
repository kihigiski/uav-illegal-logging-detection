import airsim
import cv2
import numpy as np

# --- 1. CONNECT TO AIRSIM (NO ID MODIFICATIONS) ---
client = airsim.VehicleClient()
client.confirmConnection()

print("Capturing native, unbroken segmentation frame...")
responses = client.simGetImages([
    airsim.ImageRequest("0", airsim.ImageType.Segmentation, False, False)
])

if not responses:
    print("Error getting images.")
    exit()

# Convert to image array
img_seg = np.frombuffer(responses[0].image_data_uint8, dtype=np.uint8).reshape(responses[0].height, responses[0].width, 3)

# Calculate the bitwise mask for OpenCV logic
mask = (img_seg[:,:,0].astype(np.uint32) +
        (img_seg[:,:,1].astype(np.uint32) << 8) +
        (img_seg[:,:,2].astype(np.uint32) << 16))

# Variables to store the colors you click
clicked_colors = []

# --- 2. THE INTERACTIVE COLOR PICKER ---
def mouse_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        # Get the exact bitwise color ID of the pixel you clicked
        color_id = mask[y, x]
        clicked_colors.append(color_id)
        print(f"Locked Color ID: {color_id} from coordinates (X:{x}, Y:{y})")
        
        # Give visual feedback (draw a white circle where you clicked)
        cv2.circle(img_seg, (x, y), 5, (255, 255, 255), -1)
        cv2.imshow("Click Logger FIRST, then Chainsaw. Press 'q' when done.", img_seg)

cv2.imshow("Click Logger FIRST, then Chainsaw. Press 'q' when done.", img_seg)
cv2.setMouseCallback("Click Logger FIRST, then Chainsaw. Press 'q' when done.", mouse_click)

print("\n--- INSTRUCTIONS ---")
print("1. Click once on the Logger's body.")
print("2. Click once on the Chainsaw.")
print("3. Press 'q' to close the window and see the isolated result.")

cv2.waitKey(0)
cv2.destroyAllWindows()

# --- 3. DIGITAL ISOLATION (THE RESULTS) ---
if len(clicked_colors) >= 2:
    logger_color = clicked_colors[0]
    chainsaw_color = clicked_colors[1]
    
    print("\n--- YOUR HARDCODED DICTIONARY ---")
    print(f"Use this in your main script:")
    print(f"NATIVE_CHARACTER_COLORS = [{logger_color}, {chainsaw_color}]")
    
    # Create a completely black image
    isolated_view = np.zeros_like(img_seg)
    
    # Copy ONLY the pixels that match the two colors you clicked
    isolated_view[mask == logger_color] = [0, 0, 255]   # Paint Logger Red
    isolated_view[mask == chainsaw_color] = [255, 255, 0] # Paint Chainsaw Cyan
    
    cv2.imshow("Isolated Character (Background Deleted)", isolated_view)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("You didn't click both objects. Run again.")