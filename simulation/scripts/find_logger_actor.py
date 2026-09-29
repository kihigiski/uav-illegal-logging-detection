import airsim

client = airsim.MultirotorClient()
client.confirmConnection()

# This grabs every single object name in the current Unreal level
all_objects = client.simListSceneObjects()

print("\n--- SEARCHING FOR LOGGERS ---")
search_term = "Logger" # Or "Character" or "BP"
found_any = False

for obj in all_objects:
    if search_term.lower() in obj.lower():
        print(f"FOUND: {obj}")
        found_any = True

if not found_any:
    print(f"No objects containing '{search_term}' were found.")
    print("Printing first 20 objects as a sample:")
    print(all_objects[:20])