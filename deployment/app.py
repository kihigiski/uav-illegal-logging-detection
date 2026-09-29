import subprocess
import sys
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# System State Variables
drone_process = None
mission_initiator = None  # Tracks who started the mission (Control vs Operator)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/operator')
def operator():
    return render_template('operator.html')

@app.route('/start_mission', methods=['POST'])
def start_mission():
    global drone_process, mission_initiator
    
    # Read the role (control/operator) from the request
    data = request.get_json() or {}
    role = data.get('role', 'unknown')

    # Check if a mission is already running
    if drone_process is None or drone_process.poll() is not None:
        print(f"🚀 Initializing Drone Edge Node... [Initiated by: {role.upper()}]")
        mission_initiator = role  # Lock the mission to the initiator
        
        # Start the core drone brain
        try:
            drone_process = subprocess.Popen([sys.executable, "drone_brain.py"])
            return jsonify({
                "status": "success", 
                "message": f"Drone Node successfully started by {role}"
            })
        except Exception as e:
            return jsonify({"status": "error", "message": f"Failed to launch brain: {e}"}), 500
    
    return jsonify({"status": "ignored", "message": "Mission is already active"})

@app.route('/stop_mission', methods=['POST'])
def stop_mission():
    global drone_process, mission_initiator
    
    data = request.get_json() or {}
    role = data.get('role', 'unknown')

    if drone_process is not None:
        # SECURITY CHECK: Operators cannot stop missions started by Ground Control
        if role == 'operator' and mission_initiator == 'control':
            print(f"SECURITY ALERT: Unauthorized override attempt by OPERATOR.")
            return jsonify({
                "status": "denied", 
                "message": "Override Denied: Mission locked by Control Station."
            }), 403
            
        print(f"Terminating Drone Systems... [Stopped by: {role.upper()}]")
        
        # Gracefully terminate the core brain
        drone_process.terminate()
        drone_process.wait()
        drone_process = None
        
        # Reset security lock
        mission_initiator = None  
        return jsonify({"status": "success", "message": "Drone Node Terminated Successfully"})
        
    return jsonify({"status": "ignored", "message": "No active mission to stop"})

if __name__ == '__main__':
    print("GROUND CONTROL STATION ONLINE: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)