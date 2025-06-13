import React, { useEffect, useRef, useState } from 'react';
import { useMap, Tooltip } from 'react-leaflet'; // Added Tooltip
import L from 'leaflet';
import 'leaflet-routing-machine';
import { ApiRoutePair, RouteDetails } from '../types';
import ambulanceMarkerIconPath from '../static/ambulance.png'; 

// Ensure CSS for leaflet-routing-machine is imported, e.g., in App.tsx or index.tsx
// import 'leaflet-routing-machine/dist/leaflet-routing-machine.css';

// Extend the L.Routing.Control type to include our custom property
declare module 'leaflet' {
  namespace Routing {
    interface Control {
      _allocationId?: number;
    }
  }
}

interface AllocationRoutingProps {
  routePair: ApiRoutePair | null;
  onRouteFound: (details: RouteDetails) => void;
  onAmbulanceArrived: () => void;
  onEtaUpdate: (allocationId: number, etaMessage: string | null) => void; // Added
  showEta?: boolean;
}

const ambulanceIcon = L.icon({
  iconUrl: ambulanceMarkerIconPath, 
  iconSize: [50, 50],
  iconAnchor: [25, 25],
});

const AllocationRouting: React.FC<AllocationRoutingProps> = ({
  routePair,
  onRouteFound,
  onAmbulanceArrived,
  onEtaUpdate, // Added
  showEta
}) => {
  const map = useMap();
  const routingControlRef = useRef<L.Routing.Control | null>(null);
  const ambulanceMarkerRef = useRef<L.Marker | null>(null);
  const [etaMessage, setEtaMessage] = useState<string | null>(null);
  const [isRouteCompleted, setIsRouteCompleted] = useState<boolean>(false);
  const routeFoundRef = useRef<boolean>(false); // Add ref to track if route has been found

  useEffect(() => {
    if (!map || !routePair) return;

    // Only create new route if we don't have one or if the allocation ID changed
    if (!routingControlRef.current || routingControlRef.current._allocationId !== routePair.allocation_id) {
      // Clean up previous route and marker
      if (routingControlRef.current) {
        try {
          routingControlRef.current.setWaypoints([]);
        } catch (e) {
          console.warn("Error clearing waypoints on existing routing control:", e);
        }
        map.removeControl(routingControlRef.current);
        routingControlRef.current = null;
      }
      if (ambulanceMarkerRef.current) {
        if (map && map.hasLayer(ambulanceMarkerRef.current)) {
          map.removeLayer(ambulanceMarkerRef.current);
        }
        ambulanceMarkerRef.current = null;
      }

      const waypoints = [
        L.latLng(routePair.resource.lat, routePair.resource.lng),
        L.latLng(routePair.incident.lat, routePair.incident.lng),
      ];

      const control = L.Routing.control({
        waypoints,
        router: L.Routing.osrmv1({
          serviceUrl: process.env.OSRM_SERVICE_URL || 'https://router.project-osrm.org/route/v1', // Use environment variable with fallback to public demo server
        }),
        routeWhileDragging: false,
        addWaypoints: false,
        show: false,
        lineOptions: {
          styles: [{ color: 'blue', weight: 4, opacity: 0.8 }],
          extendToWaypoints: true,
          missingRouteTolerance: 5
        },
        createMarker: () => null,
      } as any);

      // Store allocation ID on the control instance
      control._allocationId = routePair.allocation_id;

      control.on('routesfound', (e: any) => {
        // Only process route if it hasn't been found yet for this routePair
        if (routeFoundRef.current) return;
        routeFoundRef.current = true;

        const routes = e.routes as L.Routing.IRoute[];
        if (routes.length > 0) {
          const route = routes[0];
          onRouteFound({
            coordinates: route.coordinates ? route.coordinates.map(c => [c.lat, c.lng] as L.LatLngTuple) : [],
            totalTimeSeconds: route.summary?.totalTime || 0,
            totalDistanceMeters: route.summary?.totalDistance || 0,
          });

          let currentEtaMsg = null;
          if (showEta && route.summary) {
            const minutes = Math.round(route.summary.totalTime / 60);
            currentEtaMsg = `ETA: ${minutes} min (Inc: ${routePair.incident.incident_id}, Res: ${routePair.resource.resource_id})`;
          } else if (showEta && routePair.predicted_eta_seconds) {
            const minutes = Math.round(routePair.predicted_eta_seconds / 60);
            currentEtaMsg = `Predicted ETA: ${minutes} min (Inc: ${routePair.incident.incident_id}, Res: ${routePair.resource.resource_id})`;
          }
          setEtaMessage(currentEtaMsg);
          onEtaUpdate(routePair.allocation_id, currentEtaMsg);

          // Animate ambulance
          const routeCoordinates = route.coordinates;
          if (routeCoordinates && routeCoordinates.length > 0) {
            if (ambulanceMarkerRef.current) {
              map.removeLayer(ambulanceMarkerRef.current);
            }
            ambulanceMarkerRef.current = L.marker(routeCoordinates[0], { icon: ambulanceIcon }).addTo(map);

            // Add Tooltip to ambulance marker
            if (routePair.resource.type && routePair.resource.status) {
              ambulanceMarkerRef.current.bindTooltip(`
                <strong>Resource ID: ${routePair.resource.resource_id || 'N/A'}</strong><br />
                Type: ${routePair.resource.type}<br />
                Status: ${routePair.resource.status}
              `).openTooltip();
            }
            
            let i = 0;
            const moveAmbulance = () => {
              // Stop if route is already completed
              if (isRouteCompleted) return;
              
              if (i < routeCoordinates.length) {
                ambulanceMarkerRef.current?.setLatLng(routeCoordinates[i]);
                i++;
                setTimeout(moveAmbulance, 50); // Adjust speed as needed
              } else {
                // Only call onAmbulanceArrived if it hasn't been called for this route yet
                if (!isRouteCompleted) {
                  onAmbulanceArrived();
                  setIsRouteCompleted(true); // Mark as completed
                  // Remove ambulance marker after arrival
                  setTimeout(() => {
                    if (ambulanceMarkerRef.current && map.hasLayer(ambulanceMarkerRef.current)) {
                      map.removeLayer(ambulanceMarkerRef.current);
                      ambulanceMarkerRef.current = null;
                    }
                  }, 3000); // Keep ambulance for 3s after arrival
                }
              }
            };
            moveAmbulance();
          }
        }
      })
      .on('routingerror', (e: any) => {
        console.error('Routing error:', e.error);
        const errorMsg = "Routing error";
        setEtaMessage(errorMsg);
        onEtaUpdate(routePair.allocation_id, errorMsg);
      })
      .addTo(map);

      routingControlRef.current = control;
    }

    // Cleanup function for when the component unmounts
    return () => {
      if (routingControlRef.current) {
        try {
          routingControlRef.current.setWaypoints([]);
        } catch (e) {
          console.warn("Error clearing waypoints during cleanup:", e);
        }
        map.removeControl(routingControlRef.current);
        routingControlRef.current = null;
      }
      if (ambulanceMarkerRef.current) {
        if (map && map.hasLayer(ambulanceMarkerRef.current)) {
          map.removeLayer(ambulanceMarkerRef.current);
        }
        ambulanceMarkerRef.current = null;
      }
    };
  }, [map, routePair?.allocation_id, onRouteFound, onAmbulanceArrived, onEtaUpdate, showEta]); // Only depend on allocation_id instead of entire routePair

  return null;
};

export default AllocationRouting;