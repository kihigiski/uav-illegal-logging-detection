import cv2
import time
import numpy as np
from flask import Flask, Response, jsonify
from flask_cors import CORS
from ultralytics import YOLO
import airsim
import sqlite3
from datetime import datetime
import io
import csv

app = Flask(__name__)
CORS(app) 

# --- DATABASE MANAGER ---
class DatabaseLogger:
    def __init__(self, db_name="mission_data.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.current_mission_id = self.start_mission(canopy=0.63)

    def create_tables(self):
        self.cursor.executescript("""
            CREATE TABLE IF NOT EXISTS MISSION (
                mission_id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time DATETIME,
                location_name TEXT,
                canopy_density_setting REAL,
                weather_condition TEXT
            );
            
            CREATE TABLE IF NOT EXISTS DETECTION_EVENT (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                mission_id INTEGER,
                timestamp DATETIME,
                frame_index INTEGER,
                object_class TEXT,
                confidence REAL,
                tracking_id INTEGER,
                gps_lat REAL,
                gps_long REAL,
                inference_ms REAL,
                calc_fps REAL,
                FOREIGN KEY(mission_id) REFERENCES MISSION(mission_id)
            );
            
            CREATE TABLE IF NOT EXISTS ALERT (
                alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER,
                threat_level TEXT,
                verified_visual BOOLEAN,
                FOREIGN KEY(event_id) REFERENCES DETECTION_EVENT(event_id)
            );
        """)
        self.conn.commit()

    def start_mission(self, location="Kereita Forest Reserve - Sector 4", canopy=0.63, weather="Clear"):
        self.cursor.execute("""
            INSERT INTO MISSION (start_time, location_name, canopy_density_setting, weather_condition)
            VALUES (?, ?, ?, ?)
        """, (datetime.now(), location, canopy, weather))
        self.conn.commit()
        return self.cursor.lastrowid

    def log_detection(self, frame_idx, obj_class, conf, track_id, inf_ms, fps, lat=-0.395, lon=36.680):
        self.cursor.execute("""
            INSERT INTO DETECTION_EVENT (mission_id, timestamp, frame_index, object_class, confidence, tracking_id, gps_lat, gps_long, inference_ms, calc_fps)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (self.current_mission_id, datetime.now(), frame_idx, obj_class, conf, track_id, lat, lon, inf_ms, fps))
        self.conn.commit()
        return self.cursor.lastrowid

    def log_alert(self, event_id, threat_level="CRITICAL", verified=True):
        self.cursor.execute("""
            INSERT INTO ALERT (event_id, threat_level, verified_visual)
            VALUES (?, ?, ?)
        """, (event_id, threat_level, verified))
        self.conn.commit()

db_manager = DatabaseLogger()

# 1. ONBOARD AI
model = YOLO('best_optimized.onnx')

# 2. ONBOARD MEMORY STATE
system_state = {
    "telemetry": {"altitude": "0.0 m", "velocity": "CV MODE", "heading": "CV MODE", "gps": "Active"},
    "logs": ["[Drone Edge Node] AlertFilter Active. Tracker initialized."],
    "threat_active": False,
    "performance": {"inference_ms": 0.0, "calc_fps": 0.0}
}

# --- GLOBAL VAR FOR IMAGE CAPTURE ---
latest_frame = None

# --- THE ALERT FILTER STATE ---
alert_history = {} # Stores {track_id: consecutive_frame_count}

def connect_to_airsim():
    try:
        client = airsim.VehicleClient()
        client.confirmConnection()
        print("ONBOARD SENSOR: AirSim Camera Connected!")
        return client
    except Exception:
        return None

def generate_frames():
    global latest_frame  # Declare global to update the snapshot
    
    client = connect_to_airsim()
    if client is None: return
            
    frame_counter = 0
            
    while True:
        frame_counter += 1

        try:
            responses = client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)])
            if not responses: continue
            response = responses[0]
            if response.width == 0 or response.height == 0: continue
            img1d = np.frombuffer(response.image_data_uint8, dtype=np.uint8)
            frame = img1d.reshape(response.height, response.width, 3)
        except Exception:
            break

        # --- CORE PERFORMANCE MEASUREMENT ---
        start_inf = time.perf_counter()
        
        # RESTORED: model.track with persist=True (The AlertFilter needs this)
        results = model.track(frame, persist=True, imgsz=224, verbose=False)
        
        end_inf = time.perf_counter()
        
        inf_ms = (end_inf - start_inf) * 1000
        calc_fps = 1000.0 / inf_ms if inf_ms > 0 else 0
        
        system_state["performance"]["inference_ms"] = round(inf_ms, 2)
        system_state["performance"]["calc_fps"] = round(calc_fps, 1)

        threat_detected_this_frame = False
        
        # --- THE ALERT FILTER LOGIC ---
        if results[0].boxes is not None and results[0].boxes.id is not None:
            for box, track_id in zip(results[0].boxes, results[0].boxes.id):
                tid = int(track_id)
                label = model.names[int(box.cls)]
                conf = float(box.conf)

                # Log all raw detections to DB
                event_id = db_manager.log_detection(frame_counter, label, conf, tid, inf_ms, calc_fps)

                # Persistence Logic: Object must be seen for 5 frames to trigger Alert
                if conf >= 0.60 and label.lower() in ['axe', 'chainsaw']:
                    alert_history[tid] = alert_history.get(tid, 0) + 1
                    
                    if alert_history[tid] == 5:
                        db_manager.log_alert(event_id)
                        system_state["logs"].append(f"[{time.strftime('%H:%M:%S')}] *** THREAT CONFIRMED: {label.upper()} (ID: {tid}) ***")
                    
                    if alert_history[tid] >= 5:
                        threat_detected_this_frame = True
        
        system_state["threat_active"] = threat_detected_this_frame
        
        # Plotting
        annotated_frame = results[0].plot()
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        
        # Update the global latest frame for the capture endpoint
        if ret:
            latest_frame = buffer.tobytes()
            
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_transmit')
def video_transmit():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/telemetry_transmit')
def telemetry_transmit():
    return jsonify({
        "telemetry": system_state["telemetry"],
        "performance": system_state["performance"],
        "threat_active": system_state["threat_active"],
        "logs": system_state["logs"][-10:]
    })

# --- RESTORED SNAPSHOT ENDPOINT ---
@app.route('/capture_image')
def capture_image():
    global latest_frame
    if latest_frame is not None:
        return Response(latest_frame, mimetype='image/jpeg')
    else:
        return jsonify({"error": "No frame available yet"}), 404

@app.route('/export_csv')
def export_csv():
    try:
        conn = sqlite3.connect("mission_data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp, frame_index, object_class, confidence, tracking_id, inference_ms FROM DETECTION_EVENT")
        si = io.StringIO()
        writer = csv.writer(si)
        writer.writerow([i[0] for i in cursor.description]) 
        writer.writerows(cursor.fetchall()) 
        output = si.getvalue()
        conn.close()
        return Response(output, mimetype="text/csv", headers={"Content-disposition": "attachment; filename=results.csv"})
    except Exception as e:
        return jsonify({"error": str(e)}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)