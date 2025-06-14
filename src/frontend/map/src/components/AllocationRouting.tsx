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

// Cache for storing routes
const routeCache = new Map<string, L.Routing.IRoute>();

// Custom router to control requests
class CustomRouter extends L.Routing.OSRMv1 {
  constructor(options: any) {
    super(options);
  }

  route(waypoints: L.Routing.Waypoint[], callback: (err: any, routes?: L.Routing.IRoute[]) => void, context?: {}, options?: L.Routing.RoutingOptions) {
    const start = waypoints[0].latLng;
    const end = waypoints[waypoints.length - 1].latLng;
    const cacheKey = `${start.lat},${start.lng};${end.lat},${end.lng}`;

    // Check cache first
    const cachedRoute = routeCache.get(cacheKey);
    if (cachedRoute) {
      console.log('Using cached route for:', cacheKey);
      if (context) {
        callback.call(context, null, [cachedRoute]);
      } else {
        callback(null, [cachedRoute]);
      }
      return;
    }

    // If not in cache, make the request
    super.route(waypoints, (err: any, routes?: L.Routing.IRoute[]) => {
      if (!err && routes && routes.length > 0) {
        console.log('Caching new route for:', cacheKey);
        routeCache.set(cacheKey, routes[0]);
      }
      if (context) {
        callback.call(context, err, routes);
      } else {
        callback(err, routes);
      }
    }, context, options);
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
    if (!routePair) return;

    // Reset route found flag for new route pair
    routeFoundRef.current = false;

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

    const handleRouteFound = (route: L.Routing.IRoute) => {
      if (routeFoundRef.current) return;
      routeFoundRef.current = true;

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

        if (routePair.resource.type && routePair.resource.status) {
          ambulanceMarkerRef.current.bindTooltip(`
            <strong>Resource ID: ${routePair.resource.resource_id || 'N/A'}</strong><br />
            Type: ${routePair.resource.type}<br />
            Status: ${routePair.resource.status}
          `).openTooltip();
        }
        
        let i = 0;
        const moveAmbulance = () => {
          if (isRouteCompleted) return;
          
          if (i < routeCoordinates.length) {
            ambulanceMarkerRef.current?.setLatLng(routeCoordinates[i]);
            i++;
            setTimeout(moveAmbulance, 100);
          } else {
            if (!isRouteCompleted) {
              onAmbulanceArrived();
              setIsRouteCompleted(true);
              setTimeout(() => {
                if (ambulanceMarkerRef.current && map.hasLayer(ambulanceMarkerRef.current)) {
                  map.removeLayer(ambulanceMarkerRef.current);
                  ambulanceMarkerRef.current = null;
                }
              }, 3000);
            }
          }
        };
        moveAmbulance();
      }
    };

    const control = L.Routing.control({
      waypoints,
      router: new CustomRouter({
        serviceUrl: '/route/v1'
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

    control._allocationId = routePair.allocation_id;

    control.on('routesfound', (e: any) => {
      const routes = e.routes as L.Routing.IRoute[];
      if (routes.length > 0) {
        handleRouteFound(routes[0]);
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

    return () => {
      if (routingControlRef.current) {
        map.removeControl(routingControlRef.current);
        routingControlRef.current = null;
      }
    };
  }, [map, routePair?.allocation_id, onRouteFound, onAmbulanceArrived, onEtaUpdate, showEta]);

  return null;
};

export default AllocationRouting;