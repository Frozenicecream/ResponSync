import pandas as pd
import numpy as np
from geopy.distance import geodesic
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor
from sklearn.linear_model import LinearRegression
# sklearn.model_selection.train_test_split is not directly used in load_and_train_model
import os
import requests
import time
import joblib  # Added for saving/loading model
import json    # Added for saving metadata

# --- Configuration ---

API_BASE_URL = "http://localhost:5000"
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))

# --- Model Persistence Configuration ---
MODEL_FILENAME = "trained_voting_model.joblib"
MODEL_METADATA_FILENAME = "model_metadata.json"
MODEL_SAVE_PATH = os.path.join(DATA_DIR, MODEL_FILENAME)
METADATA_SAVE_PATH = os.path.join(DATA_DIR, MODEL_METADATA_FILENAME)


# Global variables to store the trained model, columns, and last data timestamp
trained_model = None
model_columns = None
_last_loaded_csv_mtime = None # Stores the mtime of the CSV used for the current in-memory 'trained_model'

def load_and_train_model():
    """
    Loads a pre-trained model if available and the underlying data hasn't changed.
    Otherwise, trains a new model, saves it, and returns it.
    """
    global trained_model, model_columns, _last_loaded_csv_mtime

    allocations_csv_path = os.path.join(DATA_DIR, 'final_allocations.csv')

    if not os.path.exists(allocations_csv_path):
        print(f"Error: Training data CSV file not found at {allocations_csv_path}")
        return None, None

    current_csv_mtime = None
    try:
        current_csv_mtime = os.path.getmtime(allocations_csv_path)
    except OSError as e:
        print(f"Warning: Could not get modification time for {allocations_csv_path}: {e}.")
        print("Will attempt to train a new model or load if an existing model file is found (without mtime check).")

    # 1. Check in-memory cache (if this function were called multiple times in one process run)
    if trained_model is not None and model_columns is not None and \
       _last_loaded_csv_mtime == current_csv_mtime and current_csv_mtime is not None:
        print("Using in-memory cached model (data unchanged).")
        return trained_model, model_columns

    # 2. Try to load from disk
    if os.path.exists(MODEL_SAVE_PATH) and os.path.exists(METADATA_SAVE_PATH):
        try:
            with open(METADATA_SAVE_PATH, 'r') as f:
                metadata = json.load(f)
            saved_csv_mtime = metadata.get('csv_mtime')
            saved_model_columns = metadata.get('model_columns')

            # Only load if CSV mtime matches (and mtime is available) or if current_csv_mtime is None (cannot verify)
            # and saved_model_columns exist.
            if saved_model_columns and (current_csv_mtime is None or saved_csv_mtime == current_csv_mtime):
                if current_csv_mtime is not None:
                    print(f"Loading pre-trained model from {MODEL_SAVE_PATH} (CSV data appears unchanged).")
                else:
                    print(f"Loading pre-trained model from {MODEL_SAVE_PATH} (CSV mtime check skipped due to error).")
                
                loaded_model = joblib.load(MODEL_SAVE_PATH)
                print("Model loaded successfully from disk.")
                
                # Update globals
                trained_model = loaded_model
                model_columns = saved_model_columns
                _last_loaded_csv_mtime = saved_csv_mtime # Use saved_csv_mtime from metadata
                return trained_model, model_columns
            elif current_csv_mtime is not None and saved_csv_mtime != current_csv_mtime:
                print(f"Training data CSV ({allocations_csv_path}) has changed. Retraining model.")
            elif not saved_model_columns:
                print("Metadata is incomplete (missing model columns). Retraining model.")
            # If we reach here, retraining is needed.
        except Exception as e:
            print(f"Error loading model/metadata from disk: {e}. Retraining model.")
    else:
        if not os.path.exists(MODEL_SAVE_PATH):
            print(f"No saved model found at {MODEL_SAVE_PATH}.")
        if not os.path.exists(METADATA_SAVE_PATH):
            print(f"No model metadata found at {METADATA_SAVE_PATH}.")
        print("Proceeding to train a new model.")

    # 3. Train a new model
    try:
        print(f"Loading training data from {allocations_csv_path} for new training...")
        training_df = pd.read_csv(allocations_csv_path)
        print(f"Loaded {len(training_df)} training samples from CSV.")

        training_df = training_df.dropna(subset=['actual_response_time'])
        print(f"After cleaning NaNs in target 'actual_response_time': {len(training_df)} samples.")

        if training_df.empty:
            print("No training data available after cleaning. Cannot train model.")
            return None, None

        print("Training Voting Regressor model...")
        feature_cols = ['incident_type', 'resource_type', 'severity', 'distance', 'traffic_factor', 'resource_status']
        X_train = training_df[feature_cols].copy() # Renamed to X_train to avoid confusion
        X_train = pd.get_dummies(X_train, columns=['incident_type', 'resource_type'], dummy_na=False)
        y_train = training_df['actual_response_time'] # Renamed to y_train

        rf = RandomForestRegressor(random_state=42)
        gb = GradientBoostingRegressor(random_state=42)
        lr = LinearRegression()
        newly_trained_model = VotingRegressor(estimators=[('rf', rf), ('gb', gb), ('lr', lr)])
        newly_trained_model.fit(X_train, y_train)
        print("Model training completed.")

        # Save the newly trained model and metadata
        joblib.dump(newly_trained_model, MODEL_SAVE_PATH)
        print(f"Model saved to {MODEL_SAVE_PATH}")
        
        current_model_columns = X_train.columns.tolist()
        metadata_to_save = {
            'csv_mtime': current_csv_mtime, # This might be None if os.path.getmtime failed
            'model_columns': current_model_columns
        }
        with open(METADATA_SAVE_PATH, 'w') as f:
            json.dump(metadata_to_save, f)
        print(f"Metadata saved to {METADATA_SAVE_PATH}")

        # Update globals
        trained_model = newly_trained_model
        model_columns = current_model_columns
        _last_loaded_csv_mtime = current_csv_mtime
        return trained_model, model_columns

    except FileNotFoundError:
        print(f"Error: Training data CSV file not found at {allocations_csv_path} during training attempt.")
        return None, None
    except Exception as e:
        print(f"An error occurred during model training or saving: {e}")
        # Potentially clean up partially saved files if necessary, though omitted for brevity
        return None, None

