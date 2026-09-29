import os
import pandas as pd


DATA_DIR = "data"
RAW_DIR = os.path.join(DATA_DIR, "raw_images")
LOG_FILE = "source_log_images.csv"

def sync_log_with_files():
    print("STARTING LOG SYNC")
    
    if not os.path.exists(LOG_FILE):
        print("Error: Log file not found.")
        return

    # Load the current log
    df = pd.read_csv(LOG_FILE)
    print(f"Original Log Entries: {len(df)}")
    
    # List to track valid indices
    valid_indices = []
    files_found_on_disk = 0
    
    for index, row in df.iterrows():
        # The 'Image_ID' column stores the relative path (e.g., "query_folder/img_1.jpg")
        relative_path = row['Image_ID']
        full_path = os.path.join(RAW_DIR, relative_path)
        
        # Check if the file actually exists
        if os.path.exists(full_path):
            valid_indices.append(index)
            files_found_on_disk += 1
        else:
            # Optional: Print what is being removed
            # print(f"Removing entry for deleted file: {relative_path}")
            pass

    # Create a new DataFrame with only the valid rows
    clean_df = df.loc[valid_indices]
    
    # Save back to CSV
    clean_df.to_csv(LOG_FILE, index=False)
    
    print(f"Sync Complete.")
    print(f"Entries Removed: {len(df) - len(clean_df)}")
    print(f"New Log Count: {len(clean_df)}")

if __name__ == "__main__":
    # Safety check
    confirm = input(f"This will update '{LOG_FILE}' to match the files currently in '{RAW_DIR}'.\nAny log entries for missing files will be DELETED.\nType 'yes' to proceed: ")
    if confirm.lower() == 'yes':
        sync_log_with_files()
    else:
        print("Operation cancelled.")