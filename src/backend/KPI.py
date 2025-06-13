import os
import sqlite3
from datetime import datetime

# Get the directory of the main.py script (c:/Code/ResponSync-1/src)
# Assuming the database is in c:/Code/ResponSync-1/database/
# Adjust DB_PATH to go up two levels from src/backend/KPI.py and then into database
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SRC_DIR, '..')) # Go up from src/backend to ResponSync-1
DB_PATH = os.path.join(ROOT_DIR, 'database', 'database.db')

def connect_to_db():
    """Connects to the SQLite database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        print(f"Connected to {os.path.basename(DB_PATH)}")
    except sqlite3.Error as e:
        print(f"Could not establish a connection to {os.path.basename(DB_PATH)}: {e}")
        return None
    return conn

def calculate_kpi(conn):
    """Calculates and displays KPI details for each allocation."""
    cursor = conn.cursor()

    query = """
    SELECT
        ca.allocation_id,
        ca.assignment_time,
        ci.report_time,
        ci.type AS incident_type,
        ci.severity AS incident_severity,
        cr.type AS resource_type
    FROM
        all_allocations ca
    JOIN
        all_incidents ci ON ca.incident_id = ci.incident_id
    JOIN
        all_resources cr ON ca.resource_id = cr.resource_id
    ORDER BY
        ca.assignment_time;
    """

    try:
        cursor.execute(query)
        allocations = cursor.fetchall()

        if not allocations:
            print("No allocations found in the database.")
            return None

        print("\n--- Allocation Details ---\n")
        print(f"{'Allocation ID':<15} {'Resource Type':<15} {'Incident Type':<15} {'Severity':<10} {'Allocation Time (s)':<25}")
        print("-" * 80)
        allocation_details = []
        total_allocation_time = 0
        incident_counts = {'crime': 0, 'fire': 0, 'medical': 0, 'accident':0}
        resource_counts = {'Police Car':0,'Ambulance':0,'Fire Truck':0}

        for alloc in allocations:
            alloc_id, assignment_time_str, report_time_str, incident_type, incident_severity, resource_type = alloc

            # Convert string timestamps to datetime objects
            assignment_time = datetime.strptime(assignment_time_str, '%Y-%m-%d %H:%M:%S')
            report_time = datetime.strptime(report_time_str, '%Y-%m-%d %H:%M:%S')
            # Calculate incident and resource counts
            incident_counts[incident_type] += 1
            resource_counts[resource_type] += 1
            
            # Calculate allocation time in seconds
            allocation_time_delta = assignment_time - report_time
            allocation_time_seconds = allocation_time_delta.total_seconds()
            total_allocation_time+=allocation_time_seconds

            print(f"{alloc_id:<15} {resource_type:<15} {incident_type:<15} {incident_severity:<10} {allocation_time_seconds:<25.2f}")
            allocation_details.append({
                "allocation_id": alloc_id,
                "resource_type": resource_type,
                "incident_type": incident_type,
                "severity": incident_severity,
                "allocation_time_seconds": f"{allocation_time_seconds:.2f}"
            })

        average_allocation_time = total_allocation_time / len(allocations)
        simulation_length = calculate_simulation_length(conn)
        incident_distribution, resource_distribution = calculate_distributions(incident_counts, resource_counts)
        total_allocations = len(allocations)

        print(f"\nAverage Allocation Time: {average_allocation_time:.2f} seconds")
        print(f"\nSimulation Length: {simulation_length:.2f} seconds")
        print("\n--- End of Allocation Details ---\n")

        # Combine all kpi data into kpi_data and return
        kpi_data = {
            "incident_distribution": incident_distribution,
            "resource_distribution": resource_distribution,
            "average_allocation_time": f"{average_allocation_time:.2f}",
            "simulation_length": f"{simulation_length:.2f}",
            "total_allocations": total_allocations,
            "allocation_details": allocation_details
        }

        return kpi_data

    except sqlite3.Error as e:
        print(f"Error querying allocations: {e}")
        return None

def calculate_simulation_length(conn):
    """Calculates and displays the simulation length in seconds."""
    cursor = conn.cursor()

    query = """
    SELECT
        MIN(report_time) AS start_time,
        MAX(report_time) AS end_time
    FROM
        all_incidents;
    """
    try:
        cursor.execute(query)
        result = cursor.fetchone()
        start_time_str, end_time_str = result

        # Convert string timestamps to datetime objects
        start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')

        # Calculate simulation length in seconds
        simulation_length_delta = end_time - start_time
        simulation_length_seconds = simulation_length_delta.total_seconds()

    except sqlite3.Error as e:
        print(f"Error querying simulation length: {e}")
        return None

    # return simulation length in seconds
    return simulation_length_seconds

def calculate_distributions(incident_counts, resource_counts):
    """Calculates and displays incident and resource distributions."""
    
    # Calculate incident and resource totals
    total_incidents = sum(incident_counts.values())
    total_resources = sum(resource_counts.values())

    # Calculate incident and resource distributions as percentages
    incident_distribution = {incident_type: f"{(count / total_incidents) * 100:.2f}" for incident_type, count in incident_counts.items()}
    # Calculate incident and resource distributions as percentages
    incident_distribution_dict = {incident_type: f"{(count / total_incidents) * 100:.2f}" for incident_type, count in incident_counts.items()}
    resource_distribution_dict = {resource_type: f"{(count / total_resources) * 100:.2f}" for resource_type, count in resource_counts.items()}

    # Convert dictionaries to the array format expected by the frontend
    incident_distribution_list = [{"name": name, "value": value} for name, value in incident_distribution_dict.items()]
    resource_distribution_list = [{"name": name, "value": value} for name, value in resource_distribution_dict.items()]

    return incident_distribution_list, resource_distribution_list

def main():
    print("\nStarting KPI calculation...")
    # Establish a connection to the database
    conn = connect_to_db()
    if conn:
        # Calculate KPIs
        calculate_kpi(conn)
        conn.close()
        print("KPI calculation complete.")
    else:
        print("Database connection failed. Cannot calculate KPIs.")

def get_kpi_data():
    conn = connect_to_db()
    if conn:
        kpi_data = calculate_kpi(conn)
        conn.close()
        return kpi_data
    else:
        print("Database connection failed in get_kpi_data. Cannot calculate KPIs.")
        return {"kpi_data": []}

if __name__ == "__main__":
    main()