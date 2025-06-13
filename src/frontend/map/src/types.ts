import L from 'leaflet';

export interface Coordinates {
  lat: number;
  lng: number;
}

// Assumes API is updated to include IDs
export interface ApiIncident {
  incident_id: number; // Essential for tracking
  location_latitude: number;
  location_longitude: number;
  severity: string;
  type: string;
}

// Assumes API is updated to include IDs
export interface ApiResource {
  resource_id: number; // Essential for tracking
  current_latitude: number;
  current_longitude: number;
  type: string;
  status: string; // 'available', 'en_route', 'occupied'
}

export interface TrafficRoad {
  road: string;
  area: string;
  startlat: number;
  startlong: number;
  endlat: number;
  endlong: number;
  trafficvolume: number;
}

// Assumes /api/routepair is updated to include IDs and ETA
export interface ApiRoutePair {
  allocation_id: number; // Added
  incident: Coordinates & { incident_id?: number | null }; // Changed from id to incident_id
  resource: { // Modified to include type and status
    lat: number;
    lng: number;
    resource_id?: number | null;
    type: string; // Added
    status: string; // Added
  };
  predicted_eta_seconds?: number; // Estimated time from routing or DB
}

export interface RouteDetails {
  coordinates: L.LatLngTuple[];
  totalTimeSeconds: number;
  totalDistanceMeters: number;
}

// Used to store KPI data
export interface KPIData {
  incident_distribution : IncidentDistribution;
  resource_distribution : ResourceDistribution;
  average_allocation_time : string;
  simulation_length : string;
  total_allocations : number;
  allocation_details : AllocationDetails[];
}
export interface DistributionDataItem {
  name: string;
  value: string; 
}

export type IncidentDistribution = DistributionDataItem[];
export type ResourceDistribution = DistributionDataItem[];

export interface AllocationDetails {
  allocation_id : number;
  allocation_time_seconds : string; 
  incident_type : string;
  resource_type : string;
  severity : number;
}