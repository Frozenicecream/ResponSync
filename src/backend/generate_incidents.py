import sqlite3
import random
import time
import requests
import os
import threading

# Get the absolute path to the database
DATABASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'database.db'))

def get_random_data_from_db():
    """Get random incident and resource data from the database."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    
    try:
        # Get random incident data
        incidents = conn.execute('SELECT location_latitude, location_longitude, severity, type FROM incidents').fetchall()
        
        # Get random resource data
        resources = conn.execute('SELECT type, current_latitude, current_longitude FROM resources').fetchall()
        
        return incidents, resources
    finally:
        conn.close()

def generate_resources():
    """Generate random resources in a separate thread."""
    while True:
        incidents, resources = get_random_data_from_db()
        num_resources = random.randint(1, 3)
        
        for _ in range(num_resources):
            resource = random.choice(resources)
            resource_data = {
                'type': resource['type'],
                'current_latitude': resource['current_latitude'],
                'current_longitude': resource['current_longitude'],
                'status': 'available'
            }
            
            try:
                response = requests.post('http://localhost:5000/resources', json=resource_data)
                if response.status_code == 201:
                    print(f"Created resource: {response.json()}")
                else:
                    print(f"Failed to create resource: {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"Error creating resource: {e}")
        
        time.sleep(15)

def generate_incidents():
    """Generate random incidents in a separate thread."""
    while True:
        incidents, resources = get_random_data_from_db()
        num_incidents = random.randint(1, 3)
        
        for _ in range(num_incidents):
            incident = random.choice(incidents)
            incident_data = {
                'location_latitude': incident['location_latitude'],
                'location_longitude': incident['location_longitude'],
                'severity': incident['severity'],
                'type': incident['type']
            }
            
            try:
                response = requests.post('http://localhost:5000/incidents', json=incident_data)
                if response.status_code == 201:
                    print(f"Created incident: {response.json()}")
                else:
                    print(f"Failed to create incident: {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"Error creating incident: {e}")
        
        time.sleep(15)

def main():
    print("Starting incident and resource generator...")
    print("Press Ctrl+C to stop")
    
    # Create threads for generating resources and incidents
    resource_thread = threading.Thread(target=generate_resources, daemon=True)
    incident_thread = threading.Thread(target=generate_incidents, daemon=True)
    
    try:
        # Start both threads
        resource_thread.start()
        incident_thread.start()
        
        # Keep the main thread running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping generator...")

if __name__ == "__main__":
    main()