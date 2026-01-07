import React, { useState, useEffect, useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend,
  BarChart, Bar, Cell, PieChart, Pie, Sector
} from 'recharts';
import './RiskAssessment.css';

const API_BASE_URL = '/api';

const RiskAssessment = () => {
  const [riskData, setRiskData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedView, setSelectedView] = useState('bubble');
  const [filterStatus, setFilterStatus] = useState('all');

  useEffect(() => {
    fetchRiskData();
  }, []);

  const fetchRiskData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('Fetching risk data from:', `${API_BASE_URL}/portfolio/risk-assessment`);
      const response = await fetch(`${API_BASE_URL}/portfolio/risk-assessment`);
      
      console.log('Response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('Risk data received:', data.length, 'leases');
        setRiskData(data);
      } else {
        const errorText = await response.text();
        console.error('Error response:', errorText);
        setError(`Failed to fetch risk data (${response.status}): ${errorText}`);
      }
      setLoading(false);
    } catch (err) {
      console.error('Error fetching risk data:', err);
      setError(`Failed to connect to backend API: ${err.message}`);
      setLoading(false);
    }
  };

  // Filter data based on status
  const filteredData = useMemo(() => {
    if (filterStatus === 'all') return riskData;
    return riskData.filter(lease => lease.lease_status === filterStatus);
  }, [riskData, filterStatus]);

  // Calculate summary statistics
  const stats = useMemo(() => {
    if (!riskData.length) return null;

    const criticalLeases = riskData.filter(l => l.lease_status === 'CRITICAL').length;
    const highPriority = riskData.filter(l => l.lease_status === 'HIGH_PRIORITY').length;
    const avgRisk = riskData.reduce((sum, l) => sum + l.total_risk_score, 0) / riskData.length;
    const totalAtRisk = riskData
      .filter(l => l.total_risk_score > 70)
      .reduce((sum, l) => sum + l.estimated_annual_rent, 0);

    return {
      criticalLeases,
      highPriority,
      avgRisk,
      totalAtRisk
    };
  }, [riskData]);

  // Prepare data for different visualizations
  const bubbleData = useMemo(() => {
    return filteredData.map(lease => ({
      x: lease.days_to_expiry,
      y: lease.total_risk_score,
      z: lease.estimated_annual_rent / 10000, // Scale for visibility
      tenant: lease.tenant_name,
      status: lease.lease_status,
      rent: lease.estimated_annual_rent,
      concentration: lease.portfolio_concentration_pct
    }));
  }, [filteredData]);

  // Risk category distribution
  const riskDistribution = useMemo(() => {
    const categories = {
      'Critical (80-100)': 0,
      'High (60-79)': 0,
      'Medium (40-59)': 0,
      'Low (20-39)': 0,
      'Minimal (0-19)': 0
    };

    filteredData.forEach(lease => {
      const score = lease.total_risk_score;
      if (score >= 80) categories['Critical (80-100)']++;
      else if (score >= 60) categories['High (60-79)']++;
      else if (score >= 40) categories['Medium (40-59)']++;
      else if (score >= 20) categories['Low (20-39)']++;
      else categories['Minimal (0-19)']++;
    });

    return Object.entries(categories).map(([name, value]) => ({
      name,
      value,
      percentage: (value / filteredData.length * 100).toFixed(1)
    }));
  }, [filteredData]);

  // Risk components radar data (average scores)
  const radarData = useMemo(() => {
    if (!filteredData.length) return [];

    const avgScores = {
      rollover: 0,
      escalation: 0,
      sector: 0,
      concentration: 0
    };

    filteredData.forEach(lease => {
      avgScores.rollover += lease.rollover_score;
      avgScores.escalation += lease.escalation_risk_score;
      avgScores.sector += lease.sector_risk_base;
      avgScores.concentration += lease.concentration_risk_score;
    });

    const count = filteredData.length;
    return [
      {
        risk: 'Rollover Risk',
        score: avgScores.rollover / count,
        fullMark: 100
      },
      {
        risk: 'Escalation Risk',
        score: avgScores.escalation / count,
        fullMark: 100
      },
      {
        risk: 'Industry Risk',
        score: avgScores.sector / count,
        fullMark: 100
      },
      {
        risk: 'Concentration Risk',
        score: avgScores.concentration / count,
        fullMark: 100
      }
    ];
  }, [filteredData]);

  // Top 10 risky leases
  const topRiskyLeases = useMemo(() => {
    return [...filteredData]
      .sort((a, b) => b.total_risk_score - a.total_risk_score)
      .slice(0, 10);
  }, [filteredData]);

  // Industry sector risk breakdown
  const sectorRiskData = useMemo(() => {
    const sectors = {};
    
    filteredData.forEach(lease => {
      const sector = lease.industry_sector || 'Unknown';
      if (!sectors[sector]) {
        sectors[sector] = {
          sector,
          avgRisk: 0,
          count: 0,
          totalRent: 0
        };
      }
      sectors[sector].avgRisk += lease.total_risk_score;
      sectors[sector].count++;
      sectors[sector].totalRent += lease.estimated_annual_rent;
    });

    return Object.values(sectors)
      .map(s => ({
        sector: s.sector,
        avgRisk: s.avgRisk / s.count,
        count: s.count,
        totalRent: s.totalRent
      }))
      .sort((a, b) => b.avgRisk - a.avgRisk);
  }, [filteredData]);

  // Color mapping for risk levels
  const getRiskColor = (score) => {
    if (score >= 80) return '#ef4444'; // Critical - red
    if (score >= 60) return '#f97316'; // High - orange
    if (score >= 40) return '#eab308'; // Medium - yellow
    if (score >= 20) return '#22c55e'; // Low - green
    return '#3b82f6'; // Minimal - blue
  };

  const getStatusColor = (status) => {
    const colors = {
      'CRITICAL': '#ef4444',
      'HIGH_PRIORITY': '#f97316',
      'NEEDS_ATTENTION': '#eab308',
      'MONITOR': '#22c55e',
      'STABLE': '#3b82f6',
      'EXPIRED_RECENT': '#dc2626',
      'EXPIRED_OLD': '#9ca3af'
    };
    return colors[status] || '#6b7280';
  };

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="custom-tooltip">
          <p className="tooltip-tenant"><strong>{data.tenant}</strong></p>
          <p className="tooltip-item">Risk Score: <strong>{data.y?.toFixed(1)}</strong></p>
          <p className="tooltip-item">Days to Expiry: <strong>{data.x}</strong></p>
          <p className="tooltip-item">Annual Rent: <strong>${data.rent?.toLocaleString()}</strong></p>
          <p className="tooltip-item">Status: <strong>{data.status}</strong></p>
          <p className="tooltip-item">Concentration: <strong>{data.concentration?.toFixed(2)}%</strong></p>
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <div className="risk-assessment">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading risk assessment data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="risk-assessment">
        <div className="error-container">
          <h2>⚠️ Error Loading Risk Data</h2>
          <p>{error}</p>
          <button className="retry-button" onClick={fetchRiskData}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="risk-assessment">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Summary Cards */}
        {stats && (
          <div className="risk-summary-grid">
            <div className="risk-summary-card critical">
              <div className="summary-content">
                <div className="summary-label">Critical Leases</div>
                <div className="summary-value">{stats.criticalLeases}</div>
                <div className="summary-sublabel">Expiring 0-90 days</div>
              </div>
            </div>
            <div className="risk-summary-card high">
              <div className="summary-content">
                <div className="summary-label">High Priority</div>
                <div className="summary-value">{stats.highPriority}</div>
                <div className="summary-sublabel">Expiring 91-180 days</div>
              </div>
            </div>
            <div className="risk-summary-card avg">
              <div className="summary-content">
                <div className="summary-label">Average Risk Score</div>
                <div className="summary-value">{stats.avgRisk.toFixed(1)}</div>
                <div className="summary-sublabel">Portfolio-wide</div>
              </div>
            </div>
            <div className="risk-summary-card revenue">
              <div className="summary-content">
                <div className="summary-label">Revenue at Risk</div>
                <div className="summary-value">${(stats.totalAtRisk / 1000000).toFixed(1)}M</div>
                <div className="summary-sublabel">Score &gt; 70</div>
              </div>
            </div>
          </div>
        )}

        {/* Risk Scoring Explanation */}
        <div className="risk-explanation">
          <h3 className="explanation-title">How Risk Scores Are Calculated</h3>
          <p className="explanation-intro">
            Each lease receives a Total Risk Score (0-100) based on four weighted components:
          </p>
          <div className="risk-factors-grid">
            <div className="risk-factor">
              <div className="factor-weight">40%</div>
              <div className="factor-content">
                <h4>Rollover Risk</h4>
                <p>Based on days until lease expiration. Critical leases expiring in 0-90 days score highest (100), while leases 2+ years out score lowest (10).</p>
              </div>
            </div>
            <div className="risk-factor">
              <div className="factor-weight">20%</div>
              <div className="factor-content">
                <h4>Escalation Risk</h4>
                <p>Measures if rent keeps pace with inflation. Low escalation rates (&lt;2%) score higher as they create future revenue pressure.</p>
              </div>
            </div>
            <div className="risk-factor">
              <div className="factor-weight">20%</div>
              <div className="factor-content">
                <h4>Industry Risk</h4>
                <p>Sector-based risk scores. Retail and Restaurant (80) have higher default risk than Healthcare and Government (20).</p>
              </div>
            </div>
            <div className="risk-factor">
              <div className="factor-weight">20%</div>
              <div className="factor-content">
                <h4>Concentration Risk</h4>
                <p>Portfolio exposure to individual leases. Larger tenants (&gt;10% of portfolio) score higher due to potential revenue impact.</p>
              </div>
            </div>
          </div>
          <div className="score-legend">
            <span className="legend-label">Risk Levels:</span>
            <div className="legend-items">
              <span className="legend-item critical">Critical (80-100)</span>
              <span className="legend-item high">High (60-79)</span>
              <span className="legend-item medium">Medium (40-59)</span>
              <span className="legend-item low">Low (20-39)</span>
              <span className="legend-item minimal">Minimal (0-19)</span>
            </div>
          </div>
        </div>

        {/* View Selector and Filter */}
        <div className="risk-controls">
          <div className="view-selector">
            <button 
              className={`view-btn ${selectedView === 'bubble' ? 'active' : ''}`}
              onClick={() => setSelectedView('bubble')}
            >
              Bubble Chart
            </button>
            <button 
              className={`view-btn ${selectedView === 'radar' ? 'active' : ''}`}
              onClick={() => setSelectedView('radar')}
            >
              Risk Components
            </button>
            <button 
              className={`view-btn ${selectedView === 'distribution' ? 'active' : ''}`}
              onClick={() => setSelectedView('distribution')}
            >
              Distribution
            </button>
            <button 
              className={`view-btn ${selectedView === 'sectors' ? 'active' : ''}`}
              onClick={() => setSelectedView('sectors')}
            >
              By Industry
            </button>
          </div>

          <div className="status-filter">
            <label>Filter by Status:</label>
            <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
              <option value="all">All Leases</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH_PRIORITY">High Priority</option>
              <option value="NEEDS_ATTENTION">Needs Attention</option>
              <option value="MONITOR">Monitor</option>
              <option value="STABLE">Stable</option>
              <option value="EXPIRED_RECENT">Recently Expired</option>
            </select>
          </div>
        </div>

        {/* Main Visualization Area */}
        <div className="visualization-container">
          {selectedView === 'bubble' && (
            <motion.div
              className="chart-section"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
            >
              <h3 className="chart-title">
                Risk vs. Time Matrix
                <span className="chart-subtitle">Bubble size = Annual rent value</span>
              </h3>
              <ResponsiveContainer width="100%" height={500}>
                <ScatterChart margin={{ top: 20, right: 20, bottom: 60, left: 60 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis 
                    type="number" 
                    dataKey="x" 
                    name="Days to Expiry"
                    label={{ value: 'Days Until Expiration', position: 'bottom', offset: 40 }}
                    stroke="#9ca3af"
                  />
                  <YAxis 
                    type="number" 
                    dataKey="y" 
                    name="Risk Score"
                    label={{ value: 'Total Risk Score', angle: -90, position: 'left', offset: 40 }}
                    stroke="#9ca3af"
                    domain={[0, 100]}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Scatter name="Leases" data={bubbleData} fill="#8b5cf6">
                    {bubbleData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={getRiskColor(entry.y)} />
                    ))}
                  </Scatter>
                </ScatterChart>
              </ResponsiveContainer>
              <div className="chart-legend">
                <div className="legend-item">
                  <span className="legend-color" style={{ background: '#ef4444' }}></span>
                  <span>Critical (80-100)</span>
                </div>
                <div className="legend-item">
                  <span className="legend-color" style={{ background: '#f97316' }}></span>
                  <span>High (60-79)</span>
                </div>
                <div className="legend-item">
                  <span className="legend-color" style={{ background: '#eab308' }}></span>
                  <span>Medium (40-59)</span>
                </div>
                <div className="legend-item">
                  <span className="legend-color" style={{ background: '#22c55e' }}></span>
                  <span>Low (20-39)</span>
                </div>
                <div className="legend-item">
                  <span className="legend-color" style={{ background: '#3b82f6' }}></span>
                  <span>Minimal (0-19)</span>
                </div>
              </div>
            </motion.div>
          )}

          {selectedView === 'radar' && (
            <motion.div
              className="chart-section"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
            >
              <h3 className="chart-title">
                Risk Component Breakdown
                <span className="chart-subtitle">Average scores across portfolio</span>
              </h3>
              <ResponsiveContainer width="100%" height={500}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="#374151" />
                  <PolarAngleAxis dataKey="risk" stroke="#9ca3af" />
                  <PolarRadiusAxis angle={90} domain={[0, 100]} stroke="#9ca3af" />
                  <Radar 
                    name="Risk Score" 
                    dataKey="score" 
                    stroke="#8b5cf6" 
                    fill="#8b5cf6" 
                    fillOpacity={0.6} 
                  />
                  <Tooltip />
                </RadarChart>
              </ResponsiveContainer>
              <div className="risk-component-details">
                {radarData.map((component, idx) => (
                  <div key={idx} className="component-detail">
                    <div className="component-name">{component.risk}</div>
                    <div className="component-bar">
                      <div 
                        className="component-bar-fill" 
                        style={{ 
                          width: `${component.score}%`,
                          background: getRiskColor(component.score)
                        }}
                      ></div>
                    </div>
                    <div className="component-score">{component.score.toFixed(1)}</div>
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          {selectedView === 'distribution' && (
            <motion.div
              className="chart-section"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
            >
              <h3 className="chart-title">
                Risk Distribution
                <span className="chart-subtitle">Lease count by risk category</span>
              </h3>
              <div className="distribution-charts">
                <ResponsiveContainer width="50%" height={400}>
                  <PieChart>
                    <Pie
                      data={riskDistribution}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percentage }) => `${name}: ${percentage}%`}
                      outerRadius={120}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {riskDistribution.map((entry, index) => {
                        const colors = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6'];
                        return <Cell key={`cell-${index}`} fill={colors[index]} />;
                      })}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
                <ResponsiveContainer width="50%" height={400}>
                  <BarChart data={riskDistribution}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="name" stroke="#9ca3af" angle={-15} textAnchor="end" height={100} />
                    <YAxis stroke="#9ca3af" />
                    <Tooltip />
                    <Bar dataKey="value" fill="#8b5cf6">
                      {riskDistribution.map((entry, index) => {
                        const colors = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6'];
                        return <Cell key={`cell-${index}`} fill={colors[index]} />;
                      })}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </motion.div>
          )}

          {selectedView === 'sectors' && (
            <motion.div
              className="chart-section"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
            >
              <h3 className="chart-title">
                Risk by Industry Sector
                <span className="chart-subtitle">Average risk scores and portfolio exposure</span>
              </h3>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={sectorRiskData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis type="number" stroke="#9ca3af" domain={[0, 100]} />
                  <YAxis dataKey="sector" type="category" stroke="#9ca3af" width={150} />
                  <Tooltip content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className="custom-tooltip">
                          <p><strong>{data.sector}</strong></p>
                          <p>Avg Risk: <strong>{data.avgRisk.toFixed(1)}</strong></p>
                          <p>Leases: <strong>{data.count}</strong></p>
                          <p>Total Rent: <strong>${data.totalRent.toLocaleString()}</strong></p>
                        </div>
                      );
                    }
                    return null;
                  }} />
                  <Bar dataKey="avgRisk" fill="#8b5cf6">
                    {sectorRiskData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={getRiskColor(entry.avgRisk)} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </motion.div>
          )}
        </div>

        {/* Top Risky Leases Table */}
        <div className="top-risk-section">
          <h3 className="section-title">Top 10 Highest Risk Leases</h3>
          <div className="risk-table-container">
            <table className="risk-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Tenant</th>
                  <th>Industry</th>
                  <th>Status</th>
                  <th>Days to Expiry</th>
                  <th>Annual Rent</th>
                  <th>Concentration</th>
                  <th>Risk Score</th>
                </tr>
              </thead>
              <tbody>
                {topRiskyLeases.map((lease, index) => (
                  <tr key={lease.lease_id}>
                    <td className="rank-cell">{index + 1}</td>
                    <td className="tenant-cell">{lease.tenant_name}</td>
                    <td>{lease.industry_sector || 'Unknown'}</td>
                    <td>
                      <span 
                        className="status-badge" 
                        style={{ background: getStatusColor(lease.lease_status) }}
                      >
                        {lease.lease_status.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className={lease.days_to_expiry < 90 ? 'critical-days' : ''}>
                      {lease.days_to_expiry} days
                    </td>
                    <td className="rent-cell">${lease.estimated_annual_rent.toLocaleString()}</td>
                    <td>{lease.portfolio_concentration_pct.toFixed(2)}%</td>
                    <td>
                      <div className="risk-score-cell">
                        <div className="risk-score-bar">
                          <div 
                            className="risk-score-fill"
                            style={{ 
                              width: `${lease.total_risk_score}%`,
                              background: getRiskColor(lease.total_risk_score)
                            }}
                          ></div>
                        </div>
                        <span className="risk-score-value">{lease.total_risk_score.toFixed(1)}</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Risk Insights */}
        <div className="risk-insights">
          <h3 className="section-title">Key Insights</h3>
          <div className="insights-grid">
            <div className="insight-card">
              <div className="insight-content">
                <h4>Immediate Action Required</h4>
                <p>
                  {stats?.criticalLeases} lease{stats?.criticalLeases !== 1 ? 's' : ''} expiring in the next 90 days
                  {stats?.criticalLeases > 0 && ' - prioritize renewal negotiations immediately.'}
                </p>
              </div>
            </div>
            <div className="insight-card">
              <div className="insight-content">
                <h4>Escalation Analysis</h4>
                <p>
                  Monitor leases with low escalation rates (&lt;2%) as they may not keep pace with inflation,
                  creating long-term revenue pressure.
                </p>
              </div>
            </div>
            <div className="insight-card">
              <div className="insight-content">
                <h4>Concentration Risk</h4>
                <p>
                  Large tenants (>5% of portfolio) represent significant rollover risk.
                  Consider diversification strategies and early renewal discussions.
                </p>
              </div>
            </div>
            <div className="insight-card">
              <div className="insight-content">
                <h4>Sector Exposure</h4>
                <p>
                  Review industry-specific risks across your portfolio.
                  Retail and restaurant sectors typically carry higher rollover risk.
                </p>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default RiskAssessment;

