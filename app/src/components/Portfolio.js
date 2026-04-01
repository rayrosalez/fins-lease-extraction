import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiRefreshCw, FiHome, FiUser, FiTrendingUp, FiAlertTriangle, FiDollarSign, FiActivity, FiBookOpen, FiX, FiFileText, FiThumbsUp, FiMinus, FiThumbsDown, FiChevronUp, FiChevronDown, FiMapPin, FiBarChart2 } from 'react-icons/fi';
import LeaseMap from './LeaseMap';
import RiskAssessment from './RiskAssessment';
import './Portfolio.css';

const API_BASE_URL = '/api';

const Portfolio = () => {
  const [kpis, setKpis] = useState(null);
  const [, setRecentExtractions] = useState([]);
  const [allLeases, setAllLeases] = useState([]);
  const [marketSummary, setMarketSummary] = useState([]);
  const [locationData, setLocationData] = useState([]);
  const [landlords, setLandlords] = useState([]);
  const [tenants, setTenants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('leases');
  const [glossaryOpen, setGlossaryOpen] = useState(false);
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
  const [landlordSortConfig, setLandlordSortConfig] = useState({ key: null, direction: 'asc' });
  const [tenantSortConfig, setTenantSortConfig] = useState({ key: null, direction: 'asc' });

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

  const handleSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const getSortedLeases = () => {
    if (!sortConfig.key) return allLeases;

    const sortedLeases = [...allLeases].sort((a, b) => {
      let aValue = a[sortConfig.key];
      let bValue = b[sortConfig.key];

      // Handle date sorting for uploaded_at
      if (sortConfig.key === 'uploaded_at') {
        aValue = aValue ? new Date(aValue).getTime() : 0;
        bValue = bValue ? new Date(bValue).getTime() : 0;
      }

      // Handle string sorting
      if (typeof aValue === 'string') {
        aValue = aValue.toLowerCase();
        bValue = bValue.toLowerCase();
      }

      // Handle null/undefined values
      if (aValue === null || aValue === undefined) return 1;
      if (bValue === null || bValue === undefined) return -1;

      if (aValue < bValue) {
        return sortConfig.direction === 'asc' ? -1 : 1;
      }
      if (aValue > bValue) {
        return sortConfig.direction === 'asc' ? 1 : -1;
      }
      return 0;
    });

    return sortedLeases;
  };

  const renderSortIcon = (columnKey) => {
    if (sortConfig.key !== columnKey) {
      return <span className="sort-icon sort-icon-inactive">⇅</span>;
    }
    return sortConfig.direction === 'asc' ? (
      <FiChevronUp className="sort-icon sort-icon-active" size={16} />
    ) : (
      <FiChevronDown className="sort-icon sort-icon-active" size={16} />
    );
  };

  const handleLandlordSort = (key) => {
    let direction = 'asc';
    if (landlordSortConfig.key === key && landlordSortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setLandlordSortConfig({ key, direction });
  };

  const getSortedLandlords = () => {
    if (!landlordSortConfig.key) return landlords;

    const sortedLandlords = [...landlords].sort((a, b) => {
      let aValue = a[landlordSortConfig.key];
      let bValue = b[landlordSortConfig.key];

      // Handle date sorting for created_at
      if (landlordSortConfig.key === 'created_at') {
        aValue = aValue ? new Date(aValue).getTime() : 0;
        bValue = bValue ? new Date(bValue).getTime() : 0;
      }

      // Handle string sorting
      if (typeof aValue === 'string') {
        aValue = aValue.toLowerCase();
        bValue = bValue.toLowerCase();
      }

      // Handle null/undefined values
      if (aValue === null || aValue === undefined) return 1;
      if (bValue === null || bValue === undefined) return -1;

      if (aValue < bValue) {
        return landlordSortConfig.direction === 'asc' ? -1 : 1;
      }
      if (aValue > bValue) {
        return landlordSortConfig.direction === 'asc' ? 1 : -1;
      }
      return 0;
    });

    return sortedLandlords;
  };

  const renderLandlordSortIcon = (columnKey) => {
    if (landlordSortConfig.key !== columnKey) {
      return <span className="sort-icon sort-icon-inactive">⇅</span>;
    }
    return landlordSortConfig.direction === 'asc' ? (
      <FiChevronUp className="sort-icon sort-icon-active" size={16} />
    ) : (
      <FiChevronDown className="sort-icon sort-icon-active" size={16} />
    );
  };

  const handleTenantSort = (key) => {
    let direction = 'asc';
    if (tenantSortConfig.key === key && tenantSortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setTenantSortConfig({ key, direction });
  };

  const getSortedTenants = () => {
    if (!tenantSortConfig.key) return tenants;

    const sortedTenants = [...tenants].sort((a, b) => {
      let aValue = a[tenantSortConfig.key];
      let bValue = b[tenantSortConfig.key];

      // Handle date sorting for created_at
      if (tenantSortConfig.key === 'created_at') {
        aValue = aValue ? new Date(aValue).getTime() : 0;
        bValue = bValue ? new Date(bValue).getTime() : 0;
      }

      // Handle string sorting
      if (typeof aValue === 'string') {
        aValue = aValue.toLowerCase();
        bValue = bValue.toLowerCase();
      }

      // Handle null/undefined values
      if (aValue === null || aValue === undefined) return 1;
      if (bValue === null || bValue === undefined) return -1;

      if (aValue < bValue) {
        return tenantSortConfig.direction === 'asc' ? -1 : 1;
      }
      if (aValue > bValue) {
        return tenantSortConfig.direction === 'asc' ? 1 : -1;
      }
      return 0;
    });

    return sortedTenants;
  };

  const renderTenantSortIcon = (columnKey) => {
    if (tenantSortConfig.key !== columnKey) {
      return <span className="sort-icon sort-icon-inactive">⇅</span>;
    }
    return tenantSortConfig.direction === 'asc' ? (
      <FiChevronUp className="sort-icon sort-icon-active" size={16} />
    ) : (
      <FiChevronDown className="sort-icon sort-icon-active" size={16} />
    );
  };

  const metrics = kpis ? [
    { label: 'Total Leases', value: kpis.total_leases.toLocaleString(), icon: FiFileText, subtext: `${kpis.expiring_12_months} expiring soon` },
    { 
      label: 'Landlords', 
      value: landlords.length.toLocaleString(), 
      icon: FiHome, 
      subtext: landlords.length > 0 
        ? `${(landlords.reduce((sum, l) => sum + (l.financial_health_score || 0), 0) / landlords.length).toFixed(1)} avg health`
        : 'No data'
    },
    { 
      label: 'Tenants', 
      value: tenants.length.toLocaleString(), 
      icon: FiUser, 
      subtext: tenants.length > 0 
        ? `${(tenants.reduce((sum, t) => sum + (t.financial_health_score || 0), 0) / tenants.length).toFixed(1)} avg health`
        : 'No data'
    },
    { label: 'Avg. Rent PSF', value: `$${kpis.avg_rent_psf.toFixed(2)}`, icon: FiDollarSign, subtext: `${kpis.total_properties} properties` },
    { label: 'Portfolio WALT', value: `${kpis.portfolio_walt.toFixed(1)} yrs`, icon: FiActivity, subtext: `${kpis.markets_count} markets` },
    { label: 'Avg. Risk Score', value: `${kpis.avg_risk_score.toFixed(1)}/100`, icon: FiAlertTriangle, subtext: `${kpis.total_tenants} tenants` },
  ] : [
    { label: 'Total Leases', value: '-', icon: FiFileText, subtext: 'Loading...' },
    { label: 'Landlords', value: '-', icon: FiHome, subtext: 'Loading...' },
    { label: 'Tenants', value: '-', icon: FiUser, subtext: 'Loading...' },
    { label: 'Avg. Rent PSF', value: '-', icon: FiDollarSign, subtext: 'Loading...' },
    { label: 'Portfolio WALT', value: '-', icon: FiActivity, subtext: 'Loading...' },
    { label: 'Avg. Risk Score', value: '-', icon: FiAlertTriangle, subtext: 'Loading...' },
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
            <h2>[!] Connection Error</h2>
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

            <motion.div 
          className="kpi-strip"
          initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {metrics.map((metric, index) => {
            const IconComponent = metric.icon;
            // Determine icon type for styling
            let iconType = 'default';
            if (metric.label === 'Landlords') iconType = 'landlord';
            else if (metric.label === 'Tenants') iconType = 'tenant';
            
            return (
              <React.Fragment key={index}>
                <div className="kpi-item">
                  <div className={`kpi-icon kpi-icon-${iconType}`}>
                    <IconComponent size={20} />
        </div>
                  <div className="kpi-content">
                    <div className="kpi-label">{metric.label}</div>
                    <div className="kpi-value">{metric.value}</div>
                    <div className="kpi-subtext">{metric.subtext}</div>
                  </div>
                </div>
                {index < metrics.length - 1 && <div className="kpi-divider"></div>}
              </React.Fragment>
            );
          })}
        </motion.div>

        <div className="tab-navigation">
          <button 
            className={`tab-button ${activeTab === 'leases' ? 'active' : ''}`}
            onClick={() => setActiveTab('leases')}
          >
            <FiFileText size={16} style={{ marginRight: '0.5rem' }} />
            All Leases
          </button>
          <button 
            className={`tab-button ${activeTab === 'markets' ? 'active' : ''}`}
            onClick={() => setActiveTab('markets')}
          >
            <FiBarChart2 size={16} style={{ marginRight: '0.5rem' }} />
            Market Summary
          </button>
          <button 
            className={`tab-button ${activeTab === 'map' ? 'active' : ''}`}
            onClick={() => setActiveTab('map')}
          >
            <FiMapPin size={16} style={{ marginRight: '0.5rem' }} />
            Map View
          </button>
          <button 
            className={`tab-button ${activeTab === 'landlords' ? 'active' : ''}`}
            onClick={() => setActiveTab('landlords')}
          >
            <FiHome size={16} style={{ marginRight: '0.5rem' }} />
            Landlords
          </button>
          <button 
            className={`tab-button ${activeTab === 'tenants' ? 'active' : ''}`}
            onClick={() => setActiveTab('tenants')}
          >
            <FiUser size={16} style={{ marginRight: '0.5rem' }} />
            Tenants
          </button>
          <button 
            className={`tab-button tab-button-risk ${activeTab === 'risk' ? 'active' : ''}`}
            onClick={() => setActiveTab('risk')}
          >
            <FiAlertTriangle size={16} style={{ marginRight: '0.5rem' }} />
            Risk Assessment
          </button>
        </div>

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
                    <th className="sortable-header" onClick={() => handleSort('uploaded_at')}>
                      <div className="header-content">
                        Uploaded
                        {renderSortIcon('uploaded_at')}
                </div>
                    </th>
                    <th className="sortable-header" onClick={() => handleSort('tenant_name')}>
                      <div className="header-content">
                        Tenant
                        {renderSortIcon('tenant_name')}
                </div>
                    </th>
                    <th className="sortable-header" onClick={() => handleSort('property_name')}>
                      <div className="header-content">
                        Property
                        {renderSortIcon('property_name')}
              </div>
                    </th>
                    <th className="sortable-header" onClick={() => handleSort('market')}>
                      <div className="header-content">
                        Market
                        {renderSortIcon('market')}
                </div>
                    </th>
                    <th className="sortable-header" onClick={() => handleSort('commencement_date')}>
                      <div className="header-content">
                        Commencement
                        {renderSortIcon('commencement_date')}
                </div>
                    </th>
                    <th className="sortable-header" onClick={() => handleSort('expiration_date')}>
                      <div className="header-content">
                        Expiration
                        {renderSortIcon('expiration_date')}
              </div>
                    </th>
                    <th className="sortable-header" onClick={() => handleSort('base_rent_psf')}>
                      <div className="header-content">
                        Rent PSF
                        {renderSortIcon('base_rent_psf')}
                </div>
                    </th>
                    <th className="sortable-header" onClick={() => handleSort('square_feet')}>
                      <div className="header-content">
                        Square Feet
                        {renderSortIcon('square_feet')}
                  </div>
                    </th>
                    <th className="sortable-header" onClick={() => handleSort('years_remaining')}>
                      <div className="header-content">
                        Years Left
                        {renderSortIcon('years_remaining')}
                </div>
                    </th>
                    <th className="sortable-header" onClick={() => handleSort('status')}>
                      <div className="header-content">
                        Status
                        {renderSortIcon('status')}
              </div>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {getSortedLeases().map((lease) => (
                    <tr key={lease.id}>
                      <td className="uploaded-cell">
                        {lease.uploaded_at ? (
                          <div className="uploaded-date">
                            <div>{new Date(lease.uploaded_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</div>
                            <div className="uploaded-time">{new Date(lease.uploaded_at).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</div>
                          </div>
                        ) : (
                          <span className="no-date">-</span>
                        )}
                      </td>
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
            <p className="section-description">
              Financial profiles of property owners and REITs with credit ratings, portfolio statistics, and market data enriched through MCP web search.
            </p>
            
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
                    const IconComponent = sentiment === 'POSITIVE' ? FiThumbsUp : sentiment === 'NEUTRAL' ? FiMinus : FiThumbsDown;
                    return (
                      <div key={sentiment} className={`sentiment-item sentiment-${sentiment.toLowerCase()}`}>
                        <span className="sentiment-icon">
                          <IconComponent size={24} />
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
                    <th className="sortable-header" onClick={() => handleLandlordSort('created_at')}>
                      <div className="header-content">
                        Uploaded
                        {renderLandlordSortIcon('created_at')}
                      </div>
                    </th>
                    <th className="sortable-header" onClick={() => handleLandlordSort('landlord_name')}>
                      <div className="header-content">
                        Name
                        {renderLandlordSortIcon('landlord_name')}
                      </div>
                    </th>
                    <th className="sortable-header" onClick={() => handleLandlordSort('company_type')}>
                      <div className="header-content">
                        Type
                        {renderLandlordSortIcon('company_type')}
                      </div>
                    </th>
                    <th className="sortable-header" onClick={() => handleLandlordSort('stock_ticker')}>
                      <div className="header-content">
                        Ticker
                        {renderLandlordSortIcon('stock_ticker')}
                      </div>
                    </th>
                    <th className="sortable-header" onClick={() => handleLandlordSort('market_cap')}>
                      <div className="header-content">
                        Market Cap
                        {renderLandlordSortIcon('market_cap')}
                      </div>
                    </th>
                    <th className="sortable-header" onClick={() => handleLandlordSort('annual_revenue')}>
                      <div className="header-content">
                        Annual Revenue
                        {renderLandlordSortIcon('annual_revenue')}
                      </div>
                    </th>
                    <th className="sortable-header" onClick={() => handleLandlordSort('credit_rating')}>
                      <div className="header-content">
                        Credit Rating
                        {renderLandlordSortIcon('credit_rating')}
                      </div>
                    </th>
                    <th className="sortable-header" onClick={() => handleLandlordSort('total_properties')}>
                      <div className="header-content">
                        Properties
                        {renderLandlordSortIcon('total_properties')}
                      </div>
                    </th>
                    <th className="sortable-header" onClick={() => handleLandlordSort('financial_health_score')}>
                      <div className="header-content">
                        Health Score
                        {renderLandlordSortIcon('financial_health_score')}
                      </div>
                    </th>
                    <th className="sortable-header" onClick={() => handleLandlordSort('bankruptcy_risk')}>
                      <div className="header-content">
                        Risk
                        {renderLandlordSortIcon('bankruptcy_risk')}
                      </div>
                    </th>
                    <th className="sortable-header" onClick={() => handleLandlordSort('recent_news_sentiment')}>
                      <div className="header-content">
                        Sentiment
                        {renderLandlordSortIcon('recent_news_sentiment')}
                      </div>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {getSortedLandlords().map((landlord) => (
                    <tr key={landlord.landlord_id}>
                      <td className="uploaded-cell">
                        {landlord.created_at ? (
                          <div className="uploaded-date">
                            <div>{new Date(landlord.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</div>
                            <div className="uploaded-time">{new Date(landlord.created_at).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</div>
                          </div>
                        ) : (
                          <span className="no-date">-</span>
                        )}
                      </td>
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
            <p className="section-description">
              Financial profiles of tenant companies including health scores, credit ratings, bankruptcy risk assessment, and operational metrics enriched through MCP web search.
            </p>
            
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
                    <th className="sortable-header" onClick={() => handleTenantSort('created_at')}>
                      <div className="header-content">
                        Uploaded
                        {renderTenantSortIcon('created_at')}
                      </div>
                    </th>
                    <th className="sortable-header" onClick={() => handleTenantSort('tenant_name')}>
                      <div className="header-content">
                        Name
                        {renderTenantSortIcon('tenant_name')}
                      </div>
                    </th>
                    <th className="sortable-header" onClick={() => handleTenantSort('industry_sector')}>
                      <div className="header-content">
                        Industry
                        {renderTenantSortIcon('industry_sector')}
                      </div>
                    </th>
                    <th className="sortable-header" onClick={() => handleTenantSort('company_type')}>
                      <div className="header-content">
                        Type
                        {renderTenantSortIcon('company_type')}
                      </div>
                    </th>
                    <th className="sortable-header" onClick={() => handleTenantSort('stock_ticker')}>
                      <div className="header-content">
                        Ticker
                        {renderTenantSortIcon('stock_ticker')}
                      </div>
                    </th>
                    <th className="sortable-header" onClick={() => handleTenantSort('annual_revenue')}>
                      <div className="header-content">
                        Annual Revenue
                        {renderTenantSortIcon('annual_revenue')}
                      </div>
                    </th>
                    <th className="sortable-header" onClick={() => handleTenantSort('employee_count')}>
                      <div className="header-content">
                        Employees
                        {renderTenantSortIcon('employee_count')}
                      </div>
                    </th>
                    <th className="sortable-header" onClick={() => handleTenantSort('credit_rating')}>
                      <div className="header-content">
                        Credit Rating
                        {renderTenantSortIcon('credit_rating')}
                      </div>
                    </th>
                    <th className="sortable-header" onClick={() => handleTenantSort('financial_health_score')}>
                      <div className="header-content">
                        Health Score
                        {renderTenantSortIcon('financial_health_score')}
                      </div>
                    </th>
                    <th className="sortable-header" onClick={() => handleTenantSort('bankruptcy_risk')}>
                      <div className="header-content">
                        Risk
                        {renderTenantSortIcon('bankruptcy_risk')}
                      </div>
                    </th>
                    <th className="sortable-header" onClick={() => handleTenantSort('revenue_growth_pct')}>
                      <div className="header-content">
                        Growth
                        {renderTenantSortIcon('revenue_growth_pct')}
                      </div>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {getSortedTenants().map((tenant) => (
                    <tr key={tenant.tenant_id}>
                      <td className="uploaded-cell">
                        {tenant.created_at ? (
                          <div className="uploaded-date">
                            <div>{new Date(tenant.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</div>
                            <div className="uploaded-time">{new Date(tenant.created_at).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</div>
                          </div>
                        ) : (
                          <span className="no-date">-</span>
                        )}
                      </td>
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
      </div>

      {/* Floating Glossary Button */}
      <button 
        className="floating-glossary-button" 
        onClick={() => setGlossaryOpen(!glossaryOpen)}
        title="Reference Guide"
      >
        <FiBookOpen size={24} />
      </button>

      {/* Glossary Modal Popup */}
      <AnimatePresence>
        {glossaryOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              className="glossary-modal-backdrop"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setGlossaryOpen(false)}
            />
            
            {/* Modal Container for Centering */}
            <div className="glossary-modal-container">
              <motion.div
                className="glossary-modal"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ type: 'spring', damping: 25, stiffness: 300 }}
              >
              <div className="glossary-modal-header">
                <h2 className="glossary-modal-title">
                  <FiBookOpen size={28} />
                  Reference Guide
                </h2>
                <button className="glossary-modal-close" onClick={() => setGlossaryOpen(false)}>
                  <FiX size={28} />
                </button>
              </div>

              <div className="glossary-modal-content">
                <div className="glossary-card-vertical">
                  <div className="glossary-term">PSF</div>
                  <div className="glossary-full-term">Price Per Square Foot</div>
                  <div className="glossary-definition">
                    A standard commercial real estate metric that represents the annual rental cost 
                    divided by the total rentable square footage of a space. PSF allows for easy 
                    comparison of rental rates across properties of different sizes.
                  </div>
                  <div className="glossary-formula">
                    <span className="formula-label">Formula:</span>
                    <code>PSF = Annual Base Rent ÷ Rentable Square Feet</code>
                  </div>
                </div>

                <div className="glossary-card-vertical">
                  <div className="glossary-term">WALT</div>
                  <div className="glossary-full-term">Weighted Average Lease Term</div>
                  <div className="glossary-definition">
                    A key portfolio metric that calculates the average remaining lease duration, 
                    weighted by each lease's contribution to total rental income or square footage. 
                    WALT helps investors understand the stability of cash flows and the timeline 
                    for potential vacancy risk.
                  </div>
                  <div className="glossary-formula">
                    <span className="formula-label">Formula:</span>
                    <code>WALT = Σ(Remaining Term × Annual Rent) ÷ Total Annual Rent</code>
                  </div>
                </div>

                <div className="glossary-card-vertical">
                  <div className="glossary-term">Risk Score</div>
                  <div className="glossary-full-term">Tenant Credit & Lease Risk Assessment</div>
                  <div className="glossary-definition">
                    A composite score (typically 1-10) that evaluates the overall risk profile of 
                    a lease or tenant. Factors considered include tenant creditworthiness, 
                    industry stability, lease term remaining, and rental rate relative to market.
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

                <div className="glossary-card-vertical">
                  <div className="glossary-term">Enrichment</div>
                  <div className="glossary-full-term">Data Enrichment via MCP</div>
                  <div className="glossary-definition">
                    The process of augmenting basic lease data with external financial, credit, and 
                    operational information about tenants and landlords. This enrichment uses the 
                    Model Context Protocol (MCP) to fetch real-time web data including financial statements, 
                    credit ratings, market cap, bankruptcy risk, and news sentiment.
                  </div>
                  <div className="glossary-factors">
                    <span className="factors-label">Enriched Data Types:</span>
                    <ul>
                      <li>Financial health scores & credit ratings</li>
                      <li>Market capitalization & stock performance</li>
                      <li>Bankruptcy risk assessment</li>
                      <li>Recent news sentiment analysis</li>
                    </ul>
                  </div>
                </div>

                <div className="glossary-card-vertical">
                  <div className="glossary-term">Financial Health Score</div>
                  <div className="glossary-full-term">Tenant/Landlord Financial Health Score</div>
                  <div className="glossary-definition">
                    A normalized score (0-10) that represents the overall financial strength and 
                    stability of a tenant or landlord entity. This score is derived from multiple 
                    financial metrics including revenue, profit margin, debt-to-equity ratio, cash 
                    reserves, and revenue growth trends.
                  </div>
                  <div className="glossary-formula">
                    <span className="formula-label">Components:</span>
                    <code>Health Score = f(Revenue, Profit Margin, Debt Ratio, Cash Position, Growth)</code>
                  </div>
                </div>

                <div className="glossary-card-vertical">
                  <div className="glossary-term">Adaptive Risk Models</div>
                  <div className="glossary-full-term">Dynamic Risk Scoring Framework</div>
                  <div className="glossary-definition">
                    A flexible risk assessment system that automatically adjusts scoring methodology 
                    based on available enrichment data. Four models are used: FULLY_ENRICHED (both 
                    tenant and landlord data), TENANT_ENRICHED (only tenant data), LANDLORD_ENRICHED 
                    (only landlord data), and BASIC (no enrichment).
                  </div>
                  <div className="glossary-factors">
                    <span className="factors-label">Model Types:</span>
                    <ul>
                      <li>FULLY_ENRICHED - Both tenant & landlord data</li>
                      <li>TENANT_ENRICHED - Only tenant financial data</li>
                      <li>LANDLORD_ENRICHED - Only landlord financial data</li>
                      <li>BASIC - Lease-specific factors only</li>
                    </ul>
                  </div>
                </div>

                <div className="glossary-card-vertical">
                  <div className="glossary-term">MCP</div>
                  <div className="glossary-full-term">Model Context Protocol</div>
                  <div className="glossary-definition">
                    An open protocol that enables AI systems to securely connect with external data 
                    sources and tools. In this application, MCP is used to fetch real-time financial, 
                    operational, and market data about tenants and landlords from web sources. This 
                    allows the system to enrich lease records with current information beyond what's 
                    available in the original lease documents.
                  </div>
                </div>
              </div>
            </motion.div>
            </div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Portfolio;

