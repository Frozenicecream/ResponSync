import sqlite3
from flask import Flask, request, jsonify, g, render_template
import os # Import the os module
from flask_cors import CORS
from . import KPI # Import the KPI module using a relative import
import threading # Import threading for the shutdown event

# Determine the absolute path to the database file
# __file__ is the path to api.py (e.g., c:/Code/ResponSync/src/backend/api.py)
# os.path.dirname(__file__) is the directory of api.py (src/backend/)
# os.path.join(os.path.dirname(__file__), '..', 'database', 'database.db')
# constructs the path src/backend/../database/database.db
# os.path.abspath() resolves this to the absolute path c:/Code/ResponSync/src/database/database.db
DATABASE_ABS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'database.db'))

DATABASE = DATABASE_ABS_PATH # Use the absolute path

app = Flask(__name__)
CORS(app) # This will enable CORS for all routes
app.config['JSON_SORT_KEYS'] = False # Keep JSON order as is

def get_db():
    """Opens a new database connection if there is none yet for the current application context."""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row # Return rows as dictionary-like objects
    return g.db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'db'):
        g.db.close()

def query_db(query, args=(), one=False):
    """Helper function to query the database."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    """Helper function to execute commands (INSERT, UPDATE, DELETE)."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(query, args)
    conn.commit()
    last_id = cur.lastrowid
    cur.close()
    return last_id

# --- Incident Endpoints (CRD) ---

@app.route('/incidents', methods=['POST'])
def create_incident():
    """Creates a new incident."""
    data = request.get_json()
    if not data or not all(k in data for k in ('location_latitude', 'location_longitude', 'severity', 'type')):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        incident_id = execute_db(
            'INSERT INTO all_incidents (location_latitude, location_longitude, severity, type) VALUES (?, ?, ?, ?)',
            [data['location_latitude'], data['location_longitude'], data['severity'], data['type']]
        )
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500

    try:
        incident_id = execute_db(
            'INSERT INTO current_incidents (location_latitude, location_longitude, severity, type) VALUES (?, ?, ?, ?)',
            [data['location_latitude'], data['location_longitude'], data['severity'], data['type']]
        )
        new_incident = query_db('SELECT * FROM current_incidents WHERE incident_id = ?', [incident_id], one=True)
        return jsonify(dict(new_incident)), 201
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500

@app.route('/incidents', methods=['GET'])
def get_incidents():
    """Retrieves all incidents."""
    try:
        incidents = query_db('SELECT * FROM current_incidents')
        return jsonify([dict(ix) for ix in incidents]), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500

@app.route('/incidents/<int:incident_id>', methods=['GET'])
def get_incident(incident_id):
    """Retrieves a specific incident by ID."""
    try:
        incident = query_db('SELECT * FROM current_incidents WHERE incident_id = ?', [incident_id], one=True)
        if incident is None:
            return jsonify({"error": "Incident not found"}), 404
        return jsonify(dict(incident)), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500

@app.route('/incidents/<int:incident_id>', methods=['DELETE'])
def delete_incident(incident_id):
    """Deletes an incident by ID."""
    try:
        # Optional: Check if incident exists before deleting
        incident = query_db('SELECT 1 FROM current_incidents WHERE incident_id = ?', [incident_id], one=True)
        if incident is None:
            return jsonify({"error": "Incident not found"}), 404

        execute_db('DELETE FROM current_incidents WHERE incident_id = ?', [incident_id])
        # Consider deleting related allocations as well, or handle foreign key constraints
        # execute_db('DELETE FROM current_allocations WHERE incident_id = ?', [incident_id])
        return jsonify({"message": "Incident deleted successfully"}), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500


# --- Resource Endpoints (CRUD) ---

