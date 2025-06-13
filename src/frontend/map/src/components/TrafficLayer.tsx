import React from 'react';
import { Polyline, Tooltip } from 'react-leaflet';
import { TrafficRoad } from '../types';

interface TrafficLayerProps {
  trafficData: TrafficRoad[];
}

const TrafficLayer: React.FC<TrafficLayerProps> = ({ trafficData }) => {
  const getTrafficColor = (volume: number): string => {
    if (volume > 50000) return 'red';
    if (volume > 30000) return 'orange';
    if (volume > 15000) return 'yellow';
    return 'green';
  };

  return (
    <>
      {trafficData.map((road, index) => (
        <Polyline
          key={`traffic-${index}-${road.road}`}
          positions={[
            [road.startlat, road.startlong],
            [road.endlat, road.endlong],
          ]}
          color={getTrafficColor(road.trafficvolume)}
          weight={4}
          opacity={0.7}
        >
          <Tooltip>
            <b>{road.road}</b><br />
            Area: {road.area}<br />
            Volume: {road.trafficvolume}
          </Tooltip>
        </Polyline>
      ))}
    </>
  );
};

export default TrafficLayer;