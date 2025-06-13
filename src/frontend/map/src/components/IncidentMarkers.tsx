import React from 'react';
import { Marker, Tooltip } from 'react-leaflet';
import L from 'leaflet';
import { ApiIncident } from '../types';

interface IncidentMarkersProps {
  incidents: ApiIncident[];
}

const hazardIcon = L.icon({
  iconUrl: 'https://cdn-icons-png.flaticon.com/512/564/564619.png', // Same as map.html
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -30],
});

const IncidentMarkers: React.FC<IncidentMarkersProps> = ({ incidents }) => {
  return (
    <>
      {incidents.map((incident) => (
        <Marker
          key={`incident-${incident.incident_id}`}
          position={[incident.location_latitude, incident.location_longitude]}
          icon={hazardIcon}
        >
          <Tooltip>
            <div>
              <strong>Incident ID: {incident.incident_id}</strong><br />
              Type: {incident.type}<br />
              Severity: {incident.severity}<br />
              Lat: {incident.location_latitude}<br />
              Lng: {incident.location_longitude}
            </div>
          </Tooltip>
        </Marker>
      ))}
    </>
  );
};

export default IncidentMarkers;