@app.route('/resources', methods=['POST'])
def create_resource():
    """Creates a new resource."""
    data = request.get_json()
    if not data or not all(k in data for k in ('type', 'current_latitude', 'current_longitude', 'status')):
        return jsonify({"error": "Missing required fields"}), 400
    if data.get('status') not in ('available', 'en_route', 'occupied'):
         return jsonify({"error": "Invalid status value"}), 400

    try:
        resource_id = execute_db(
            'INSERT INTO all_resources (type, current_latitude, current_longitude, status) VALUES (?, ?, ?, ?)',
            [data['type'], data['current_latitude'], data['current_longitude'], data['status']]
        )
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500

    try:
        resource_id = execute_db(
            'INSERT INTO current_resources (type, current_latitude, current_longitude, status) VALUES (?, ?, ?, ?)',
            [data['type'], data['current_latitude'], data['current_longitude'], data['status']]
        )
        new_resource = query_db('SELECT * FROM current_resources WHERE resource_id = ?', [resource_id], one=True)
        return jsonify(dict(new_resource)), 201
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500
      
@app.route('/resources', methods=['GET'])
def get_resources():
    """Retrieves all resources."""
    try:
        resources = query_db('SELECT * FROM current_resources')
        return jsonify([dict(res) for res in resources]), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500

@app.route('/resources/<int:resource_id>', methods=['GET'])
def get_resource(resource_id):
    """Retrieves a specific resource by ID."""
    try:
        resource = query_db('SELECT * FROM current_resources WHERE resource_id = ?', [resource_id], one=True)
        if resource is None:
            return jsonify({"error": "Resource not found"}), 404
        return jsonify(dict(resource)), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500

