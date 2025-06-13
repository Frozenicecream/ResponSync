import React, { useRef, useState, useEffect, useCallback } from 'react';
import { MapContainer, TileLayer } from 'react-leaflet';
import L from 'leaflet';
import { Link } from 'react-router-dom'; // Import Link
import IncidentMarkers from './IncidentMarkers';
import ResourceMarkers from './ResourceMarkers';
import TrafficLayer from './TrafficLayer';
import AllocationRouting from './AllocationRouting';
import { ApiIncident, ApiResource, TrafficRoad, ApiRoutePair, RouteDetails } from '../types';

// Bangalore coordinates
const initialCenter: L.LatLngTuple = [12.9716, 77.5946];
const initialZoom = 13;

// URLs - adjust if not using proxy or if backend is elsewhere
const INCIDENTS_API_URL = '/api/incidents';
const RESOURCES_API_URL = '/api/resources'; // Removed limit, timestamp added in fetch
const TRAFFIC_API_URL = '/data/bangaloretrafficcoord.json'; // Path relative to the public folder
const ACTIVE_ALLOCATIONS_API_URL = '/api/routepair'; // Changed name for clarity, points to the modified endpoint

const MapComponent: React.FC = () => {
  const [incidents, setIncidents] = useState<ApiIncident[]>([]);
  const [resources, setResources] = useState<ApiResource[]>([]);
  const [trafficData, setTrafficData] = useState<TrafficRoad[]>([]);
  const [activeAllocations, setActiveAllocations] = useState<ApiRoutePair[]>([]);
  const [etas, setEtas] = useState<Record<number, string | null>>({});
  const completedAllocationIds = useRef<Set<number>>(new Set()); // Use useRef for a mutable set

  const fetchData = useCallback(async () => {
    try {
      // Fetch Incidents
      const incidentsRes = await fetch(`${INCIDENTS_API_URL}?t=${new Date().getTime()}`); // Added cache buster
      if (!incidentsRes.ok) throw new Error(`Failed to fetch incidents: ${incidentsRes.status}`);
      const incidentsData: ApiIncident[] = await incidentsRes.json();
      setIncidents(incidentsData);
      console.log(`Fetched ${incidentsData.length} incidents.`);

      // Fetch Resources
      const resourcesRes = await fetch(`${RESOURCES_API_URL}?t=${new Date().getTime()}`); // Added cache buster
      if (!resourcesRes.ok) throw new Error(`Failed to fetch resources: ${resourcesRes.status}`);
      const resourcesData: ApiResource[] = await resourcesRes.json();
      setResources(resourcesData);
      console.log(`Fetched ${resourcesData.length} resources.`);

      // Fetch Traffic Data (only once or less frequently if it's static)
      if (trafficData.length === 0) {
        const trafficRes = await fetch(TRAFFIC_API_URL);
        if (!trafficRes.ok) throw new Error(`Failed to fetch traffic data: ${trafficRes.status}`);
        const trafficJsonData: TrafficRoad[] = await trafficRes.json();
        setTrafficData(trafficJsonData);
      }

      // Fetch Active Allocations
      const activeAllocationsRes = await fetch(ACTIVE_ALLOCATIONS_API_URL);
      if (!activeAllocationsRes.ok) throw new Error(`Failed to fetch active allocations: ${activeAllocationsRes.status}`);
      let activeAllocationsData: ApiRoutePair[] = await activeAllocationsRes.json();

      // Filter out allocations that have been locally marked as complete
      activeAllocationsData = activeAllocationsData.filter(
        (alloc) => !completedAllocationIds.current.has(alloc.allocation_id)
      );

      setActiveAllocations(activeAllocationsData);

      // Clear ETAs for allocations that no longer exist
      setEtas(prevEtas => {
        const newEtas: Record<number, string | null> = {};
        activeAllocationsData.forEach(alloc => {
          if (prevEtas[alloc.allocation_id]) {
            newEtas[alloc.allocation_id] = prevEtas[alloc.allocation_id];
          }
        });
        return newEtas;
      });

    } catch (error) {
      console.error("Error fetching map data:", error);
    }
  }, [trafficData.length]);

  useEffect(() => {
    fetchData(); // Initial fetch
    const interval = setInterval(fetchData, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, [fetchData]);

  const handleRouteFound = useCallback((allocationId: number, details: RouteDetails) => {
    console.log(`Route found for allocation ${allocationId}:`, details);
  }, []);

  const handleEtaUpdate = useCallback((allocationId: number, etaMessage: string | null) => {
    setEtas(prevEtas => ({
      ...prevEtas,
      [allocationId]: etaMessage,
    }));
  }, []);

  const handleAmbulanceArrived = useCallback(async (allocationId: number) => {
    // If this allocation is already in the completed set, don't try to complete it again
    if (completedAllocationIds.current.has(allocationId)) {
      return;
    }

    console.log(`Ambulance for allocation ${allocationId} reported arrival sequence started.`);
    
    // Add the completed allocation ID to the set
    completedAllocationIds.current.add(allocationId);

    // Remove the allocation from the local state to update the map
    setActiveAllocations(prevAllocations =>
      prevAllocations.filter(alloc => alloc.allocation_id !== allocationId)
    );
    // Clear ETA for the completed allocation
    setEtas(prevEtas => {
      const newEtas = { ...prevEtas };
      delete newEtas[allocationId];
      return newEtas;
    });
    
    try {
      const response = await fetch(`/api/allocation/complete/${allocationId}`, { method: 'POST' });
      if (!response.ok) {
        const errorData = await response.json();
        // If we get a 404, it likely means the allocation was already completed
        if (response.status === 404) {
          console.log(`Allocation ${allocationId} was already completed on the backend.`);
          return;
        }
        throw new Error(`Failed to complete allocation ${allocationId}: ${errorData.error || response.statusText}`);
      }
      console.log(`Allocation ${allocationId} successfully marked as complete on backend.`);

    } catch (error) {
      console.error("Error completing allocation:", error);
      // Don't remove from completedAllocationIds or retry on error
      // This prevents the retry loop
    }
  }, []); // Empty dependency array since it doesn't depend on any props or state

  const allocatedResourceIds = activeAllocations
    .map(alloc => alloc.resource.resource_id)
    .filter(id => id !== null && id !== undefined) as number[];

  // Filter out resources that are currently allocated
  const unallocatedResources = resources.filter(r => !allocatedResourceIds.includes(r.resource_id));

  const resourceIcon = L.icon({
    iconUrl: '/images/marker-icon.png',
    iconRetinaUrl: '/images/marker-icon-2x.png',
    shadowUrl: '/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  });

  return (
    <div style={{ position: 'relative', height: '100vh', width: '100%' }}>
      <Link to="/dashboard" className="dashboard-nav-button">
        End simulation
      </Link>
      <MapContainer center={initialCenter} zoom={initialZoom} style={{ height: '100%', width: '100%' }}>
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        <IncidentMarkers incidents={incidents} />
        <ResourceMarkers resources={unallocatedResources} resourceIcon={resourceIcon} />
        <TrafficLayer trafficData={trafficData} />
        {activeAllocations.map(allocation => (
          <AllocationRouting
            key={allocation.allocation_id}
            routePair={allocation}
            onRouteFound={(details) => handleRouteFound(allocation.allocation_id, details)}
            onAmbulanceArrived={() => handleAmbulanceArrived(allocation.allocation_id)}
            onEtaUpdate={handleEtaUpdate}
            showEta={true} 
          />
        ))}
      </MapContainer>
      <div 
        id="eta-display-container" 
        style={{ 
          position: 'absolute', 
          top: '10px', 
          right: '10px', 
          zIndex: 1000, 
          display: 'flex', 
          flexDirection: 'column', 
          gap: '5px',
          background: 'rgba(255, 255, 255, 0.8)', // Optional: background for better readability
          padding: '5px', // Optional: padding
          borderRadius: '3px' // Optional: border radius
        }}
      >
        {Object.entries(etas)
          .filter(([_, message]) => message !== null) // Filter out null messages
          .map(([allocationId, message]) => (
            <div key={`eta-${allocationId}`} style={{ background: 'white', padding: '5px', borderRadius: '3px', boxShadow: '0 0 5px rgba(0,0,0,0.3)'}}>
              {message}
            </div>
        ))}
      </div>
    </div>
  );
};

export default MapComponent;