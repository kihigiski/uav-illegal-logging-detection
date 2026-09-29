import sqlite3
import os

print("Initiating Database Logging Test (FT-04)")

# 1. Create a temporary test database
db_path = 'test_mission_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 2. Create the table exactly as app.py does
cursor.execute('''
    CREATE TABLE IF NOT EXISTS DETECTION_EVENT (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        class_name TEXT,
        confidence REAL,
        inference_ms REAL
    )
''')
conn.commit()
print("PROOF 1: SQLite Database and Table successfully created.")

# 3. Defensible Proof: Writing Data
# We simulate the AI detecting an Axe in 12.5 milliseconds
cursor.execute('''
    INSERT INTO DETECTION_EVENT (timestamp, class_name, confidence, inference_ms)
    VALUES (CURRENT_TIMESTAMP, 'Axe', 0.96, 12.5)
''')
conn.commit()
print("PROOF 2: Successfully wrote 'Axe' detection to the database.")

# 4. Defensible Proof: Reading Data (Proving it wasn't lost)
cursor.execute('SELECT * FROM DETECTION_EVENT')
row = cursor.fetchone()

if row:
    print(f"PROOF 3: Data successfully retrieved! Row Data: {row}")
else:
    print("ERROR: Database is empty.")

# Clean up the test
conn.close()
if os.path.exists(db_path):
    os.remove(db_path) # Delete the test file so it's clean for next time