@app.route('/resources/<int:resource_id>', methods=['PUT'])
def update_resource(resource_id):
    """Updates an existing resource."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided for update"}), 400

    # Build the update query dynamically based on provided fields
    fields = []
    values = []
    allowed_fields = ['type', 'current_latitude', 'current_longitude', 'status']

    for field in allowed_fields:
        if field in data:
            if field == 'status' and data[field] not in ('available', 'en_route', 'occupied'):
                 return jsonify({"error": "Invalid status value"}), 400
            fields.append(f"{field} = ?")
            values.append(data[field])

    if not fields:
        return jsonify({"error": "No valid fields provided for update"}), 400

    values.append(resource_id) # Add resource_id for the WHERE clause
    query = f"UPDATE current_resources SET {', '.join(fields)} WHERE resource_id = ?"

    try:
        # Check if resource exists
        resource = query_db('SELECT 1 FROM current_resources WHERE resource_id = ?', [resource_id], one=True)
        if resource is None:
            return jsonify({"error": "Resource not found"}), 404

        execute_db(query, values)
        updated_resource = query_db('SELECT * FROM current_resources WHERE resource_id = ?', [resource_id], one=True)
        return jsonify(dict(updated_resource)), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500


@app.route('/resources/<int:resource_id>', methods=['DELETE'])
def delete_resource(resource_id):
    """Deletes a resource by ID."""
    try:
        # Optional: Check if resource exists before deleting
        resource = query_db('SELECT 1 FROM current_resources WHERE resource_id = ?', [resource_id], one=True)
        if resource is None:
            return jsonify({"error": "Resource not found"}), 404

        # Delete related allocations first due to foreign key constraints
        execute_db('DELETE FROM current_allocations WHERE resource_id = ?', [resource_id])
        # Then delete the resource
        execute_db('DELETE FROM current_resources WHERE resource_id = ?', [resource_id])
        return jsonify({"message": "Resource and related allocations deleted successfully"}), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500


# --- Allocation Endpoints (CRD) ---

@app.route('/allocations', methods=['POST'])
def create_allocation():
    """Creates a new allocation record."""
    data = request.get_json()
    if not data or not all(k in data for k in ('incident_id', 'resource_id')):
        return jsonify({"error": "Missing required fields (incident_id, resource_id)"}), 400

    # Optional: Add predicted_response_time if provided
    predicted_time = data.get('predicted_response_time') # Can be None

    try:
        # Check if incident and resource exist
        incident = query_db('SELECT 1 FROM current_incidents WHERE incident_id = ?', [data['incident_id']], one=True)
        resource = query_db('SELECT 1 FROM current_resources WHERE resource_id = ?', [data['resource_id']], one=True)
        if not incident:
            return jsonify({"error": f"Incident with ID {data['incident_id']} not found"}), 404
        if not resource:
            return jsonify({"error": f"Resource with ID {data['resource_id']} not found"}), 404

        # Check for UNIQUE constraint on incident_id (only one allocation per incident)
        existing_allocation = query_db('SELECT 1 FROM current_allocations WHERE incident_id = ?', [data['incident_id']], one=True)
        if existing_allocation:
             return jsonify({"error": f"Incident {data['incident_id']} already has an allocation"}), 409 # Conflict

        execute_db(
            'INSERT INTO all_allocations (incident_id, resource_id, predicted_response_time) VALUES (?, ?, ?)',
            [data['incident_id'], data['resource_id'], predicted_time]
        )

        allocation_id = execute_db(
            'INSERT INTO current_allocations (incident_id, resource_id, predicted_response_time) VALUES (?, ?, ?)',
            [data['incident_id'], data['resource_id'], predicted_time]
        )
        new_allocation = query_db('SELECT * FROM current_allocations WHERE allocation_id = ?', [allocation_id], one=True)

        # Optionally update resource status to 'en_route' upon allocation
        execute_db('UPDATE current_resources SET status = ? WHERE resource_id = ?', ['en_route', data['resource_id']])

        return jsonify(dict(new_allocation)), 201
    except sqlite3.IntegrityError as e:
         # Catch potential foreign key or unique constraint errors not caught above
         return jsonify({"error": f"Database integrity error: {e}"}), 400
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500

@app.route('/allocations', methods=['GET'])
def get_allocations():
    """Retrieves all allocation records."""
    try:
        # Join with incidents and resources for more context (optional)
        allocations = query_db('''
            SELECT a.*, i.type as incident_type, r.type as resource_type
            FROM current_allocations a
            JOIN current_incidents i ON a.incident_id = i.incident_id
            JOIN current_resources r ON a.resource_id = r.resource_id
        ''')
        # If you only want allocation table data:
        # allocations = query_db('SELECT * FROM current_allocations')
        return jsonify([dict(alloc) for alloc in allocations]), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500

@app.route('/allocations/<int:allocation_id>', methods=['GET'])
def get_allocation(allocation_id):
    """Retrieves a specific allocation by ID."""
    try:
        allocation = query_db('SELECT * FROM current_allocations WHERE allocation_id = ?', [allocation_id], one=True)
        if allocation is None:
            return jsonify({"error": "Allocation not found"}), 404
        return jsonify(dict(allocation)), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500

@app.route('/allocations/<int:allocation_id>', methods=['DELETE'])
def delete_allocation(allocation_id):
    """Deletes an allocation by ID."""
    try:
        # Optional: Check if allocation exists before deleting
        allocation = query_db('SELECT resource_id FROM current_allocations WHERE allocation_id = ?', [allocation_id], one=True)
        if allocation is None:
            return jsonify({"error": "Allocation not found"}), 404

        execute_db('DELETE FROM current_allocations WHERE allocation_id = ?', [allocation_id])

        # Optionally update the previously allocated resource status back to 'available'
        # Be careful: Only do this if the resource isn't immediately re-allocated or occupied
        # resource_id = allocation['resource_id']
        # execute_db('UPDATE current_resources SET status = ? WHERE resource_id = ? AND status = ?', ['available', resource_id, 'en_route'])

        return jsonify({"message": "Allocation deleted successfully"}), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500

# Renders the map onto the home page
# For now the home page is map.html, it can be changed later.

@app.route('/')
def show_map():
    return render_template('map.html')

# --- API Endpoints for the Map Visualization ---

@app.route('/api/incidents', methods=['GET'])
def get_incidents_for_map():
    """Fetches incidents for the map API."""
    try:
        incidents = query_db('SELECT * FROM current_incidents') # Changed 'incidents' to 'current_incidents'
        return jsonify([
            {
                'incident_id': incident['incident_id'], # Added incident_id
                'location_latitude': incident['location_latitude'],
                'location_longitude': incident['location_longitude'],
                'severity': incident['severity'],
                'type': incident['type']
            }
            for incident in incidents
        ]), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500

@app.route('/api/resources', methods=['GET'])
def get_resources_for_map():
    """Fetches a limited number of resources with offset for rotation."""
    try:
        resources = query_db('SELECT * FROM current_resources WHERE status = "available"') # Changed 'resources' to 'current_resources'
        return jsonify([
            {
                'resource_id': r['resource_id'], # Added resource_id
                'current_latitude': r['current_latitude'],
                'current_longitude': r['current_longitude'],
                'type': r['type'],
                'status': r['status']
            }
            for r in resources
        ]), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500

@app.route('/api/routepair', methods=['GET'])
def get_route_pair():
    """Fetches all current allocated incident and resource coordinates for routing on the map."""
    try:
        query = """
            SELECT
                ca.allocation_id as allocation_id, 
                i.incident_id as incident_id,
                i.location_latitude as incident_lat,
                i.location_longitude as incident_lng,
                r.resource_id as resource_id,
                r.current_latitude as resource_lat,
                r.current_longitude as resource_lng,
                r.type as resource_type,         
                r.status as resource_status      
            FROM current_allocations ca
            JOIN current_incidents i ON ca.incident_id = i.incident_id
            JOIN current_resources r ON ca.resource_id = r.resource_id;
        """
        route_data_list = query_db(query) 

        if route_data_list:
            allocations = []
            for route_data in route_data_list:
                allocations.append({
                    "allocation_id": route_data["allocation_id"], 
                    "incident": {
                        "lat": route_data["incident_lat"],
                        "lng": route_data["incident_lng"],
                        "incident_id": route_data["incident_id"]
                    },
                    "resource": {
                        "lat": route_data["resource_lat"],
                        "lng": route_data["resource_lng"],
                        "resource_id": route_data["resource_id"],
                        "type": route_data["resource_type"],      
                        "status": route_data["resource_status"]    
                    }
                })
            return jsonify(allocations), 200
        else:
            # Return an empty list if no allocations are found.
            return jsonify([]), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/api/allocation/complete/<int:allocation_id>', methods=['POST'])
def complete_allocation(allocation_id):
    """Marks an allocation as complete and deletes associated incident and resource."""
    try:
        # First, get the incident_id and resource_id from the allocation
        allocation_details = query_db('SELECT incident_id, resource_id FROM current_allocations WHERE allocation_id = ?', [allocation_id], one=True)
        if not allocation_details:
            return jsonify({"error": f"Allocation {allocation_id} not found"}), 404

        incident_id = allocation_details['incident_id']
        resource_id = allocation_details['resource_id']

        # Delete the allocation
        execute_db('DELETE FROM current_allocations WHERE allocation_id = ?', [allocation_id])
        
        # Delete the incident
        execute_db('DELETE FROM current_incidents WHERE incident_id = ?', [incident_id,])
        
        # Delete the resource
        execute_db('DELETE FROM current_resources WHERE resource_id = ?', [resource_id,])

        return jsonify({"message": f"Allocation {allocation_id} completed and associated data deleted."}), 200

    except sqlite3.Error as e:
        conn.rollback() # Rollback in case of error
        return jsonify({"error": f"Database error during completion: {e}"}), 500
    except Exception as e:
        conn.rollback() # Rollback in case of error
        return jsonify({"error": f"An unexpected error occurred during completion: {str(e)}"}), 500

# --- Main Application Runner ---
if __name__ == '__main__':
    app.run(debug=True) # debug=True is helpful for development

# Global event for graceful shutdown
shutdown_event = threading.Event()

@app.route('/api/kpi_data', methods=['GET'])
def get_kpi_data():
    """Retrieves KPI data."""
    kpi_data = KPI.get_kpi_data()
    return jsonify(kpi_data), 200

import os
@app.route('/api/shutdown', methods=['POST'])
def shutdown():
    shutdown_event.set()  # Signal background threads to stop
    os._exit(0)  # Forcefully exit the process
    return jsonify({"message": "Server shutting down..."}), 200