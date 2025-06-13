import pandas as pd
import numpy as np
import random

INCIDENT_TYPES = ["fire", "accident", "medical", "crime"]
RESOURCE_TYPES = ["Ambulance", "Fire Truck", "Police Car"]

def get_resource_type(incident_type):
    resource_mapping = {
        "fire": "Fire Truck",
        "accident": "Ambulance",
        "medical": "Ambulance",
        "crime": "Police Car"
    }
    return resource_mapping.get(incident_type, "Ambulance")  # Default to Ambulance if type not found

def main(input_csv, n, incident_id_start):
    df = pd.read_csv(input_csv)
    numeric_cols = [
        "severity", "distance", "traffic_factor", "base_response_time",
        "resource_status", "actual_response_time", "predicted_response_time"
    ]
    means = df[numeric_cols].mean()
    stds = df[numeric_cols].std()

    resource_ids = df["resource_id"].unique().tolist()

    rows = []
    for i in range(n):
        incident_id = incident_id_start + i
        resource_id = int(random.choice(resource_ids))
        incident_type = random.choice(INCIDENT_TYPES)
        resource_type = get_resource_type(incident_type)
        row = {
            "incident_id": incident_id,
            "resource_id": resource_id,
            "incident_type": incident_type,
            "resource_type": resource_type,
        }
        for col in numeric_cols:
            val = np.random.normal(means[col], stds[col])
            if col == "severity":
                val = int(np.clip(round(val), 1, 5))
            elif col == "resource_status":
                val = int(np.clip(round(val), 0, 1))
            row[col] = val
        rows.append(row)

    new_df = pd.DataFrame(rows)
    
    # Format the output to match CSV format
    columns = ["incident_id", "resource_id", "incident_type", "resource_type", 
              "severity", "distance", "traffic_factor", "base_response_time",
              "resource_status", "actual_response_time", "predicted_response_time"]
    
    # Print each row in CSV format without index
    for _, row in new_df[columns].iterrows():
        print(f"{row['incident_id']},{row['resource_id']},{row['incident_type']},{row['resource_type']},"
              f"{row['severity']},{row['distance']:.14f},{row['traffic_factor']:.14f},{row['base_response_time']:.2f},"
              f"{row['resource_status']},{row['actual_response_time']:.14f},{row['predicted_response_time']:.14f}")

if __name__ == "__main__":
    input_csv = "data/final_allocations.csv"
    n = int(input("Enter number of tuples to generate (n): "))
    incident_id_start = int(input("Enter starting incident_id: "))
    main(input_csv, n, incident_id_start)