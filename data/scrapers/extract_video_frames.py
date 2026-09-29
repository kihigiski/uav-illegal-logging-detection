import os
import cv2
import yt_dlp
import re
import pandas as pd
from datetime import datetime
import time
import hashlib

# --- CONFIGURATION ---
DATA_DIR = "data"
RAW_DIR = os.path.join(DATA_DIR, "raw_video_frames")
LOG_FILE = "source_log_videos.csv"

# --- ACTION CAPTURE SETTINGS ---
SKIP_SECONDS = 0 
CAPTURE_EVERY_SEC = 0.5 
MAX_FRAMES_PER_VIDEO = 2000

# --- VIDEO SOURCES (Mix of URLs and Local File Paths) ---
VIDEO_SOURCES = [
    #"https://www.youtube.com/watch?v=pM7lKsApm6M",
    # You can add local paths like this:
    r"C:\Users\admin\Desktop\Simon\Simon (2)\IS Dissertation\Data Collection\local videos\local_vid5.mp4",
    # "./local_videos/sample_logging.mp4"
]

# --- SETUP ---
if not os.path.exists(RAW_DIR):
    os.makedirs(RAW_DIR)

if os.path.exists(LOG_FILE):
    log_df = pd.read_csv(LOG_FILE)
else:
    log_df = pd.DataFrame(columns=["Image_ID", "Source_Type", "Source_URL", "Date_Accessed", "Notes"])

def append_log(image_id, source_type, source_url, notes=""):
    global log_df
    new_entry = {
        "Image_ID": image_id,
        "Source_Type": source_type,
        "Source_URL": source_url,
        "Date_Accessed": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Notes": notes
    }
    log_df = pd.concat([log_df, pd.DataFrame([new_entry])], ignore_index=True)
    log_df.to_csv(LOG_FILE, index=False)

def extract_video_id(source_string):
    # Check if it's a local file first
    if os.path.isfile(source_string):
        # Return the filename without the extension
        return os.path.splitext(os.path.basename(source_string))[0].replace(" ", "_")
        
    # Try YouTube ID
    match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', source_string)
    if match and "youtube" in source_string:
        return match.group(1)
    
    # Universal fallback for other URLs
    hash_object = hashlib.md5(source_string.encode())
    return "vid_" + hash_object.hexdigest()[:10]

def process_videos():
    print("--- STARTING HYBRID VIDEO EXTRACTION (V5) ---")
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'current_download.%(ext)s', 
        'quiet': False,
        'no_warnings': True,
        'ignoreerrors': True,
        'socket_timeout': 15,
        'retries': 5
    }

    for source in VIDEO_SOURCES:
        video_id = extract_video_id(source)
        print(f"\n------------------------------------------------")
        print(f"Processing: {source} (ID: {video_id})")
        
        save_dir = os.path.join(RAW_DIR, f"yt_{video_id}")
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # Cleanup potential download leftovers before starting
        for f in os.listdir('.'):
            if f.startswith("current_download"):
                try: os.remove(f) 
                except: pass

        video_file_to_process = None
        is_local_file = os.path.isfile(source)

        try:
            if is_local_file:
                print("  > Local file detected. Skipping download.")
                video_file_to_process = source
                source_type_log = "Local Video"
            else:
                print("  > URL detected. Downloading...")
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([source])
                
                # Find the downloaded temporary file
                for f in os.listdir('.'):
                    if f.startswith("current_download") and not f.endswith(".part"):
                        video_file_to_process = f
                        print(f"  > Found downloaded file: {video_file_to_process}")
                        break
                source_type_log = "Web Video"
            
            if not video_file_to_process:
                print("  [Error] Video source could not be resolved. Skipping.")
                continue

            # --- EXTRACT FRAMES ---
            vidcap = cv2.VideoCapture(video_file_to_process)
            if not vidcap.isOpened():
                print(f"  [Error] OpenCV could not open {video_file_to_process}")
                continue

            fps = vidcap.get(cv2.CAP_PROP_FPS)
            if fps == 0 or fps != fps: fps = 30.0 
            total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps
            
            print(f"  Video Length: {duration:.1f}s")
            
            frame_interval = int(fps * CAPTURE_EVERY_SEC)
            if frame_interval < 1: frame_interval = 1 
            
            start_frame = int(fps * SKIP_SECONDS)
            if start_frame >= total_frames: start_frame = 0

            vidcap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            
            count = start_frame
            saved_count = 0
            
            print(f"  Extracting frames to '{save_dir}'...")

            while True:
                success, image = vidcap.read()
                if not success: break 
                
                if (count - start_frame) % frame_interval == 0:
                    image_name = f"frame_{count}.jpg"
                    save_path = os.path.join(save_dir, image_name)
                    cv2.imwrite(save_path, image)
                    append_log(f"yt_{video_id}/{image_name}", source_type_log, source, f"Time: {count/fps:.2f}s")
                    saved_count += 1
                    
                    if saved_count >= MAX_FRAMES_PER_VIDEO: break
                
                count += 1
            
            print(f"  Done. Saved {saved_count} frames.")
            vidcap.release()

        except Exception as e:
            print(f"  [Critical Error] {e}")
        
        finally:
            if 'vidcap' in locals() and vidcap.isOpened(): vidcap.release()
            time.sleep(1)
            
            # SAFE CLEANUP: Only delete files if they start with "current_download"
            # This ensures we NEVER delete your original local video files!
            for f in os.listdir('.'):
                if f.startswith("current_download"):
                    try: os.remove(f)
                    except: pass

if __name__ == "__main__":
    process_videos()
    print(f"\nProcessing Complete.")