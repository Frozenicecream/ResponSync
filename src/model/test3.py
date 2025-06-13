import pandas as pd
import numpy as np
from geopy.distance import geodesic
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import os
import requests
import time

# --- Configuration ---
API_BASE_URL = "http://localhost:5000"
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))

def load_and_train_model():
    """Load training data and train the model."""
    try:
        allocations_csv_path = os.path.join(DATA_DIR, 'final_allocations.csv')
        if not os.path.exists(allocations_csv_path):
            print(f"Error: Training data CSV file not found at {allocations_csv_path}")
            return None
        training_df = pd.read_csv(allocations_csv_path)
        print(f"Loaded {len(training_df)} training samples from CSV.")

        # Remove rows where 'actual_response_time' is NaN
        training_df = training_df.dropna(subset=['actual_response_time'])
        
        # Optionally, remove rows with NaN values in any critical column
        # training_df = training_df.dropna(subset=['incident_type', 'resource_type', 'severity', 'distance', 'traffic_factor', 'resource_status'])
        
        print(f"After cleaning: {len(training_df)} training samples remaining.")

        print("Training ML model...")
        feature_cols = ['incident_type', 'resource_type', 'severity', 'distance', 'traffic_factor', 'resource_status']
        X = training_df[feature_cols].copy()
        X = pd.get_dummies(X, columns=['incident_type', 'resource_type'], dummy_na=False)
        y = training_df['actual_response_time']

        model = RandomForestRegressor(random_state=42)
        model.fit(X, y)
        print("Model training completed.")
        return model, X.columns
    except Exception as e:
        print(f"Error in model training: {e}")
        return None

def process_allocations():
    """Process current incidents and make allocations."""
    model_data = load_and_train_model()
    if not model_data:
        print("Failed to train model. Exiting.")
        return
    model, training_columns = model_data

    feature_cols = ['incident_type', 'resource_type', 'severity', 'distance', 'traffic_factor', 'resource_status']

    print("Fetching current data from API...")
    try:
        incidents_response = requests.get(f"{API_BASE_URL}/incidents")
        incidents_response.raise_for_status()
        incidents_data = incidents_response.json()
        if not incidents_data:
            print("No incidents data received from API.")
            return
        incidents_df = pd.DataFrame(incidents_data)
        print(f"Fetched {len(incidents_df)} incidents from API.")

        resources_response = requests.get(f"{API_BASE_URL}/resources")
        resources_response.raise_for_status()
        resources_data = resources_response.json()
        if not resources_data:
            print("No resources data received from API.")
            return
        resources_df = pd.DataFrame(resources_data)
        print(f"Fetched {len(resources_df)} resources from API.")

        predictions_csv_path = os.path.join(DATA_DIR, r'data/final_incident_predictions.csv')
        predictions_df = pd.read_csv(predictions_csv_path)
        predictions_df.columns = predictions_df.columns.str.strip().str.lower().str.replace(' ', '_')
        if 's.no.' in predictions_df.columns:
            predictions_df.drop(columns=['s.no.'], inplace=True)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return

    print("Preparing current data for predictions...")
    rows = []
    for _, incident in incidents_df.iterrows():
        for _, resource in resources_df.iterrows():
            try:
                incident_lat = float(incident['location_latitude'])
                incident_lon = float(incident['location_longitude'])
                resource_lat = float(resource['current_latitude'])
                resource_lon = float(resource['current_longitude'])

                distance = geodesic((incident_lat, incident_lon), (resource_lat, resource_lon)).km

                traffic_factor = predictions_df[
                    predictions_df['incident_id'] == incident['incident_id']
                ]['predicted_traffic_factor'].iloc[0] if not predictions_df.empty else 50

                rows.append({
                    'incident_id': incident['incident_id'],
                    'resource_id': resource['resource_id'],
                    'incident_type': incident['type'],
                    'resource_type': resource['type'],
                    'severity': incident['severity'],
                    'distance': distance,
                    'traffic_factor': traffic_factor,
                    'resource_status': 1 if str(resource.get('status', '')).lower() == 'available' else 0
                })
            except (ValueError, TypeError, KeyError, IndexError):
                continue

    if not rows:
        print("No valid incident-resource pairs generated.")
        return

    current_df = pd.DataFrame(rows)

    valid_pairings = {
        'fire': ['Fire Truck', 'Rescue Team'],
        'accident': ['Ambulance', 'Police Car', 'Medical Team'],
        'medical': ['Ambulance', 'Medical Team'],
        'rescue': ['Rescue Team', 'Fire Truck', 'Police Car']
    }

    current_df = current_df[current_df.apply(
        lambda row: row.get('resource_type', '') in valid_pairings.get(str(row.get('incident_type', '')).lower(), []),
        axis=1
    )]

    if current_df.empty:
        print("No valid pairings after filtering by type.")
        return

    print("Making predictions for current incidents...")
    X_current = current_df[feature_cols].copy()
    X_current = pd.get_dummies(X_current, columns=['incident_type', 'resource_type'], dummy_na=False)

    for col in training_columns:
        if col not in X_current.columns:
            X_current[col] = 0
    X_current = X_current[training_columns]

    current_df['predicted_response_time'] = model.predict(X_current)

    print("Determining best allocations...")
    best_allocs_indices = current_df.groupby('incident_id')['predicted_response_time'].idxmin()
    best_allocs = current_df.loc[best_allocs_indices].copy()

    print("Posting allocations to API...")
    for _, allocation in best_allocs.iterrows():
        payload = {
            "incident_id": int(allocation['incident_id']),
            "resource_id": int(allocation['resource_id']),
            "predicted_response_time": float(allocation['predicted_response_time'])
        }
        try:
            post_response = requests.post(f"{API_BASE_URL}/allocations", json=payload)
            if 200 <= post_response.status_code < 300:
                print(f"Successfully allocated incident {payload['incident_id']} to resource {payload['resource_id']}")
            elif post_response.status_code == 409:
                print(f"Conflict: Incident {payload['incident_id']} already has an allocation")
            else:
                print(f"Error creating allocation for incident {payload['incident_id']} (HTTP {post_response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"Request failed for allocation of incident {payload['incident_id']}: {e}")

    print("Resource allocation process finished.")

if __name__ == "__main__":
    while True:
        process_allocations()
        time.sleep(15)  # Wait for 15 seconds before next run
