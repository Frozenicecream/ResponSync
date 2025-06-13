-- Drop tables if they exist to start fresh (for development/testing)
DROP TABLE IF EXISTS incidents;
DROP TABLE IF EXISTS resources;
DROP TABLE IF EXISTS allocations;
DROP TABLE IF EXISTS current_incidents;
DROP TABLE IF EXISTS current_resources;
DROP TABLE IF EXISTS current_allocations;
DROP TABLE IF EXISTS all_incidents;
DROP TABLE IF EXISTS all_resources;
DROP TABLE IF EXISTS all_allocations;

-- Create the incidents table
CREATE TABLE incidents (
    incident_id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_latitude REAL NOT NULL,
    location_longitude REAL NOT NULL,
    address VARCHAR(255),
    pincode VARCHAR(6),
    severity INTEGER NOT NULL,
    type TEXT NOT NULL,
    report_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create the resources table
CREATE TABLE resources (
    resource_id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    current_latitude REAL NOT NULL,
    current_longitude REAL NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('available', 'en_route', 'occupied'))
);

-- Create the allocations table
CREATE TABLE allocations (
    allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INTEGER NOT NULL,
    resource_id INTEGER NOT NULL,
    assignment_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    predicted_response_time REAL, -- In minutes or seconds, specify in your code
    FOREIGN KEY (incident_id) REFERENCES incidents(incident_id),
    FOREIGN KEY (resource_id) REFERENCES resources(resource_id)
    UNIQUE (incident_id)
);

CREATE TABLE current_incidents (
    incident_id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_latitude REAL NOT NULL,
    location_longitude REAL NOT NULL,
    severity INTEGER NOT NULL,
    type TEXT NOT NULL,
    report_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE current_resources (
    resource_id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    current_latitude REAL NOT NULL,
    current_longitude REAL NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('available', 'en_route', 'occupied'))
);

CREATE TABLE current_allocations (
    allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INTEGER NOT NULL,
    resource_id INTEGER NOT NULL,
    assignment_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    predicted_response_time REAL,
    FOREIGN KEY (incident_id) REFERENCES current_incidents(incident_id),
    FOREIGN KEY (resource_id) REFERENCES current_resources(resource_id),
    UNIQUE (incident_id) 
);  

CREATE TABLE all_incidents (
    incident_id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_latitude REAL NOT NULL,
    location_longitude REAL NOT NULL,
    severity INTEGER NOT NULL,
    type TEXT NOT NULL,
    report_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE all_resources (
    resource_id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    current_latitude REAL NOT NULL,
    current_longitude REAL NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('available', 'en_route', 'occupied'))
);

CREATE TABLE all_allocations (
    allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INTEGER NOT NULL,
    resource_id INTEGER NOT NULL,
    assignment_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    predicted_response_time REAL,
    FOREIGN KEY (incident_id) REFERENCES current_incidents(incident_id),
    FOREIGN KEY (resource_id) REFERENCES current_resources(resource_id),
    UNIQUE (incident_id) 
); 

