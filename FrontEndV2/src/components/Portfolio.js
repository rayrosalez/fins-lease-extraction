import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FiRefreshCw, FiHome, FiUser, FiTrendingUp, FiAlertTriangle, FiDollarSign, FiActivity } from 'react-icons/fi';
import LeaseMap from './LeaseMap';
import RiskAssessment from './RiskAssessment';
import './Portfolio.css';

const API_BASE_URL = 'http://localhost:5001/api';

const Portfolio = () => {
  const [kpis, setKpis] = useState(null);
  const [recentExtractions, setRecentExtractions] = useState([]);
  const [allLeases, setAllLeases] = useState([]);
  const [marketSummary, setMarketSummary] = useState([]);
  const [locationData, setLocationData] = useState([]);
  const [landlords, setLandlords] = useState([]);
  const [tenants, setTenants] = useState([]);
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

      const [kpiResponse, recentResponse, leasesResponse, marketResponse, locationResponse, landlordsResponse, tenantsResponse] = await Promise.all([
        fetch(`${API_BASE_URL}/portfolio/kpis`),
        fetch(`${API_BASE_URL}/portfolio/recent`),
        fetch(`${API_BASE_URL}/portfolio/leases`),
        fetch(`${API_BASE_URL}/portfolio/market-summary`),
        fetch(`${API_BASE_URL}/portfolio/location-summary`),
        fetch(`${API_BASE_URL}/portfolio/landlords`),
        fetch(`${API_BASE_URL}/portfolio/tenants`)
      ]);

      if (kpiResponse.ok) setKpis(await kpiResponse.json());
      if (recentResponse.ok) setRecentExtractions(await recentResponse.json());
      if (leasesResponse.ok) setAllLeases(await leasesResponse.json());
      if (marketResponse.ok) setMarketSummary(await marketResponse.json());
      if (locationResponse.ok) setLocationData(await locationResponse.json());
      if (landlordsResponse.ok) setLandlords(await landlordsResponse.json());
      if (tenantsResponse.ok) setTenants(await tenantsResponse.json());

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
    { label: 'Avg. Risk Score', value: `${kpis.avg_risk_score.toFixed(1)}/100`, change: `${kpis.total_tenants} tenants` },
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
            className={`tab-button ${activeTab === 'risk' ? 'active' : ''}`}
            onClick={() => setActiveTab('risk')}
          >
            Risk Assessment
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
          <button 
            className={`tab-button ${activeTab === 'landlords' ? 'active' : ''}`}
            onClick={() => setActiveTab('landlords')}
          >
            <FiHome size={16} style={{ marginRight: '0.5rem' }} />
            Landlords ({landlords.length})
          </button>
          <button 
            className={`tab-button ${activeTab === 'tenants' ? 'active' : ''}`}
            onClick={() => setActiveTab('tenants')}
          >
            <FiUser size={16} style={{ marginRight: '0.5rem' }} />
            Tenants ({tenants.length})
          </button>
          <button 
            className={`tab-button ${activeTab === 'glossary' ? 'active' : ''}`}
            onClick={() => setActiveTab('glossary')}
          >
            Glossary
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

        {activeTab === 'risk' && (
          <motion.div 
            className="risk-section"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <RiskAssessment />
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

        {activeTab === 'landlords' && (
          <motion.div 
            className="landlords-section"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="section-title">Landlord Profiles</h2>
            
            {/* Landlord Aggregate Metrics */}
            <div className="entity-metrics-grid">
              <div className="entity-metric-card">
                <div className="entity-metric-icon landlord-icon">
                  <FiHome size={24} />
                </div>
                <div className="entity-metric-content">
                  <div className="entity-metric-value">{landlords.length}</div>
                  <div className="entity-metric-label">Total Landlords</div>
                </div>
              </div>
              
              <div className="entity-metric-card">
                <div className="entity-metric-icon revenue-icon">
                  <FiDollarSign size={24} />
                </div>
                <div className="entity-metric-content">
                  <div className="entity-metric-value">
                    ${(landlords.reduce((sum, l) => sum + (l.annual_revenue || 0), 0) / 1e9).toFixed(1)}B
                  </div>
                  <div className="entity-metric-label">Total Revenue</div>
                </div>
              </div>
              
              <div className="entity-metric-card">
                <div className="entity-metric-icon health-icon">
                  <FiActivity size={24} />
                </div>
                <div className="entity-metric-content">
                  <div className="entity-metric-value">
                    {landlords.length > 0 
                      ? (landlords.reduce((sum, l) => sum + (l.financial_health_score || 0), 0) / landlords.length).toFixed(1)
                      : '-'}
                  </div>
                  <div className="entity-metric-label">Avg Health Score</div>
                </div>
              </div>
              
              <div className="entity-metric-card">
                <div className="entity-metric-icon risk-icon">
                  <FiAlertTriangle size={24} />
                </div>
                <div className="entity-metric-content">
                  <div className="entity-metric-value">
                    {landlords.filter(l => l.bankruptcy_risk === 'LOW').length}
                  </div>
                  <div className="entity-metric-label">Low Risk</div>
                </div>
              </div>
            </div>

            {/* Risk Distribution Chart */}
            <div className="entity-charts-grid">
              <div className="entity-chart-card">
                <h3 className="chart-title">Risk Distribution</h3>
                <div className="risk-distribution">
                  {['LOW', 'MEDIUM', 'HIGH'].map(risk => {
                    const count = landlords.filter(l => l.bankruptcy_risk === risk).length;
                    const pct = landlords.length > 0 ? (count / landlords.length * 100) : 0;
                    return (
                      <div key={risk} className="risk-bar-row">
                        <span className="risk-label">{risk}</span>
                        <div className="risk-bar-container">
                          <div 
                            className={`risk-bar risk-${risk.toLowerCase()}`}
                            style={{ width: `${pct}%` }}
                          ></div>
                        </div>
                        <span className="risk-count">{count}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
              
              <div className="entity-chart-card">
                <h3 className="chart-title">Company Types</h3>
                <div className="company-type-grid">
                  {Object.entries(
                    landlords.reduce((acc, l) => {
                      const type = l.company_type || 'Unknown';
                      acc[type] = (acc[type] || 0) + 1;
                      return acc;
                    }, {})
                  ).map(([type, count]) => (
                    <div key={type} className="company-type-item">
                      <span className="type-name">{type}</span>
                      <span className="type-count">{count}</span>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="entity-chart-card">
                <h3 className="chart-title">News Sentiment</h3>
                <div className="sentiment-grid">
                  {['POSITIVE', 'NEUTRAL', 'NEGATIVE'].map(sentiment => {
                    const count = landlords.filter(l => l.recent_news_sentiment === sentiment).length;
                    return (
                      <div key={sentiment} className={`sentiment-item sentiment-${sentiment.toLowerCase()}`}>
                        <span className="sentiment-emoji">
                          {sentiment === 'POSITIVE' ? '😊' : sentiment === 'NEUTRAL' ? '😐' : '😟'}
                        </span>
                        <span className="sentiment-count">{count}</span>
                        <span className="sentiment-label">{sentiment}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Landlords Table */}
            <div className="table-container">
              <table className="entity-table landlord-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Type</th>
                    <th>Ticker</th>
                    <th>Market Cap</th>
                    <th>Annual Revenue</th>
                    <th>Credit Rating</th>
                    <th>Properties</th>
                    <th>Health Score</th>
                    <th>Risk</th>
                    <th>Sentiment</th>
                  </tr>
                </thead>
                <tbody>
                  {landlords.map((landlord) => (
                    <tr key={landlord.landlord_id}>
                      <td className="name-cell">{landlord.landlord_name}</td>
                      <td>{landlord.company_type || '-'}</td>
                      <td className="ticker-cell">{landlord.stock_ticker || '-'}</td>
                      <td>{landlord.market_cap ? `$${(landlord.market_cap / 1e9).toFixed(1)}B` : '-'}</td>
                      <td>{landlord.annual_revenue ? `$${(landlord.annual_revenue / 1e6).toFixed(0)}M` : '-'}</td>
                      <td>{landlord.credit_rating || '-'}</td>
                      <td>{landlord.total_properties || '-'}</td>
                      <td>
                        <div className="health-score-cell">
                          <div className="health-bar" style={{ width: `${(landlord.financial_health_score || 0) * 10}%` }}></div>
                          <span>{landlord.financial_health_score?.toFixed(1) || '-'}</span>
                        </div>
                      </td>
                      <td>
                        <span className={`risk-badge risk-${(landlord.bankruptcy_risk || 'unknown').toLowerCase()}`}>
                          {landlord.bankruptcy_risk || '-'}
                        </span>
                      </td>
                      <td>
                        <span className={`sentiment-badge sentiment-${(landlord.recent_news_sentiment || 'unknown').toLowerCase()}`}>
                          {landlord.recent_news_sentiment || '-'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {landlords.length === 0 && (
                <div className="empty-table-message">
                  <FiHome size={48} />
                  <p>No landlord profiles yet. Enrich lease records to populate this data.</p>
                </div>
              )}
            </div>
          </motion.div>
        )}

        {activeTab === 'tenants' && (
          <motion.div 
            className="tenants-section"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="section-title">Tenant Profiles</h2>
            
            {/* Tenant Aggregate Metrics */}
            <div className="entity-metrics-grid">
              <div className="entity-metric-card tenant-card">
                <div className="entity-metric-icon tenant-icon">
                  <FiUser size={24} />
                </div>
                <div className="entity-metric-content">
                  <div className="entity-metric-value">{tenants.length}</div>
                  <div className="entity-metric-label">Total Tenants</div>
                </div>
              </div>
              
              <div className="entity-metric-card tenant-card">
                <div className="entity-metric-icon revenue-icon">
                  <FiDollarSign size={24} />
                </div>
                <div className="entity-metric-content">
                  <div className="entity-metric-value">
                    ${(tenants.reduce((sum, t) => sum + (t.annual_revenue || 0), 0) / 1e9).toFixed(1)}B
                  </div>
                  <div className="entity-metric-label">Total Revenue</div>
                </div>
              </div>
              
              <div className="entity-metric-card tenant-card">
                <div className="entity-metric-icon health-icon">
                  <FiActivity size={24} />
                </div>
                <div className="entity-metric-content">
                  <div className="entity-metric-value">
                    {tenants.length > 0 
                      ? (tenants.reduce((sum, t) => sum + (t.financial_health_score || 0), 0) / tenants.length).toFixed(1)
                      : '-'}
                  </div>
                  <div className="entity-metric-label">Avg Health Score</div>
                </div>
              </div>
              
              <div className="entity-metric-card tenant-card">
                <div className="entity-metric-icon growth-icon">
                  <FiTrendingUp size={24} />
                </div>
                <div className="entity-metric-content">
                  <div className="entity-metric-value">
                    {tenants.filter(t => t.revenue_growth_pct > 0).length}
                  </div>
                  <div className="entity-metric-label">Growing Companies</div>
                </div>
              </div>
            </div>

            {/* Visualizations Grid */}
            <div className="entity-charts-grid">
              <div className="entity-chart-card">
                <h3 className="chart-title">Industry Sectors</h3>
                <div className="industry-grid">
                  {Object.entries(
                    tenants.reduce((acc, t) => {
                      const sector = t.industry_sector || 'Unknown';
                      acc[sector] = (acc[sector] || 0) + 1;
                      return acc;
                    }, {})
                  ).slice(0, 6).map(([sector, count]) => (
                    <div key={sector} className="industry-item">
                      <span className="industry-name">{sector}</span>
                      <span className="industry-count">{count}</span>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="entity-chart-card">
                <h3 className="chart-title">Risk Distribution</h3>
                <div className="risk-distribution">
                  {['LOW', 'MEDIUM', 'HIGH'].map(risk => {
                    const count = tenants.filter(t => t.bankruptcy_risk === risk).length;
                    const pct = tenants.length > 0 ? (count / tenants.length * 100) : 0;
                    return (
                      <div key={risk} className="risk-bar-row">
                        <span className="risk-label">{risk}</span>
                        <div className="risk-bar-container">
                          <div 
                            className={`risk-bar risk-${risk.toLowerCase()}`}
                            style={{ width: `${pct}%` }}
                          ></div>
                        </div>
                        <span className="risk-count">{count}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
              
              <div className="entity-chart-card">
                <h3 className="chart-title">Company Size (Employees)</h3>
                <div className="size-distribution">
                  {[
                    { label: 'Small (<100)', filter: t => (t.employee_count || 0) < 100 },
                    { label: 'Medium (100-1K)', filter: t => (t.employee_count || 0) >= 100 && (t.employee_count || 0) < 1000 },
                    { label: 'Large (1K-10K)', filter: t => (t.employee_count || 0) >= 1000 && (t.employee_count || 0) < 10000 },
                    { label: 'Enterprise (10K+)', filter: t => (t.employee_count || 0) >= 10000 }
                  ].map(({ label, filter }) => {
                    const count = tenants.filter(filter).length;
                    return (
                      <div key={label} className="size-item">
                        <span className="size-label">{label}</span>
                        <span className="size-count">{count}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Tenants Table */}
            <div className="table-container">
              <table className="entity-table tenant-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Industry</th>
                    <th>Type</th>
                    <th>Ticker</th>
                    <th>Annual Revenue</th>
                    <th>Employees</th>
                    <th>Credit Rating</th>
                    <th>Health Score</th>
                    <th>Risk</th>
                    <th>Growth</th>
                  </tr>
                </thead>
                <tbody>
                  {tenants.map((tenant) => (
                    <tr key={tenant.tenant_id}>
                      <td className="name-cell">{tenant.tenant_name}</td>
                      <td>{tenant.industry_sector || '-'}</td>
                      <td>{tenant.company_type || '-'}</td>
                      <td className="ticker-cell">{tenant.stock_ticker || '-'}</td>
                      <td>{tenant.annual_revenue ? `$${(tenant.annual_revenue / 1e6).toFixed(0)}M` : '-'}</td>
                      <td>{tenant.employee_count?.toLocaleString() || '-'}</td>
                      <td>{tenant.credit_rating || '-'}</td>
                      <td>
                        <div className="health-score-cell">
                          <div className="health-bar tenant-health" style={{ width: `${(tenant.financial_health_score || 0) * 10}%` }}></div>
                          <span>{tenant.financial_health_score?.toFixed(1) || '-'}</span>
                        </div>
                      </td>
                      <td>
                        <span className={`risk-badge risk-${(tenant.bankruptcy_risk || 'unknown').toLowerCase()}`}>
                          {tenant.bankruptcy_risk || '-'}
                        </span>
                      </td>
                      <td>
                        <span className={`growth-badge ${(tenant.revenue_growth_pct || 0) > 0 ? 'positive' : 'negative'}`}>
                          {tenant.revenue_growth_pct ? `${tenant.revenue_growth_pct > 0 ? '+' : ''}${tenant.revenue_growth_pct.toFixed(1)}%` : '-'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {tenants.length === 0 && (
                <div className="empty-table-message">
                  <FiUser size={48} />
                  <p>No tenant profiles yet. Enrich lease records to populate this data.</p>
                </div>
              )}
            </div>
          </motion.div>
        )}

        {activeTab === 'glossary' && (
          <motion.div 
            className="glossary-section"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="section-title">Glossary of Terms</h2>
            <div className="glossary-grid">
              <div className="glossary-card">
                <div className="glossary-term">PSF</div>
                <div className="glossary-full-term">Price Per Square Foot</div>
                <div className="glossary-definition">
                  A standard commercial real estate metric that represents the annual rental cost 
                  divided by the total rentable square footage of a space. PSF allows for easy 
                  comparison of rental rates across properties of different sizes. For example, 
                  a lease with $50 PSF on a 10,000 sq ft space would have an annual rent of $500,000.
                </div>
                <div className="glossary-formula">
                  <span className="formula-label">Formula:</span>
                  <code>PSF = Annual Base Rent ÷ Rentable Square Feet</code>
                </div>
              </div>

              <div className="glossary-card">
                <div className="glossary-term">WALT</div>
                <div className="glossary-full-term">Weighted Average Lease Term</div>
                <div className="glossary-definition">
                  A key portfolio metric that calculates the average remaining lease duration, 
                  weighted by each lease's contribution to total rental income or square footage. 
                  WALT helps investors understand the stability of cash flows and the timeline 
                  for potential vacancy risk. A higher WALT generally indicates more stable, 
                  long-term income streams.
                </div>
                <div className="glossary-formula">
                  <span className="formula-label">Formula:</span>
                  <code>WALT = Σ(Remaining Term × Annual Rent) ÷ Total Annual Rent</code>
                </div>
              </div>

              <div className="glossary-card">
                <div className="glossary-term">Risk Score</div>
                <div className="glossary-full-term">Tenant Credit & Lease Risk Assessment</div>
                <div className="glossary-definition">
                  A composite score (typically 1-10) that evaluates the overall risk profile of 
                  a lease or tenant. Factors considered may include tenant creditworthiness, 
                  industry stability, lease term remaining, rental rate relative to market, 
                  and geographic concentration. Lower scores indicate lower risk, while higher 
                  scores suggest increased attention may be needed.
                </div>
                <div className="glossary-factors">
                  <span className="factors-label">Key Factors:</span>
                  <ul>
                    <li>Tenant credit rating & financial health</li>
                    <li>Industry sector volatility</li>
                    <li>Time until lease expiration</li>
                    <li>Market rent comparison</li>
                  </ul>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default Portfolio;

