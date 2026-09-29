import os
import requests
import re
import urllib.request
import urllib.parse
import pandas as pd
from datetime import datetime


DATA_DIR = "data"
RAW_DIR = os.path.join(DATA_DIR, "raw_images")
LOG_FILE = "source_log_images.csv"

#SEARCH TERMS

BING_QUERIES = [
    "lumberjack using chainsaw action",
    "man cutting tree with axe",
    "arborist chainsaw felling tree",
    "illegal logging activity in forest",
    "person chopping wood with axe",
    "logger operating chainsaw forest",
    "man carrying chainsaw in woods",
    "illegal logger cutting tree",
    "person holding axe in forest",
    "chainsaw operator cutting log"
]

# 200 images per query 
DOWNLOAD_LIMIT_PER_QUERY = 200

# SETUP
if not os.path.exists(RAW_DIR):
    os.makedirs(RAW_DIR)

# Initialize Log
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
    # Save every time to avoid data loss if script crashes
    log_df.to_csv(LOG_FILE, index=False)

def download_bing_images():
    print(f"STARTING BING IMAGE DOWNLOAD (Target: {DOWNLOAD_LIMIT_PER_QUERY} per query)")
    
    # Header to mimic a real browser to avoid being blocked
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    for query in BING_QUERIES:
        print(f"\nSearching: {query}")
        
        # Create a specific folder for this query to keep things organized
        query_folder_name = query.replace(" ", "_")
        save_dir = os.path.join(RAW_DIR, query_folder_name)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        # Encode the query (Fixes the "control character" error)
        encoded_query = urllib.parse.quote(query)
        
        images_collected = 0
        first_image_index = 0
        
        # Pagination Loop: Fetch batches until we hit the limit
        while images_collected < DOWNLOAD_LIMIT_PER_QUERY:
            print(f"  Fetching batch starting at index {first_image_index}...")
            
            # Bing Async URL
            url = f"https://www.bing.com/images/async?q={encoded_query}&first={first_image_index}&count=35&adlt=off"
            
            try:
                req = urllib.request.Request(url, headers=headers)
                resp = urllib.request.urlopen(req)
                html = resp.read().decode('utf-8')
                
                # Regex to find image links (murl)
                links = re.findall('murl&quot;:&quot;(.*?)&quot;', html)
                
                if not links:
                    print("  No more links found for this query.")
                    break

                for link in links:
                    if images_collected >= DOWNLOAD_LIMIT_PER_QUERY:
                        break
                    
                    try:
                        # Timeout set to 3s to skip slow servers quickly
                        img_data = requests.get(link, timeout=3).content
                        
                        filename = f"img_{images_collected}.jpg"
                        file_path = os.path.join(save_dir, filename)
                        
                        with open(file_path, 'wb') as f:
                            f.write(img_data)
                            
                        append_log(f"{query_folder_name}/{filename}", "Bing Search", link, f"Query: {query}")
                        images_collected += 1
                        
                        if images_collected % 20 == 0:
                            print(f"    Downloaded {images_collected}/{DOWNLOAD_LIMIT_PER_QUERY}...")
                        
                    except Exception:
                        # Skip failed downloads silently
                        continue
                
                # Move the index forward for the next batch
                first_image_index += 35
                
            except Exception as e:
                print(f"  Error processing batch: {e}")
                break
        
        print(f"  Finished query: {query}. Total collected: {images_collected}")

if __name__ == "__main__":
    download_bing_images()
    print(f"\nDone! Check '{RAW_DIR}' for your images.")