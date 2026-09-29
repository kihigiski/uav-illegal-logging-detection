import airsim
import numpy as np

print("Initiating AirSim Connection Test (FT-01)")

# 1. Establish connection (This handles the API Ping)
client = airsim.VehicleClient()
client.confirmConnection()
print("\n PROOF 1: Handshake successful!")

# 2. Retrieve a raw RGB frame from the drone's front camera
print("Requesting uncompressed RGB frame from Unreal Engine")
responses = client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)])

# 3. Convert the byte data into a mathematical matrix (NumPy Array)
if responses and len(responses) > 0:
    response = responses[0]
    img1d = np.frombuffer(response.image_data_uint8, dtype=np.uint8)
    
    # Reshape it using the height and width AirSim provided
    frame = img1d.reshape(response.height, response.width, 3)

    # Print the final shape for your documentation
    print(f" PROOF 2: Array shape verified as {frame.shape} (Height, Width, Channels)")
else:
    print(" ERROR: Did not receive an image.")