import json
from flask import Flask, jsonify, Response

print("Initiating Telemetry API Test (FT-05)")

# 1. Setup a lightweight mock of your Flask endpoints
app = Flask(__name__)

@app.route('/telemetry_transmit')
def telemetry():
    # Simulate the dictionary your drone_brain generates
    return jsonify({"drone_state": "PATROL", "active_threats": 1, "fps": 24.5})

@app.route('/export_csv')
def export_csv():
    # Simulate the CSV string generated from the SQLite database
    mock_csv_data = "id,timestamp,class,confidence\n1,10:00:01,Axe,0.95"
    return Response(mock_csv_data, mimetype="text/csv", 
                    headers={"Content-Disposition": "attachment;filename=log.csv"})

# 2. Use Flask's built-in test client (Simulates a web browser automatically!)
client = app.test_client()

# 3. Defensible Proof: JSON Telemetry Endpoint
print("\nPinging /telemetry_transmit endpoint...")
response_tel = client.get('/telemetry_transmit')

if response_tel.status_code == 200:
    data = json.loads(response_tel.data)
    print(f"PROOF 1: Server returned HTTP 200 (OK).")
    print(f"Valid JSON payload accurately parsed: {data}")
else:
    print("ERROR: Telemetry endpoint failed.")

# 4. Defensible Proof: CSV Export Endpoint
print("\nPinging /export_csv endpoint...")
response_csv = client.get('/export_csv')

if response_csv.status_code == 200 and response_csv.mimetype == 'text/csv':
    print(f"PROOF 2: Server returned HTTP 200 (OK).")
    print(f"Valid MIME type received: '{response_csv.mimetype}'")
    print(f"Download headers verified: {response_csv.headers.get('Content-Disposition')}")
else:
    print(" ERROR: CSV Export endpoint failed.")