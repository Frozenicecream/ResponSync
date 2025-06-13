import React from 'react';
import { Marker, Tooltip } from 'react-leaflet';
import L from 'leaflet';
import { ApiResource } from '../types';

interface ResourceMarkersProps {
  resources: ApiResource[];
  resourceIcon: L.Icon | L.DivIcon;
}

const ResourceMarkers: React.FC<ResourceMarkersProps> = ({ resources, resourceIcon }) => {
  return (
    <>
      {resources.map((resource) => (
        <Marker
          key={`resource-${resource.resource_id}`}
          position={[resource.current_latitude, resource.current_longitude]}
          icon={resourceIcon}
          zIndexOffset={1000} // Ensure resources appear above other markers
        >
          <Tooltip permanent={false} direction="top">
            <div>
              <strong>Resource ID: {resource.resource_id}</strong><br />
              Type: {resource.type}<br />
              Status: {resource.status}<br />
              Lat: {resource.current_latitude}<br />
              Lng: {resource.current_longitude}
            </div>
          </Tooltip>
        </Marker>
      ))}
    </>
  );
};

export default ResourceMarkers;