--Insertion of elements into incidents table
INSERT INTO incidents (location_latitude, location_longitude, address, pincode, severity, type, report_time) VALUES
(12.9716, 77.5946, 'MG Road', 560001, 3, 'medical', '2025-05-01 14:30:00'),
(12.9352, 77.6142, 'Jayanagar', 560041, 2, 'accident', '2025-05-01 15:10:00'),
(13.0352, 77.5970, 'Hebbal', 560024, 4, 'medical', '2025-05-01 16:00:00'),
(12.9611, 77.6387, 'Indiranagar', 560038, 5, 'medical', '2025-05-01 16:45:00'),
(12.9081, 77.6476, 'HSR Layout', 560102, 1, 'accident', '2025-05-01 17:30:00'),
(12.9350, 77.6250, 'Koramangala', 560034, 2, 'crime', '2025-05-01 11:20:00'),
(12.9698, 77.7499, 'Whitefield', 560066, 3, 'medical', '2025-05-01 10:10:00'),
(13.0100, 77.5500, 'Yeshwanthpur', 560022, 4, 'accident', '2025-05-01 08:30:00'),
(12.9189, 77.5739, 'Banashankari', 560085, 2, 'medical', '2025-05-01 09:50:00'),
(12.9915, 77.5560, 'Rajajinagar', 560010, 1, 'medical', '2025-05-01 07:40:00'),
(12.9611, 77.6387, 'Indiranagar', 560038, 3, 'accident', '2025-05-01 06:15:00'),
(12.9352, 77.6142, 'Jayanagar', 560041, 4, 'medical', '2025-05-01 06:45:00'),
(13.0100, 77.5500, 'Yeshwanthpur', 560022, 2, 'medical', '2025-05-01 07:10:00'),
(12.9915, 77.5560, 'Rajajinagar', 560010, 3, 'medical', '2025-05-01 07:25:00'),
(12.9189, 77.5739, 'Banashankari', 560085, 1, 'crime', '2025-05-01 08:00:00'),
(12.9698, 77.7499, 'Whitefield', 560066, 5, 'crime', '2025-05-01 08:20:00'),
(12.9716, 77.5946, 'MG Road', 560001, 2, 'accident', '2025-05-01 08:40:00'),
(12.9081, 77.6476, 'HSR Layout', 560102, 3, 'medical', '2025-05-01 08:55:00'),
(12.9350, 77.6250, 'Koramangala', 560034, 4, 'crime', '2025-05-01 09:10:00'),
(13.0352, 77.5970, 'Hebbal', 560024, 3, 'crime', '2025-05-01 09:35:00'),
(12.9611, 77.6387, 'Indiranagar', 560038, 2, 'medical', '2025-05-01 09:50:00'),
(12.9352, 77.6142, 'Jayanagar', 560041, 5, 'accident', '2025-05-01 10:05:00'),
(13.0100, 77.5500, 'Yeshwanthpur', 560022, 1, 'crime', '2025-05-01 10:25:00'),
(12.9915, 77.5560, 'Rajajinagar', 560010, 2, 'crime', '2025-05-01 10:45:00'),
(12.9189, 77.5739, 'Banashankari', 560085, 4, 'accident', '2025-05-01 11:00:00'),
(12.9698, 77.7499, 'Whitefield', 560066, 3, 'medical', '2025-05-01 11:20:00'),
(12.9716, 77.5946, 'MG Road', 560001, 2, 'crime', '2025-05-01 11:35:00'),
(12.9081, 77.6476, 'HSR Layout', 560102, 5, 'crime', '2025-05-01 11:55:00'),
(12.9350, 77.6250, 'Koramangala', 560034, 3, 'accident', '2025-05-01 12:10:00'),
(13.0352, 77.5970, 'Hebbal', 560024, 1, 'fire', '2025-05-01 12:25:00'),
(12.9611, 77.6387, 'Indiranagar', 560038, 4, 'medical', '2025-05-01 12:45:00'),
(12.9352, 77.6142, 'Jayanagar', 560041, 3, 'crime', '2025-05-01 13:05:00'),
(13.0100, 77.5500, 'Yeshwanthpur', 560022, 2, 'fire', '2025-05-01 13:20:00'),
(12.9915, 77.5560, 'Rajajinagar', 560010, 5, 'accident', '2025-05-01 13:40:00'),
(12.9189, 77.5739, 'Banashankari', 560085, 3, 'fire', '2025-05-01 14:00:00'),
(12.9698, 77.7499, 'Whitefield', 560066, 4, 'medical', '2025-05-01 14:15:00'),
(12.9716, 77.5946, 'MG Road', 560001, 2, 'accident', '2025-05-01 14:30:00'),
(12.9081, 77.6476, 'HSR Layout', 560102, 1, 'crime', '2025-05-01 14:45:00'),
(12.9350, 77.6250, 'Koramangala', 560034, 3, 'fire', '2025-05-01 15:00:00'),
(13.0352, 77.5970, 'Hebbal', 560024, 4, 'fire', '2025-05-01 15:20:00'),
(12.9611, 77.6387, 'Indiranagar', 560038, 5, 'accident', '2025-05-01 15:35:00'),
(12.9352, 77.6142, 'Jayanagar', 560041, 2, 'fire', '2025-05-01 15:50:00'),
(13.0100, 77.5500, 'Yeshwanthpur', 560022, 3, 'medical', '2025-05-01 16:05:00'),
(12.9915, 77.5560, 'Rajajinagar', 560010, 4, 'crime', '2025-05-01 16:20:00'),
(12.9189, 77.5739, 'Banashankari', 560085, 2, 'accident', '2025-05-01 16:35:00'),
(12.9698, 77.7499, 'Whitefield', 560066, 1, 'fire', '2025-05-01 16:45:00'),
(12.9716, 77.5946, 'MG Road', 560001, 3, 'fire', '2025-05-01 17:00:00'),
(12.9081, 77.6476, 'HSR Layout', 560102, 4, 'medical', '2025-05-01 17:15:00'),
(12.9350, 77.6250, 'Koramangala', 560034, 2, 'accident', '2025-05-01 17:30:00'),
(13.0352, 77.5970, 'Hebbal', 560024, 3, 'fire', '2025-05-01 17:45:00'),
(12.9611, 77.6387, 'Indiranagar', 560038, 4, 'crime', '2025-05-01 18:00:00'),
(12.9352, 77.6142, 'Jayanagar', 560041, 1, 'medical', '2025-05-01 18:10:00'),
(13.0100, 77.5500, 'Yeshwanthpur', 560022, 5, 'accident', '2025-05-01 18:25:00'),
(12.9915, 77.5560, 'Rajajinagar', 560010, 3, 'fire', '2025-05-01 18:40:00'),
(12.9189, 77.5739, 'Banashankari', 560085, 2, 'crime', '2025-05-01 18:55:00'),
(12.9698, 77.7499, 'Whitefield', 560066, 4, 'accident', '2025-05-01 19:10:00'),
(12.9716, 77.5946, 'MG Road', 560001, 1, 'medical', '2025-05-01 19:25:00'),
(12.9081, 77.6476, 'HSR Layout', 560102, 3, 'fire', '2025-05-01 19:35:00'),
(12.9350, 77.6250, 'Koramangala', 560034, 5, 'fire', '2025-05-01 19:50:00'),
(13.0352, 77.5970, 'Hebbal', 560024, 4, 'accident', '2025-05-01 20:05:00'),
(12.9611, 77.6387, 'Indiranagar', 560038, 2, 'fire', '2025-05-01 20:20:00'),
(12.9352, 77.6142, 'Jayanagar', 560041, 3, 'crime', '2025-05-01 20:30:00'),
(13.0100, 77.5500, 'Yeshwanthpur', 560022, 1, 'medical', '2025-05-01 20:45:00'),
(12.9915, 77.5560, 'Rajajinagar', 560010, 4, 'accident', '2025-05-01 21:00:00'),
(12.9189, 77.5739, 'Banashankari', 560085, 2, 'fire', '2025-05-01 21:15:00'),
(12.9698, 77.7499, 'Whitefield', 560066, 3, 'fire', '2025-05-01 21:30:00'),
(12.9716, 77.5946, 'MG Road', 560001, 5, 'accident', '2025-05-01 21:45:00'),
(12.9081, 77.6476, 'HSR Layout', 560102, 1, 'crime', '2025-05-01 22:00:00'),
(12.9350, 77.6250, 'Koramangala', 560034, 4, 'medical', '2025-05-01 22:10:00'),
(13.0352, 77.5970, 'Hebbal', 560024, 3, 'accident', '2025-05-01 22:25:00'),
(12.9611, 77.6387, 'Indiranagar', 560038, 2, 'fire', '2025-05-01 22:40:00'),
(12.9352, 77.6142, 'Jayanagar', 560041, 3, 'medical', '2025-05-01 22:50:00'),
(13.0100, 77.5500, 'Yeshwanthpur', 560022, 4, 'accident', '2025-05-01 23:05:00'),
(12.9915, 77.5560, 'Rajajinagar', 560010, 5, 'crime', '2025-05-01 23:20:00'),
(12.9189, 77.5739, 'Banashankari', 560085, 1, 'fire', '2025-05-01 23:30:00'),
(12.9698, 77.7499, 'Whitefield', 560066, 3, 'fire', '2025-05-01 23:40:00'),
(12.9716, 77.5946, 'MG Road', 560001, 2, 'accident', '2025-05-01 23:50:00'),
(12.9081, 77.6476, 'HSR Layout', 560102, 4, 'medical', '2025-05-02 00:00:00'),
(12.9350, 77.6250, 'Koramangala', 560034, 3, 'fire', '2025-05-02 00:15:00'),
(13.0352, 77.5970, 'Hebbal', 560024, 1, 'crime', '2025-05-02 00:25:00'),
(12.9611, 77.6387, 'Indiranagar', 560038, 4, 'accident', '2025-05-02 00:35:00'),
(12.9352, 77.6142, 'Jayanagar', 560041, 2, 'medical', '2025-05-02 00:45:00'),
(13.0100, 77.5500, 'Yeshwanthpur', 560022, 5, 'fire', '2025-05-02 01:00:00'),
(12.9915, 77.5560, 'Rajajinagar', 560010, 3, 'accident', '2025-05-02 01:15:00'),
(12.9189, 77.5739, 'Banashankari', 560085, 4, 'fire', '2025-05-02 01:30:00'),
(12.9698, 77.7499, 'Whitefield', 560066, 2, 'crime', '2025-05-02 01:40:00');


