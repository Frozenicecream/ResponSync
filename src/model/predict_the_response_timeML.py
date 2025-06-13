import pandas as pd
import numpy as np
from geopy.distance import geodesic
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

incident_data = pd.read_csv(r'C:\Users\jerom\OneDrive\Desktop\HACKATHON\ResponSync\data\incident_data.csv')
resource_table = pd.read_csv(r"C:\Users\jerom\OneDrive\Desktop\HACKATHON\ResponSync\data\resource_table.csv")

traffic_data = pd.read_csv(r"C:\Users\jerom\OneDrive\Desktop\HACKATHON\ResponSync\data\Banglore_traffic_Dataset.csv")

incident_data.columns = incident_data.columns.str.strip().str.lower()
resource_table.columns = resource_table.columns.str.strip()
traffic_data.columns = traffic_data.columns.str.strip().str.lower()

if 'incident_id' not in incident_data.columns:
    incident_data['incident_id'] = incident_data.index + 1

# Convert report_time to datetime and extract time features
incident_data['report_time'] = pd.to_datetime(incident_data['report_time'], errors='coerce')
incident_data['report_hour'] = incident_data['report_time'].dt.hour
incident_data['report_dayofweek'] = incident_data['report_time'].dt.dayofweek

# Calculate distance between two coordinates
def calculate_distance(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).km

def get_closest_distance(row, resources):
    lat, lon = row['location_latitude'], row['location_longitude']
    min_distance = float('inf')
    for _, res in resources.iterrows():
        dist = calculate_distance(lat, lon, res['Current Latitude'], res['Current Longitude'])
        min_distance = min(min_distance, dist)
    return min_distance

# Compute closest resource distance
incident_data['distance'] = incident_data.apply(lambda row: get_closest_distance(row, resource_table), axis=1)

# Select relevant traffic columns
traffic_data = traffic_data[['area name', 'road/intersection name', 'traffic volume', 'average speed', 
                             'congestion level', 'incident reports', 'weather conditions']]

def match_traffic(row):
    area_name = row['address'].split(",")[0].strip()
    matched = traffic_data[traffic_data['area name'].str.contains(area_name, case=False, na=False)]
    if not matched.empty:
        return matched.iloc[0]
    return pd.Series([np.nan] * len(traffic_data.columns), index=traffic_data.columns)

# Reset index and align traffic data correctly
incident_data = incident_data.reset_index(drop=True)
matched_traffic_df = incident_data.apply(match_traffic, axis=1)
incident_data = pd.concat([incident_data, matched_traffic_df.reset_index(drop=True)], axis=1)

# Fill missing values
incident_data['traffic volume'].fillna(incident_data['traffic volume'].mean(), inplace=True)
incident_data['average speed'].fillna(incident_data['average speed'].mean(), inplace=True)
incident_data['congestion level'].fillna(incident_data['congestion level'].mean(), inplace=True)
incident_data['incident reports'].fillna(1, inplace=True)
incident_data['weather conditions'] = incident_data['weather conditions'].astype('category').cat.codes

traffic_features = ['distance', 'report_hour', 'report_dayofweek', 'traffic volume', 
                    'average speed', 'congestion level', 'incident reports', 'weather conditions']
X_traffic = incident_data[traffic_features]
y_traffic = incident_data['congestion level']

traffic_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', LinearRegression())
])
traffic_pipeline.fit(X_traffic, y_traffic)
incident_data['predicted_traffic_factor'] = traffic_pipeline.predict(X_traffic)

incident_data['response_time'] = (
    incident_data['distance'] * 5 +
    incident_data['predicted_traffic_factor'] * 10 +
    np.random.normal(0, 5, len(incident_data))
).round(2)

# Train response time prediction model
response_features = ['distance', 'predicted_traffic_factor']
y_response = incident_data['response_time']
response_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', LinearRegression())
])
response_pipeline.fit(incident_data[response_features], y_response)
incident_data['predicted_response_time'] = response_pipeline.predict(incident_data[response_features]).round(2)

#output
output_data = incident_data[['incident_id', 'address', 'type', 'severity', 'distance', 
                             'average speed', 'predicted_traffic_factor', 'predicted_response_time']]

output_data = output_data.reset_index(drop=True)
output_data.index += 1
output_data.index.name = 'S.No.'

output_data.to_csv(r'C:\Users\jerom\OneDrive\Desktop\HACKATHON\ResponSync\data\final_incident_predictions.csv', index=True)
pd.set_option('display.max_columns', None)
print(output_data.head())
