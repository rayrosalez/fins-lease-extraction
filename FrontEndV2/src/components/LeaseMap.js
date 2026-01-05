import React from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, ZoomControl } from 'react-leaflet';
import { motion } from 'framer-motion';
import 'leaflet/dist/leaflet.css';
import './LeaseMap.css';

// City coordinates for major US markets (lat, lng)
const CITY_COORDINATES = {
  'San Francisco': { lat: 37.7749, lng: -122.4194, state: 'CA' },
  'Los Angeles': { lat: 34.0522, lng: -118.2437, state: 'CA' },
  'Seattle': { lat: 47.6062, lng: -122.3321, state: 'WA' },
  'Phoenix': { lat: 33.4484, lng: -112.0740, state: 'AZ' },
  'Denver': { lat: 39.7392, lng: -104.9903, state: 'CO' },
  'Dallas': { lat: 32.7767, lng: -96.7970, state: 'TX' },
  'Austin': { lat: 30.2672, lng: -97.7431, state: 'TX' },
  'Chicago': { lat: 41.8781, lng: -87.6298, state: 'IL' },
  'Atlanta': { lat: 33.7490, lng: -84.3880, state: 'GA' },
  'Miami': { lat: 25.7617, lng: -80.1918, state: 'FL' },
  'New York': { lat: 40.7128, lng: -74.0060, state: 'NY' },
  'Boston': { lat: 42.3601, lng: -71.0589, state: 'MA' }
};

const LeaseMap = ({ locations }) => {
  // Calculate max lease count for scaling
  const maxLeaseCount = Math.max(...locations.map(loc => loc.lease_count), 1);
  
  // Map locations to coordinates
  const mappedLocations = locations
    .map(loc => {
      const coords = CITY_COORDINATES[loc.city];
      if (coords) {
        return {
          ...loc,
          ...coords,
          // Scale circle size based on lease count (min 10, max 50)
          radius: 10 + (loc.lease_count / maxLeaseCount) * 40
        };
      }
      return null;
    })
    .filter(loc => loc !== null);

  // Calculate center of US for initial view
  const center = [39.8283, -98.5795]; // Geographic center of US
  const zoom = 4;

  return (
    <div className="lease-map-container-dark">
      <div className="map-header-dark">
        <h2 className="map-title-dark">Portfolio Geographic Distribution</h2>
        <p className="map-subtitle-dark">Interactive map showing property locations across major US markets</p>
      </div>

      <div className="map-wrapper-dark">
        <MapContainer 
          center={center} 
          zoom={zoom} 
          className="leaflet-map-dark"
          zoomControl={false}
          scrollWheelZoom={true}
        >
          {/* Dark mode tile layer */}
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          />
          
          <ZoomControl position="topright" />

          {/* City markers */}
          {mappedLocations.map((loc) => (
            <CircleMarker
              key={loc.city}
              center={[loc.lat, loc.lng]}
              radius={loc.radius / 2}
              pathOptions={{
                fillColor: '#FF3621',
                fillOpacity: 0.7,
                color: '#ff5540',
                weight: 2,
                opacity: 0.9
              }}
            >
              <Popup className="dark-popup">
                <div className="popup-content-dark">
                  <h3 className="popup-title">{loc.city}, {loc.state}</h3>
                  <div className="popup-stats">
                    <div className="popup-stat">
                      <span className="popup-label">Leases:</span>
                      <span className="popup-value">{loc.lease_count}</span>
                    </div>
                    <div className="popup-stat">
                      <span className="popup-label">Total Sqft:</span>
                      <span className="popup-value">{loc.total_sqft.toLocaleString()}</span>
                    </div>
                    <div className="popup-stat">
                      <span className="popup-label">Avg Rent PSF:</span>
                      <span className="popup-value">${loc.avg_rent_psf.toFixed(2)}</span>
                    </div>
                    <div className="popup-stat">
                      <span className="popup-label">Annual Rent:</span>
                      <span className="popup-value">${loc.total_annual_rent.toLocaleString()}</span>
                    </div>
                  </div>
                </div>
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>

      {/* Legend */}
      <div className="map-legend-dark">
        <div className="legend-title-dark">Legend</div>
        <div className="legend-items-dark">
          <div className="legend-item-dark">
            <div className="legend-marker-dark legend-marker-small-dark"></div>
            <span>Fewer leases</span>
          </div>
          <div className="legend-item-dark">
            <div className="legend-marker-dark legend-marker-medium-dark"></div>
            <span>Moderate</span>
          </div>
          <div className="legend-item-dark">
            <div className="legend-marker-dark legend-marker-large-dark"></div>
            <span>Many leases</span>
          </div>
        </div>
        <div className="legend-note-dark">
          Circle size represents number of leases. Click markers for details. Zoom and pan to explore.
        </div>
      </div>

      {/* Location summary cards */}
      <div className="location-cards-dark">
        {mappedLocations.slice(0, 6).map((loc, index) => (
          <motion.div
            key={loc.city}
            className="location-card-dark"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 + 0.5 }}
          >
            <div className="location-card-header-dark">
              <h3 className="location-city-dark">{loc.city}, {loc.state}</h3>
              <span className="location-count-dark">{loc.lease_count} leases</span>
            </div>
            <div className="location-stats-dark">
              <div className="location-stat-dark">
                <span className="stat-label-dark">Total Sqft</span>
                <span className="stat-value-dark">{loc.total_sqft.toLocaleString()}</span>
              </div>
              <div className="location-stat-dark">
                <span className="stat-label-dark">Avg Rent</span>
                <span className="stat-value-dark">${loc.avg_rent_psf.toFixed(2)}/SF</span>
              </div>
              <div className="location-stat-dark">
                <span className="stat-label-dark">Annual Rent</span>
                <span className="stat-value-dark">${(loc.total_annual_rent / 1000).toFixed(0)}K</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default LeaseMap;

