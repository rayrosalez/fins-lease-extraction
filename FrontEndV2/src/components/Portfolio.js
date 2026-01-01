import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FiRefreshCw } from 'react-icons/fi';
import LeaseMap from './LeaseMap';
import './Portfolio.css';

const API_BASE_URL = 'http://localhost:5001/api';

const Portfolio = () => {
  const [kpis, setKpis] = useState(null);
  const [recentExtractions, setRecentExtractions] = useState([]);
  const [allLeases, setAllLeases] = useState([]);
  const [marketSummary, setMarketSummary] = useState([]);
  const [locationData, setLocationData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchPortfolioData();
  }, []);

  const fetchPortfolioData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [kpiResponse, recentResponse, leasesResponse, marketResponse, locationResponse] = await Promise.all([
        fetch(`${API_BASE_URL}/portfolio/kpis`),
        fetch(`${API_BASE_URL}/portfolio/recent`),
        fetch(`${API_BASE_URL}/portfolio/leases`),
        fetch(`${API_BASE_URL}/portfolio/market-summary`),
        fetch(`${API_BASE_URL}/portfolio/location-summary`)
      ]);

      if (kpiResponse.ok) setKpis(await kpiResponse.json());
      if (recentResponse.ok) setRecentExtractions(await recentResponse.json());
      if (leasesResponse.ok) setAllLeases(await leasesResponse.json());
      if (marketResponse.ok) setMarketSummary(await marketResponse.json());
      if (locationResponse.ok) setLocationData(await locationResponse.json());

      setLoading(false);
    } catch (err) {
      setError('Failed to connect to backend API. Make sure the Flask server is running on port 5001.');
      setLoading(false);
      console.error('Error fetching data:', err);
    }
  };

  const metrics = kpis ? [
    { label: 'Total Leases', value: kpis.total_leases.toLocaleString(), change: `${kpis.expiring_12_months} expiring in 12mo` },
    { label: 'Avg. Rent PSF', value: `$${kpis.avg_rent_psf.toFixed(2)}`, change: `${kpis.total_properties} properties` },
    { label: 'Portfolio WALT', value: `${kpis.portfolio_walt.toFixed(1)} yrs`, change: `${kpis.markets_count} markets` },
    { label: 'Avg. Risk Score', value: kpis.avg_risk_score.toFixed(1), change: `${kpis.total_tenants} tenants` },
  ] : [
    { label: 'Total Leases', value: '-', change: 'Loading...' },
    { label: 'Avg. Rent PSF', value: '-', change: 'Loading...' },
    { label: 'Portfolio WALT', value: '-', change: 'Loading...' },
    { label: 'Avg. Risk Score', value: '-', change: 'Loading...' },
  ];

  if (loading) {
    return (
      <div className="portfolio">
        <div className="portfolio-container">
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Loading portfolio data...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="portfolio">
        <div className="portfolio-container">
          <div className="error-container">
            <h2>⚠️ Connection Error</h2>
            <p>{error}</p>
            <p className="error-hint">
              To start the backend server:<br/>
              <code>cd backend && pip install -r requirements.txt && python api.py</code>
            </p>
            <button className="retry-button" onClick={fetchPortfolioData}>
              <FiRefreshCw size={20} />
              Retry Connection
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="portfolio">
      <div className="portfolio-container">
        <motion.div 
          className="portfolio-header"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div>
            <h1 className="portfolio-title">Lease Portfolio Analytics</h1>
            <p className="portfolio-subtitle">Real-time insights from Databricks Unity Catalog</p>
          </div>
          <button className="refresh-button" onClick={fetchPortfolioData}>
            <FiRefreshCw size={20} />
            Refresh Data
          </button>
        </motion.div>

        <div className="metrics-grid">
          {metrics.map((metric, index) => (
            <motion.div 
              key={index}
              className="metric-card"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <div className="metric-label">{metric.label}</div>
              <div className="metric-value">{metric.value}</div>
              <div className="metric-change">{metric.change}</div>
            </motion.div>
          ))}
        </div>

        <div className="tab-navigation">
          <button 
            className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </button>
          <button 
            className={`tab-button ${activeTab === 'map' ? 'active' : ''}`}
            onClick={() => setActiveTab('map')}
          >
            Map View
          </button>
          <button 
            className={`tab-button ${activeTab === 'leases' ? 'active' : ''}`}
            onClick={() => setActiveTab('leases')}
          >
            All Leases ({allLeases.length})
          </button>
          <button 
            className={`tab-button ${activeTab === 'markets' ? 'active' : ''}`}
            onClick={() => setActiveTab('markets')}
          >
            Market Summary
          </button>
        </div>

        {activeTab === 'overview' && (
          <motion.div 
            className="recent-section"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="section-title">Recent Extractions</h2>
            <div className="extractions-list">
              {recentExtractions.slice(0, 5).map((extraction) => (
                <div key={extraction.id} className="extraction-item">
                  <div className="extraction-icon">📋</div>
                  <div className="extraction-info">
                    <div className="extraction-name">{extraction.name}</div>
                    <div className="extraction-meta">
                      <span className={`status ${extraction.status.toLowerCase()}`}>
                        {extraction.status}
                      </span>
                      <span className="accuracy">{extraction.accuracy}</span>
                      <span className="date">{String(extraction.date).substring(0, 10)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {activeTab === 'map' && (
          <motion.div 
            className="map-section"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <LeaseMap locations={locationData} />
          </motion.div>
        )}

        {activeTab === 'leases' && (
          <motion.div 
            className="leases-section"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="section-title">All Lease Details</h2>
            <div className="table-container">
              <table className="leases-table">
                <thead>
                  <tr>
                    <th>Tenant</th>
                    <th>Property</th>
                    <th>Market</th>
                    <th>Commencement</th>
                    <th>Expiration</th>
                    <th>Rent PSF</th>
                    <th>Square Feet</th>
                    <th>Years Left</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {allLeases.map((lease) => (
                    <tr key={lease.id}>
                      <td>{lease.tenant_name}</td>
                      <td>{lease.property_name}</td>
                      <td>{lease.market}</td>
                      <td>{lease.commencement_date}</td>
                      <td>{lease.expiration_date}</td>
                      <td>${lease.base_rent_psf.toFixed(2)}</td>
                      <td>{lease.square_feet.toLocaleString()}</td>
                      <td>{lease.years_remaining.toFixed(1)}</td>
                      <td>
                        <span className={`status ${lease.status.toLowerCase()}`}>
                          {lease.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>
        )}

        {activeTab === 'markets' && (
          <motion.div 
            className="markets-section"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="section-title">Market Summary</h2>
            <div className="market-grid">
              {marketSummary.map((market, index) => (
                <div key={index} className="market-card">
                  <h3 className="market-name">{market.market}</h3>
                  <div className="market-stats">
                    <div className="market-stat">
                      <span className="stat-label">Leases</span>
                      <span className="stat-value">{market.lease_count}</span>
                    </div>
                    <div className="market-stat">
                      <span className="stat-label">Avg Rent PSF</span>
                      <span className="stat-value">${market.avg_rent_psf}</span>
                    </div>
                    <div className="market-stat">
                      <span className="stat-label">WALT</span>
                      <span className="stat-value">{market.walt_years} yrs</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default Portfolio;

