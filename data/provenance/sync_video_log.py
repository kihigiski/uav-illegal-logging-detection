import os
import pandas as pd

# --- CONFIGURATION ---
DATA_DIR = "data"
RAW_DIR = os.path.join(DATA_DIR, "raw_video_frames")
LOG_FILE = "source_log_videos.csv"

def sync_log_with_files():
    print("--- STARTING VIDEO LOG SYNC ---")
    
    if not os.path.exists(LOG_FILE):
        print(f"Error: Log file '{LOG_FILE}' not found.")
        return

    # Load the current log
    try:
        df = pd.read_csv(LOG_FILE)
        print(f"Original Log Entries: {len(df)}")
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
    
    # List to track valid indices
    valid_indices = []
    files_found_on_disk = 0
    missing_files_count = 0
    
    for index, row in df.iterrows():
        # The 'Image_ID' column stores the relative path (e.g., "yt_VIDEOID/frame_0.jpg")
        relative_path = row['Image_ID']
        full_path = os.path.join(RAW_DIR, relative_path)
        
        # Check if the file actually exists
        if os.path.exists(full_path):
            valid_indices.append(index)
            files_found_on_disk += 1
        else:
            missing_files_count += 1
            # Optional: Uncomment to see exactly what is being removed
            # print(f"  [Removing] Missing file: {relative_path}")

    if missing_files_count == 0:
        print("Log is already perfectly synced. No changes needed.")
        return

    # Create a new DataFrame with only the valid rows
    clean_df = df.loc[valid_indices]
    
    # Save back to CSV
    clean_df.to_csv(LOG_FILE, index=False)
    
    print(f"Sync Complete.")
    print(f"Entries Removed: {len(df) - len(clean_df)}")
    print(f"New Log Count: {len(clean_df)}")

if __name__ == "__main__":
    print(f"Directory to scan: {os.path.abspath(RAW_DIR)}")
    print(f"Log file to update: {os.path.abspath(LOG_FILE)}")
    
    # Safety check
    confirm = input(f"\nThis will update '{LOG_FILE}' to match the files currently in '{RAW_DIR}'.\nAny log entries for missing frames will be DELETED.\nType 'yes' to proceed: ")
    if confirm.lower() == 'yes':
        sync_log_with_files()
    else:
        print("Operation cancelled.")