--Insertion of data into resources table
INSERT INTO resources (type, current_latitude, current_longitude, status) VALUES
('Ambulance', 12.9497, 77.6716, 'available'),
('Ambulance', 12.8949, 77.618, 'available'),
('Police Car', 12.8806, 77.6736, 'available'),
('Police Car', 12.9563, 77.6751, 'available'),
('Police Car', 12.882, 77.6489, 'available'),
('Ambulance', 13.0058, 77.65, 'available'),
('Ambulance', 12.9881, 77.6719, 'available'),
('Police Car', 12.9779, 77.6414, 'available'),
('Ambulance', 12.9388, 77.6601, 'available'),
('Fire Truck', 12.9722, 77.6743, 'available'),
('Ambulance', 13.0315, 77.6148, 'available'),
('Ambulance', 13.0267, 77.6161, 'available'),
('Ambulance', 12.8928, 77.5968, 'available'),
('Ambulance', 12.994, 77.6387, 'available'),
('Ambulance', 12.9674, 77.6334, 'available'),
('Police Car', 12.9545, 77.6018, 'available'),
('Ambulance', 12.905, 77.5925, 'available'),
('Fire Truck', 12.9292, 77.6402, 'available'),
('Fire Truck', 13.0007, 77.6394, 'available'),
('Fire Truck', 13.0202, 77.6472, 'available'),
('Police Car', 12.9261, 77.6201, 'available'),
('Ambulance', 12.9443, 77.679, 'available'),
('Fire Truck', 12.8879, 77.6751, 'available'),
('Police Car', 13.0224, 77.5844, 'available'),
('Police Car', 12.9805, 77.6245, 'available'),
('Police Car', 12.9956, 77.6397, 'available'),
('Fire Truck', 12.9785, 77.6196, 'available'),
('Police Car', 12.8857, 77.6602, 'available'),
('Fire Truck', 12.9255, 77.6849, 'available'),
('Ambulance', 12.9783, 77.6324, 'available'),
('Police Car', 12.8819, 77.6505, 'available'),
('Ambulance', 12.9291, 77.5934, 'available'),
('Ambulance', 12.9735, 77.6747, 'available'),
('Police Car', 12.9029, 77.6444, 'available'),
('Ambulance', 13.0339, 77.6525, 'available'),
('Police Car', 13.0345, 77.6367, 'available'),
('Police Car', 13.0318, 77.6279, 'available'),
('Fire Truck', 12.8948, 77.592, 'available'),
('Ambulance', 12.9107, 77.601, 'available'),
('Ambulance', 13.0153, 77.6141, 'available'),
('Fire Truck', 13.0152, 77.5906, 'available'),
('Ambulance', 12.9625, 77.6616, 'available'),
('Ambulance', 12.9166, 77.5958, 'available'),
('Ambulance', 12.9388, 77.637, 'available'),
('Police Car', 12.9533, 77.5948, 'available'),
('Police Car', 12.9354, 77.5941, 'available'),
('Ambulance', 12.9811, 77.6362, 'available'),
('Ambulance', 12.957, 77.5941, 'available'),
('Police Car', 12.9473, 77.5887, 'available'),
('Ambulance', 13.0339, 77.6255, 'available'),
('Fire Truck', 12.976, 77.6036, 'available'),
('Police Car', 12.9207, 77.6263, 'available'),
('Police Car', 12.967, 77.6447, 'available'),
('Fire Truck', 13.0196, 77.617, 'available'),
('Ambulance', 12.8879, 77.6581, 'available'),
('Ambulance', 12.9053, 77.6531, 'available'),
('Ambulance', 12.9435, 77.6599, 'available'),
('Police Car', 12.8902, 77.6562, 'available'),
('Fire Truck', 13.032, 77.6158, 'available'),
('Police Car', 12.8835, 77.6183, 'available'),
('Fire Truck', 12.9831, 77.6283, 'available'),
('Ambulance', 12.9292, 77.6655, 'available'),
('Ambulance', 12.9206, 77.5891, 'available'),
('Ambulance', 13.0123, 77.6882, 'available'),
('Ambulance', 13.0344, 77.5916, 'available'),
('Ambulance', 13.0195, 77.6806, 'available'),
('Fire Truck', 12.9074, 77.5821, 'available'),
('Ambulance', 12.9913, 77.6045, 'available'),
('Fire Truck', 13.0025, 77.612, 'available'),
('Fire Truck', 13.0217, 77.6848, 'available'),
('Police Car', 12.894, 77.6285, 'available'),
('Ambulance', 12.9969, 77.6524, 'available'),
('Ambulance', 12.8874, 77.6634, 'available'),
('Ambulance', 13.0227, 77.6553, 'available'),
('Police Car', 12.9584, 77.6036, 'available'),
('Fire Truck', 12.9545, 77.6734, 'available'),
('Ambulance', 12.9349, 77.6028, 'available'),
('Ambulance', 12.9158, 77.6432, 'available'),
('Fire Truck', 13.0297, 77.689, 'available'),
('Ambulance', 12.9614, 77.6234, 'available'),
('Police Car', 12.9229, 77.6421, 'available'),
('Police Car', 12.9001, 77.6751, 'available'),
('Ambulance', 12.9403, 77.6702, 'available'),
('Fire Truck', 12.9922, 77.6365, 'available'),
('Ambulance', 12.9554, 77.6259, 'available'),
('Fire Truck', 12.9296, 77.6774, 'available'),
('Police Car', 12.9118, 77.5825, 'available'),
('Fire Truck', 12.9046, 77.6749, 'available'),
('Fire Truck', 12.9685, 77.6502, 'available'),
('Ambulance', 12.9535, 77.6099, 'available'),
('Police Car', 12.9002, 77.5811, 'available'),
('Fire Truck', 13.0226, 77.5955, 'available'),
('Fire Truck', 12.9936, 77.5953, 'available'),
('Ambulance', 12.93, 77.6363, 'available'),
('Police Car', 13.0027, 77.6325, 'available'),
('Ambulance', 13.004, 77.6084, 'available'),
('Ambulance', 12.9214, 77.6329, 'available'),
('Ambulance', 12.963, 77.5846, 'available'),
('Ambulance', 13.0291, 77.6081, 'available'),
('Police Car', 12.9107, 77.6823, 'available');