def process_allocations():
    """Process current incidents and make allocations."""
    # Get the trained model (loads from disk or trains if necessary)
    model_data = load_and_train_model()
    
    # Ensure model_data and the model itself are not None
    if not model_data or model_data[0] is None:
        print("Failed to load or train the model. Exiting allocation process.")
        return
    
    current_model, current_training_columns = model_data

    # Ensure current_training_columns is not None before using it
    if current_training_columns is None:
        print("Model columns are not available. Exiting allocation process.")
        return

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

        # Get existing allocations to check for resource and incident availability
        allocations_response = requests.get(f"{API_BASE_URL}/allocations")
        allocations_response.raise_for_status()
        allocations_data = allocations_response.json()
        
        allocated_resources = set()
        allocated_incidents = set()
        if allocations_data:
            for a in allocations_data:
                allocated_resources.add(a['resource_id'])
                allocated_incidents.add(a['incident_id'])
        
        print(f"Currently allocated resources: {allocated_resources}")
        print(f"Currently allocated incidents: {allocated_incidents}")

        # Filter out incidents that are already allocated
        original_incident_count = len(incidents_df)
        incidents_df = incidents_df[~incidents_df['incident_id'].isin(allocated_incidents)]
        print(f"Filtered out {original_incident_count - len(incidents_df)} already allocated incidents. Processing {len(incidents_df)} incidents.")

        if incidents_df.empty:
            print("No unallocated incidents to process.")
            return

        predictions_csv_path = os.path.join(DATA_DIR, 'final_incident_predictions.csv')
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
    for _, incident in incidents_df.iterrows(): # incidents_df is now filtered
        for _, resource in resources_df.iterrows():
            try:
                # Skip if resource is already allocated
                if resource['resource_id'] in allocated_resources:
                    continue

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
        'fire': ['Fire Truck'],
        'accident': ['Ambulance'],
        'medical': ['Ambulance'],
        'crime': ['Police Car']
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

    # Align columns with the ones used during training
    for col in current_training_columns:
        if col not in X_current.columns:
            X_current[col] = 0
    X_current = X_current[current_training_columns] # Ensure order and presence of all training columns

    current_df['predicted_response_time'] = current_model.predict(X_current)

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
            # Double-check if incident got allocated by another process/thread in the meantime (optional, defensive)
            # This is less likely if this script is the sole allocator, but good for robustness
            # if payload['incident_id'] in allocated_incidents:
            #     print(f"Incident {payload['incident_id']} was allocated concurrently. Skipping.")
            #     continue

            post_response = requests.post(f"{API_BASE_URL}/allocations", json=payload)
            if 200 <= post_response.status_code < 300:
                print(f"Successfully allocated incident {payload['incident_id']} to resource {payload['resource_id']}")
                allocated_resources.add(payload['resource_id'])  # Mark resource as allocated for this run
                allocated_incidents.add(payload['incident_id'])  # Mark incident as allocated for this run
            elif post_response.status_code == 409: # Should be less frequent now with proactive check
                print(f"Conflict: Incident {payload['incident_id']} already has an allocation (or resource busy).")
            else:
                print(f"Error creating allocation for incident {payload['incident_id']} (HTTP {post_response.status_code}): {post_response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Request failed for allocation of incident {payload['incident_id']}: {e}")

    print("Resource allocation process finished.")

if __name__ == "__main__":
    while True:
        process_allocations()
        time.sleep(15)
